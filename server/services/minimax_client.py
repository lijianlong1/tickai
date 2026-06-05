"""
MiniMax 客户端

MiniMax（MiniMax AI）模型客户端，基于 OpenAI 格式调用。
支持 MiniMax 的图像生成、文本生成等模型。

官方文档参考：MiniMax 提供的 OpenAI 兼容 API 端点

注意：此文件中的"minimax"为用户的具体模型名称占位符，
实际部署时需要替换为真实的模型 API 端点和密钥。
"""
import os
import logging
import httpx
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from services.llm_client import LLMClient, ImageGenResponse, ImageGenRequest, TextCompletionResponse

logger = logging.getLogger(__name__)


# ============ MiniMax 特定配置 ============

# MiniMax API 默认端点（OpenAI 兼容）
DEFAULT_MINIMAX_BASE_URL = "https://api.minimax.chat/v1"

# 支持的模型（请根据实际 MiniMax API 调整）
MINIMAX_MODELS = {
    # 图像模型
    "minimax-image-01": {
        "type": "image",
        "name": "MiniMax Image 01",
        "description": "高质量图像生成模型",
        "sizes": ["1024x1024", "768x1344", "1344x768", "512x512"],
    },
    # 文本模型
    "minimax-text-01": {
        "type": "text",
        "name": "MiniMax Text 01",
        "description": "通用文本生成模型",
    },
    "abab-6.5-chat": {
        "type": "text",
        "name": "abab-6.5-chat",
        "description": "MiniMax abab 系列对话模型",
    },
    # 视觉理解模型
    "minimax-vl-01": {
        "type": "vision",
        "name": "MiniMax VL 01",
        "description": "视觉理解模型",
    },
}


# ============ MiniMax 客户端 ============

class MiniMaxClient:
    """
    MiniMax 模型客户端

    通过 OpenAI 兼容格式调用 MiniMax 模型：
    - 文本生成（chat/completions）
    - 图像生成（images/generations）
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 180.0,
    ):
        """
        初始化 MiniMax 客户端

        Args:
            api_key: API Key（默认从 MINIMAX_API_KEY 环境变量读取）
            base_url: API 端点（默认 https://api.minimax.chat/v1）
            timeout: 请求超时
        """
        self.api_key = api_key or os.getenv("MINIMAX_API_KEY", "")
        self.base_url = base_url or os.getenv("MINIMAX_BASE_URL", DEFAULT_MINIMAX_BASE_URL)
        self.timeout = timeout

        if not self.api_key:
            logger.warning("MINIMAX_API_KEY 未设置，MiniMax 调用将失败")

        # 复用 LLMClient 提供的底层调用能力
        self._llm = LLMClient(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout,
        )

        logger.info(f"MiniMax 客户端初始化: base_url={self.base_url}")

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: str = "minimax-text-01",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> TextCompletionResponse:
        """
        文本对话

        Args:
            messages: 消息列表
            model: MiniMax 文本模型名称
            temperature: 温度参数
            max_tokens: 最大 token 数

        Returns:
            文本响应
        """
        return await self._llm.chat(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )

    async def generate_image(
        self,
        prompt: str,
        model: str = "minimax-image-01",
        n: int = 1,
        size: str = "1024x1024",
        **kwargs
    ) -> ImageGenResponse:
        """
        图像生成

        Args:
            prompt: 图像描述
            model: MiniMax 图像模型名称
            n: 生成数量
            size: 图像尺寸

        Returns:
            图像生成结果
        """
        return await self._llm.generate_image(
            prompt=prompt,
            model=model,
            n=n,
            size=size,
            # MiniMax 不支持 dall-e 特有的 quality/style 参数
            quality="standard",
            style="vivid",
            response_format="url",
            **kwargs,
        )

    async def analyze_image(
        self,
        image_url: str,
        prompt: str = "请描述这张图片",
        model: str = "minimax-vl-01",
    ) -> str:
        """
        图像理解（视觉模型）

        Args:
            image_url: 图像 URL
            prompt: 提示词
            model: 视觉模型

        Returns:
            理解结果文本
        """
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            }
        ]

        response = await self._llm.chat(
            messages=messages,
            model=model,
            temperature=0.5,
        )
        return response.content

    async def health_check(self) -> bool:
        """
        健康检查

        Returns:
            是否可用
        """
        if not self.api_key:
            return False

        try:
            # 用最小的请求测试连通性
            response = await self._llm.chat(
                messages=[{"role": "user", "content": "hi"}],
                model="minimax-text-01",
                max_tokens=5,
            )
            return bool(response.content)
        except Exception as e:
            logger.error(f"MiniMax 健康检查失败: {e}")
            return False

    @staticmethod
    def list_supported_models(model_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        列出支持的模型

        Args:
            model_type: 模型类型过滤（text/image/vision）

        Returns:
            模型信息列表
        """
        result = []
        for model_id, info in MINIMAX_MODELS.items():
            if model_type and info["type"] != model_type:
                continue
            result.append({
                "id": model_id,
                **info,
            })
        return result


# ============ 单例 ============

_minimax_instance: Optional[MiniMaxClient] = None


def get_minimax_client() -> MiniMaxClient:
    """获取 MiniMax 客户端单例"""
    global _minimax_instance
    if _minimax_instance is None:
        _minimax_instance = MiniMaxClient()
    return _minimax_instance
