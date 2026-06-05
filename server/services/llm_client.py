"""
LLM 客户端 - 基于 OpenAI 格式调用多种模型

主要功能：
- 文本生成（chat completions）
- 图像生成（DALL-E 3 等）
- 支持自定义 base_url（用于 MiniMax 等兼容 OpenAI 格式的模型）
"""
import os
import json
import base64
import logging
import httpx
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ============ Pydantic Models ============

class TextMessage(BaseModel):
    """聊天消息"""
    role: str = Field(..., description="角色：system/user/assistant")
    content: str = Field(..., description="消息内容")


class TextCompletionRequest(BaseModel):
    """文本补全请求"""
    messages: List[TextMessage]
    model: str = Field(default="gpt-3.5-turbo")
    temperature: float = Field(default=0.7, ge=0, le=2)
    max_tokens: Optional[int] = Field(default=None, ge=1, le=8192)
    top_p: float = Field(default=1.0, ge=0, le=1)
    response_format: Optional[Dict[str, str]] = None  # {"type": "json_object"}


class TextCompletionResponse(BaseModel):
    """文本补全响应"""
    content: str
    model: str
    usage: Optional[Dict[str, int]] = None
    finish_reason: Optional[str] = None


class ImageGenRequest(BaseModel):
    """图像生成请求"""
    prompt: str = Field(..., min_length=1, max_length=4000)
    model: str = Field(default="dall-e-3")
    n: int = Field(default=1, ge=1, le=4)
    size: str = Field(default="1024x1024", description="1024x1024, 1792x1024, 1024x1792")
    quality: str = Field(default="standard", description="standard/hd")
    style: str = Field(default="vivid", description="vivid/natural")
    response_format: str = Field(default="url", description="url/b64_json")


class ImageGenResponse(BaseModel):
    """图像生成响应"""
    urls: List[str] = Field(default_factory=list)
    b64_json: List[str] = Field(default_factory=list)
    revised_prompt: Optional[str] = None
    model: str = ""


# ============ LLM 客户端 ============

class LLMClient:
    """
    LLM 客户端

    基于 OpenAI Python SDK，但支持自定义 base_url，
    可以无缝对接任何兼容 OpenAI 格式的模型（如 MiniMax、通义千问等）。
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 120.0,
    ):
        """
        初始化 LLM 客户端

        Args:
            api_key: API 密钥（默认从环境变量读取）
            base_url: API 基础 URL（默认使用 OpenAI 官方）
            timeout: 请求超时（秒）
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.timeout = timeout

        # 尝试加载 openai SDK
        try:
            from openai import AsyncOpenAI
            self.AsyncOpenAI = AsyncOpenAI
            self._use_sdk = True
        except ImportError:
            logger.warning("openai SDK 未安装，将使用 httpx 实现")
            self._use_sdk = False

        logger.info(f"LLMClient 初始化: base_url={self.base_url}, use_sdk={self._use_sdk}")

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> TextCompletionResponse:
        """
        文本生成（chat completions）

        Args:
            messages: 消息列表 [{"role": "user", "content": "..."}]
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大 token 数
            response_format: 响应格式（如 {"type": "json_object"}）
            **kwargs: 其他参数

        Returns:
            补全结果
        """
        if self._use_sdk and self.api_key:
            return await self._chat_with_sdk(
                messages, model, temperature, max_tokens, response_format, **kwargs
            )
        else:
            return await self._chat_with_httpx(
                messages, model, temperature, max_tokens, response_format, **kwargs
            )

    async def _chat_with_sdk(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: Optional[int],
        response_format: Optional[Dict[str, str]],
        **kwargs
    ) -> TextCompletionResponse:
        """使用 OpenAI SDK 调用"""
        client = self.AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout,
        )

        params = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens is not None:
            params["max_tokens"] = max_tokens
        if response_format is not None:
            params["response_format"] = response_format
        params.update(kwargs)

        response = await client.chat.completions.create(**params)

        return TextCompletionResponse(
            content=response.choices[0].message.content or "",
            model=response.model,
            usage=response.usage.dict() if response.usage else None,
            finish_reason=response.choices[0].finish_reason,
        )

    async def _chat_with_httpx(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: Optional[int],
        response_format: Optional[Dict[str, str]],
        **kwargs
    ) -> TextCompletionResponse:
        """使用 httpx 调用（兼容 OpenAI 格式）"""
        url = f"{self.base_url.rstrip('/')}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if response_format is not None:
            payload["response_format"] = response_format
        payload.update(kwargs)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        choice = data["choices"][0]
        return TextCompletionResponse(
            content=choice["message"]["content"] or "",
            model=data.get("model", model),
            usage=data.get("usage"),
            finish_reason=choice.get("finish_reason"),
        )

    async def generate_image(
        self,
        prompt: str,
        model: str = "dall-e-3",
        n: int = 1,
        size: str = "1024x1024",
        quality: str = "standard",
        style: str = "vivid",
        response_format: str = "url",
        **kwargs
    ) -> ImageGenResponse:
        """
        图像生成

        Args:
            prompt: 图像描述
            model: 模型名称
            n: 生成数量
            size: 图像尺寸
            quality: 质量（standard/hd）
            style: 风格（vivid/natural）
            response_format: 响应格式（url/b64_json）

        Returns:
            图像生成结果
        """
        if self._use_sdk and self.api_key:
            return await self._image_with_sdk(
                prompt, model, n, size, quality, style, response_format, **kwargs
            )
        else:
            return await self._image_with_httpx(
                prompt, model, n, size, quality, style, response_format, **kwargs
            )

    async def _image_with_sdk(
        self,
        prompt: str,
        model: str,
        n: int,
        size: str,
        quality: str,
        style: str,
        response_format: str,
        **kwargs
    ) -> ImageGenResponse:
        """使用 OpenAI SDK 生成图像"""
        client = self.AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout,
        )

        params = {
            "model": model,
            "prompt": prompt,
            "n": n,
            "size": size,
            "response_format": response_format,
        }
        # dall-e-3 支持 quality 和 style
        if "dall-e" in model.lower():
            params["quality"] = quality
            params["style"] = style
        params.update(kwargs)

        response = await client.images.generate(**params)

        urls = []
        b64_list = []
        for img in response.data:
            if img.url:
                urls.append(img.url)
            if img.b64_json:
                b64_list.append(img.b64_json)

        return ImageGenResponse(
            urls=urls,
            b64_json=b64_list,
            revised_prompt=response.data[0].revised_prompt if hasattr(response.data[0], 'revised_prompt') else None,
            model=response.model if hasattr(response, 'model') else model,
        )

    async def _image_with_httpx(
        self,
        prompt: str,
        model: str,
        n: int,
        size: str,
        quality: str,
        style: str,
        response_format: str,
        **kwargs
    ) -> ImageGenResponse:
        """使用 httpx 生成图像"""
        url = f"{self.base_url.rstrip('/')}/images/generations"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        payload = {
            "model": model,
            "prompt": prompt,
            "n": n,
            "size": size,
            "response_format": response_format,
        }
        if "dall-e" in model.lower():
            payload["quality"] = quality
            payload["style"] = style
        payload.update(kwargs)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        urls = [img["url"] for img in data.get("data", []) if img.get("url")]
        b64_list = [img["b64_json"] for img in data.get("data", []) if img.get("b64_json")]

        return ImageGenResponse(
            urls=urls,
            b64_json=b64_list,
            revised_prompt=data.get("data", [{}])[0].get("revised_prompt"),
            model=data.get("model", model),
        )

    async def download_image_to_file(self, url: str, save_path: str) -> str:
        """
        下载图像到本地文件

        Args:
            url: 图像 URL（可能是 OpenAI 返回的临时 URL）
            save_path: 保存路径

        Returns:
            保存的文件路径
        """
        os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            with open(save_path, "wb") as f:
                f.write(response.content)

        return save_path

    def save_base64_image(self, b64_str: str, save_path: str) -> str:
        """
        保存 base64 编码的图像

        Args:
            b64_str: base64 字符串
            save_path: 保存路径

        Returns:
            保存的文件路径
        """
        os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)

        # 处理可能包含的 data:image/png;base64, 前缀
        if "," in b64_str:
            b64_str = b64_str.split(",", 1)[1]

        image_data = base64.b64decode(b64_str)
        with open(save_path, "wb") as f:
            f.write(image_data)

        return save_path


# ============ 工厂函数 ============

def create_llm_client_from_config(
    provider: str,
    model: str,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
) -> LLMClient:
    """
    根据 provider + model 创建 LLM 客户端

    Args:
        provider: 提供商（openai / qwen / zhipu / minimax / volcengine）
        model: 模型名称
        api_key: API Key（None 时从环境变量读取）
        base_url: 自定义 base_url

    Returns:
        LLMClient 实例
    """
    # 各 provider 默认 base_url
    DEFAULT_BASE_URLS = {
        "openai": "https://api.openai.com/v1",
        "qwen": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "zhipu": "https://open.bigmodel.cn/api/paas/v4",
        "minimax": "https://api.minimax.chat/v1",  # MiniMax OpenAI 兼容端点
        "volcengine": "https://ark.cn-beijing.volces.com/api/v3",
        "doubao": "https://ark.cn-beijing.volces.com/api/v3",
    }

    # 各 provider 默认 API Key 环境变量
    DEFAULT_API_KEY_ENVS = {
        "openai": "OPENAI_API_KEY",
        "qwen": "DASHSCOPE_API_KEY",
        "zhipu": "ZHIPU_API_KEY",
        "minimax": "MINIMAX_API_KEY",
        "volcengine": "VOLCENGINE_API_KEY",
        "doubao": "DOUBAO_API_KEY",
    }

    # 确定 base_url
    if not base_url:
        base_url = os.getenv(f"{provider.upper()}_BASE_URL", DEFAULT_BASE_URLS.get(provider, ""))

    # 确定 api_key
    if not api_key:
        env_var = DEFAULT_API_KEY_ENVS.get(provider, "")
        api_key = os.getenv(env_var, "")

    return LLMClient(
        api_key=api_key,
        base_url=base_url,
    )


# ============ 预置配置 ============

# 常用的 MiniMax 图像模型
MINIMAX_IMAGE_MODELS = {
    "minimax-image-01": {
        "name": "MiniMax Image 01",
        "description": "MiniMax 图像生成模型",
        "sizes": ["1024x1024", "768x1344", "1344x768"],
        "type": "image",
    },
}

# 常用的 MiniMax 文本模型
MINIMAX_TEXT_MODELS = {
    "minimax-text-01": {
        "name": "MiniMax Text 01",
        "description": "MiniMax 文本生成模型",
        "type": "text",
    },
    "minimax-abab-6.5": {
        "name": "abab-6.5",
        "description": "MiniMax abab 系列模型",
        "type": "text",
    },
}

# 所有支持的 provider 配置
PROVIDER_CONFIGS = {
    "minimax": {
        "name": "MiniMax",
        "default_base_url": "https://api.minimax.chat/v1",
        "api_key_env": "MINIMAX_API_KEY",
        "text_models": list(MINIMAX_TEXT_MODELS.keys()),
        "image_models": list(MINIMAX_IMAGE_MODELS.keys()),
        "voice_models": [],
    },
    "openai": {
        "name": "OpenAI",
        "default_base_url": "https://api.openai.com/v1",
        "api_key_env": "OPENAI_API_KEY",
        "text_models": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", "gpt-4o"],
        "image_models": ["dall-e-3", "dall-e-2"],
        "voice_models": ["tts-1", "tts-1-hd"],
    },
    "qwen": {
        "name": "通义千问",
        "default_base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "api_key_env": "DASHSCOPE_API_KEY",
        "text_models": ["qwen-turbo", "qwen-plus", "qwen-max", "qwen-vl-plus"],
        "image_models": ["wanx-v1"],
        "voice_models": ["sambert"],
    },
}


def list_models_for_provider(provider: str, model_type: str = None) -> List[str]:
    """
    列出某 provider 支持的模型

    Args:
        provider: 提供商
        model_type: 模型类型（text/image/voice），None 表示所有

    Returns:
        模型名称列表
    """
    config = PROVIDER_CONFIGS.get(provider, {})
    if not config:
        return []

    if model_type:
        key = f"{model_type}_models"
        return config.get(key, [])

    all_models = []
    all_models.extend(config.get("text_models", []))
    all_models.extend(config.get("image_models", []))
    all_models.extend(config.get("voice_models", []))
    return all_models
