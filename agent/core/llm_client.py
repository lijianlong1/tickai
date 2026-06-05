"""
LLM 统一客户端
支持 OpenAI / 阿里云 DashScope / 智谱 GLM 等多模型接入
"""
import json
from typing import List, Dict, Any, Optional, AsyncGenerator
from abc import ABC, abstractmethod
import httpx

from .config_loader import config


class BaseLLMProvider(ABC):
    """LLM 提供方基类"""

    def __init__(self, provider_config: Dict[str, Any]):
        self.api_key = provider_config.get("api_key", "")
        self.base_url = provider_config.get("base_url", "").rstrip("/")
        self.model = provider_config.get("model", "")
        self.temperature = provider_config.get("temperature", 0.7)
        self.max_tokens = provider_config.get("max_tokens", 4096)

    @abstractmethod
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """对话接口"""
        pass

    @abstractmethod
    async def stream_chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """流式对话"""
        pass


class OpenAIProvider(BaseLLMProvider):
    """OpenAI 兼容协议实现（兼容通义、智谱、DeepSeek 等）"""

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature or self.temperature,
            "max_tokens": max_tokens or self.max_tokens,
            **kwargs,
        }

        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    async def stream_chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature or self.temperature,
            "stream": True,
            **kwargs,
        }

        async with httpx.AsyncClient(timeout=60) as client:
            async with client.stream("POST", url, headers=headers, json=payload) as resp:
                async for line in resp.aiter_lines():
                    if line.startswith("data: "):
                        chunk = line[6:].strip()
                        if chunk == "[DONE]":
                            break
                        try:
                            data = json.loads(chunk)
                            delta = data["choices"][0].get("delta", {}).get("content", "")
                            if delta:
                                yield delta
                        except (json.JSONDecodeError, KeyError):
                            continue


class LLMClient:
    """LLM 客户端（统一调度）"""

    _providers: Dict[str, BaseLLMProvider] = {}

    @classmethod
    def get_provider(cls, name: str = None) -> BaseLLMProvider:
        """获取 LLM 客户端"""
        if name is None:
            name = config.get("llm.default_provider", "openai")

        if name not in cls._providers:
            provider_config = config.get(f"llm.providers.{name}")
            if not provider_config:
                raise ValueError(f"未配置 LLM 提供方: {name}")

            # 目前都使用 OpenAI 兼容协议
            cls._providers[name] = OpenAIProvider(provider_config)

        return cls._providers[name]

    @classmethod
    async def chat(
        cls,
        messages: List[Dict[str, str]],
        provider: str = None,
        **kwargs
    ) -> str:
        """对话"""
        client = cls.get_provider(provider)
        return await client.chat(messages, **kwargs)

    @classmethod
    async def stream_chat(
        cls,
        messages: List[Dict[str, str]],
        provider: str = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """流式对话"""
        client = cls.get_provider(provider)
        async for chunk in client.stream_chat(messages, **kwargs):
            yield chunk
