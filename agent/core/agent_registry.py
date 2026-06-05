"""
Agent 注册中心
统一管理所有 Agent 实例
"""
import logging
from typing import Dict, List, Type
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class AgentRegistry:
    """Agent 注册中心（单例）"""

    _instance = None
    _registry: Dict[str, BaseAgent] = {}
    _agent_classes: Dict[str, Type[BaseAgent]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def register_class(self, agent_id: str, cls_obj: Type[BaseAgent]):
        """注册 Agent 类"""
        self._agent_classes[agent_id] = cls_obj
        logger.info(f"注册 Agent 类: {agent_id}")

    def create(self, agent_id: str, *args, **kwargs) -> BaseAgent:
        """创建 Agent 实例"""
        if agent_id in self._registry:
            return self._registry[agent_id]

        if agent_id not in self._agent_classes:
            raise ValueError(f"未注册的 Agent: {agent_id}")

        agent = self._agent_classes[agent_id](agent_id=agent_id, *args, **kwargs)
        self._registry[agent_id] = agent
        logger.info(f"创建 Agent 实例: {agent_id}")
        return agent

    def get(self, agent_id: str) -> BaseAgent:
        """获取 Agent 实例"""
        if agent_id not in self._registry:
            return self.create(agent_id)
        return self._registry[agent_id]

    def list_agents(self) -> List[Dict]:
        """列出所有 Agent"""
        return [agent.to_dict() for agent in self._registry.values()]

    def list_classes(self) -> List[str]:
        """列出所有可创建的 Agent 类"""
        return list(self._agent_classes.keys())


# 全局注册中心
registry = AgentRegistry()
