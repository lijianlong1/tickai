"""
Agent 基类
所有智能体都继承该类，统一管理 prompt、工具、记忆、状态
"""
import json
import uuid
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from .config_loader import config
from .llm_client import LLMClient


class BaseAgent(ABC):
    """Agent 基类"""

    def __init__(self, agent_id: str = None, name: str = None):
        # 元数据
        self.agent_id = agent_id or self.__class__.__name__
        self.name = name or self.agent_id
        self.description = ""
        self.llm_provider = config.get("llm.default_provider", "openai")

        # 提示词
        self.system_prompt = ""

        # 工具注册表
        self.tools: Dict[str, Any] = {}

        # 记忆
        self.memory: List[Dict[str, str]] = []

        # 状态
        self.created_at = datetime.now().isoformat()
        self.last_active_at = self.created_at

    def load_system_prompt(self, file_path: str = None):
        """从文件加载系统提示词"""
        if file_path is None:
            file_path = Path(__file__).parent.parent / "prompts" / f"{self.agent_id}.txt"

        if Path(file_path).exists():
            with open(file_path, "r", encoding="utf-8") as f:
                self.system_prompt = f.read().strip()
        else:
            self.system_prompt = f"你是 {self.name}。"

    def register_tool(self, name: str, func, description: str = "", schema: Dict = None):
        """注册工具"""
        self.tools[name] = {
            "func": func,
            "description": description,
            "schema": schema or {},
        }

    def add_memory(self, role: str, content: str):
        """添加记忆"""
        self.memory.append({"role": role, "content": content})
        self.last_active_at = datetime.now().isoformat()

        # 限制记忆长度
        if len(self.memory) > 20:
            self.memory = self.memory[-20:]

    def clear_memory(self):
        """清空记忆"""
        self.memory = []

    def build_messages(self, user_input: str) -> List[Dict[str, str]]:
        """构建消息列表"""
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.memory)
        messages.append({"role": "user", "content": user_input})
        return messages

    async def run(self, user_input: str, **kwargs) -> str:
        """运行 Agent（单轮对话）"""
        self.add_memory("user", user_input)
        messages = self.build_messages(user_input)

        try:
            response = await LLMClient.chat(
                messages,
                provider=self.llm_provider,
                **kwargs
            )
            self.add_memory("assistant", response)
            return response
        except Exception as e:
            return f"[Agent 错误] {self.name} 处理失败: {str(e)}"

    async def stream_run(self, user_input: str, **kwargs):
        """流式运行"""
        self.add_memory("user", user_input)
        messages = self.build_messages(user_input)

        full_response = ""
        async for chunk in LLMClient.stream_chat(
            messages,
            provider=self.llm_provider,
            **kwargs
        ):
            full_response += chunk
            yield chunk

        self.add_memory("assistant", full_response)

    def to_dict(self) -> Dict[str, Any]:
        """序列化 Agent 状态"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "description": self.description,
            "llm_provider": self.llm_provider,
            "system_prompt": self.system_prompt,
            "tools": list(self.tools.keys()),
            "memory_count": len(self.memory),
            "created_at": self.created_at,
            "last_active_at": self.last_active_at,
        }
