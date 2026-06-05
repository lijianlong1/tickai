"""
模型适配器层

为上层业务（视频生成、文本生成等）提供统一的模型调用接口。
支持多种 provider：MiniMax、OpenAI、通义千问、智谱等。
所有 provider 都使用 OpenAI 兼容格式调用。

使用方式：
    adapter = ModelAdapter.from_config({
        "provider": "minimax",
        "model": "minimax-image-01",
        "api_key": "...",
        "base_url": "..."  # 可选
    })
    
    result = await adapter.generate_image(prompt="...")
"""
import os
import logging
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

from services.llm_client import LLMClient, TextCompletionResponse, ImageGenResponse
from services.minimax_client import MiniMaxClient

logger = logging.getLogger(__name__)


# ============ 配置模型 ============

class ModelConfig(BaseModel):
    """模型配置"""
    provider: str = Field(..., description="提供商")
    model: str = Field(..., description="模型名称")
    api_key: Optional[str] = Field(default=None, description="API Key")
    base_url: Optional[str] = Field(default=None, description="自定义端点")
    extra_params: Optional[Dict[str, Any]] = Field(default_factory=dict, description="额外参数")


class GenerationRequest(BaseModel):
    """生成请求"""
    prompt: str
    system_prompt: Optional[str] = None
    model: str = "default"
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    response_format: Optional[Dict[str, str]] = None


class ImageRequest(BaseModel):
    """图像生成请求"""
    prompt: str
    negative_prompt: Optional[str] = None
    model: Optional[str] = None
    size: str = "1024x1024"
    n: int = 1


# ============ 适配器 ============

class ModelAdapter:
    """
    模型适配器

    统一的模型调用接口，支持多种 provider。
    实现 openai / minimax / qwen / zhipu 等。
    """

    def __init__(self, config: ModelConfig):
        """
        初始化适配器

        Args:
            config: 模型配置
        """
        self.config = config
        self.provider = config.provider.lower()
        self.model = config.model
        self.api_key = config.api_key
        self.base_url = config.base_url

        # 根据 provider 选择底层客户端
        if self.provider == "minimax":
            self._client = MiniMaxClient(
                api_key=self.api_key,
                base_url=self.base_url,
            )
        else:
            # 其他 provider 使用通用 LLMClient
            self._client = LLMClient(
                api_key=self.api_key,
                base_url=self.base_url,
            )

        logger.info(f"ModelAdapter 创建: provider={self.provider}, model={self.model}")

    # ============ 工厂方法 ============

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "ModelAdapter":
        """
        从字典创建适配器

        Args:
            config: 包含 provider, model, api_key, base_url 的字典

        Returns:
            ModelAdapter 实例
        """
        model_config = ModelConfig(**config)
        return cls(model_config)

    @classmethod
    def from_env(cls, provider: str, model: str) -> "ModelAdapter":
        """
        从环境变量创建适配器

        Args:
            provider: 提供商
            model: 模型名称

        Returns:
            ModelAdapter 实例
        """
        # 从环境变量读取
        env_var_map = {
            "openai": "OPENAI_API_KEY",
            "minimax": "MINIMAX_API_KEY",
            "qwen": "DASHSCOPE_API_KEY",
            "zhipu": "ZHIPU_API_KEY",
            "volcengine": "VOLCENGINE_API_KEY",
        }

        api_key = os.getenv(env_var_map.get(provider.lower(), ""))
        base_url = os.getenv(f"{provider.upper()}_BASE_URL", "")

        return cls(ModelConfig(
            provider=provider,
            model=model,
            api_key=api_key,
            base_url=base_url,
        ))

    @classmethod
    def from_db_config(cls, model_config_db) -> "ModelAdapter":
        """
        从数据库 ModelConfig 对象创建适配器

        Args:
            model_config_db: models.model_config.ModelConfig 实例

        Returns:
            ModelAdapter 实例
        """
        from utils.crypto import decrypt_api_key

        # 解密 API Key
        api_key = None
        if model_config_db.api_key_encrypted:
            try:
                api_key = decrypt_api_key(model_config_db.api_key_encrypted)
            except Exception as e:
                logger.warning(f"解密 API Key 失败: {e}")

        return cls(ModelConfig(
            provider=model_config_db.provider,
            model=model_config_db.model_name,
            api_key=api_key,
            base_url=model_config_db.base_url,
        ))

    # ============ 文本生成 ============

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        文本生成

        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            temperature: 温度
            max_tokens: 最大 token
            response_format: 响应格式

        Returns:
            生成的文本
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await self._client.chat(
            messages=messages,
            model=self.model,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=response_format,
        )
        return response.content

    async def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        生成 JSON 格式响应

        Args:
            prompt: 提示词
            system_prompt: 系统提示词
            **kwargs: 其他参数

        Returns:
            解析后的 JSON 字典
        """
        import json

        if not system_prompt:
            system_prompt = "你是一个 JSON 输出助手，总是返回严格的 JSON 格式。"

        response = await self.generate_text(
            prompt=prompt,
            system_prompt=system_prompt,
            response_format={"type": "json_object"},
            **kwargs,
        )

        # 尝试解析 JSON
        try:
            # 移除 markdown 代码块标记
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            return json.loads(response.strip())
        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析失败: {e}, response: {response}")
            raise ValueError(f"模型返回的不是有效 JSON: {e}")

    # ============ 图像生成 ============

    async def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        n: int = 1,
        **kwargs
    ) -> ImageGenResponse:
        """
        图像生成

        Args:
            prompt: 图像描述
            size: 尺寸
            n: 数量
            **kwargs: 其他参数

        Returns:
            图像生成结果
        """
        return await self._client.generate_image(
            prompt=prompt,
            model=self.model,
            n=n,
            size=size,
            **kwargs,
        )

    # ============ 视觉理解 ============

    async def analyze_image(
        self,
        image_url: str,
        prompt: str = "请描述这张图片",
    ) -> str:
        """
        图像理解

        Args:
            image_url: 图像 URL
            prompt: 提示词

        Returns:
            理解结果
        """
        if hasattr(self._client, "analyze_image"):
            return await self._client.analyze_image(
                image_url=image_url,
                prompt=prompt,
                model=self.model,
            )
        else:
            # 通用实现
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ],
                }
            ]
            response = await self._client.chat(
                messages=messages,
                model=self.model,
            )
            return response.content

    # ============ 工具方法 ============

    async def health_check(self) -> bool:
        """健康检查"""
        if hasattr(self._client, "health_check"):
            return await self._client.health_check()

        try:
            response = await self._client.chat(
                messages=[{"role": "user", "content": "test"}],
                model=self.model,
                max_tokens=5,
            )
            return bool(response.content)
        except Exception as e:
            logger.error(f"健康检查失败: {e}")
            return False


# ============ 便捷函数 ============

async def quick_chat(
    prompt: str,
    provider: str = "minimax",
    model: str = "minimax-text-01",
    system_prompt: Optional[str] = None,
    **kwargs
) -> str:
    """
    快速调用文本生成（使用环境变量中的 API Key）

    Args:
        prompt: 提示词
        provider: 提供商
        model: 模型名称
        system_prompt: 系统提示词
        **kwargs: 其他参数

    Returns:
        生成的文本
    """
    adapter = ModelAdapter.from_env(provider, model)
    return await adapter.generate_text(
        prompt=prompt,
        system_prompt=system_prompt,
        **kwargs,
    )


async def quick_image(
    prompt: str,
    provider: str = "minimax",
    model: str = "minimax-image-01",
    size: str = "1024x1024",
    **kwargs
) -> ImageGenResponse:
    """
    快速调用图像生成

    Args:
        prompt: 图像描述
        provider: 提供商
        model: 模型名称
        size: 图像尺寸

    Returns:
        图像生成结果
    """
    adapter = ModelAdapter.from_env(provider, model)
    return await adapter.generate_image(
        prompt=prompt,
        size=size,
        **kwargs,
    )
