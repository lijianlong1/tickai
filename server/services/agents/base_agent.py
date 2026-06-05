"""
智能体基类

定义所有智能体的通用接口和状态管理。
"""
import asyncio
import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class AgentStatus(str, Enum):
    """智能体状态"""
    PENDING = "pending"      # 等待执行
    RUNNING = "running"      # 执行中
    SUCCESS = "success"      # 成功
    FAILED = "failed"        # 失败
    SKIPPED = "skipped"      # 跳过（被重做覆盖）
    PAUSED = "paused"        # 暂停


class PanelData(BaseModel):
    """单个镜头数据"""
    index: int
    scene: str = ""
    camera: str = "中景"
    characters: list = []
    subject_image_url: Optional[str] = None
    background_image_url: Optional[str] = None
    subject_prompt: str = ""
    background_prompt: str = ""
    narration: str = ""
    vision_description: str = ""
    audio_url: Optional[str] = None
    audio_duration: float = 0.0
    duration: float = 5.0
    subtitle_position: str = "bottom_center"
    subtitle_style: Optional[Dict[str, Any]] = None


class WorkflowConfig(BaseModel):
    """工作流配置"""
    user_id: int
    workflow_id: int
    title: str
    original_prompt: str
    panel_count: int = 6
    ratio: str = "16:9"
    target_duration: int = 30
    character_ids: list = []
    model_config: Dict[str, Any] = {}
    subtitle_config: Optional[Dict[str, Any]] = None


class WorkflowContext(BaseModel):
    """工作流上下文（智能体间共享的数据）"""
    config: WorkflowConfig
    panels: list = Field(default_factory=list)  # List[PanelData]
    characters: list = Field(default_factory=list)  # List[Character]

    # 全局进度
    overall_progress: int = 0
    current_step: str = ""

    class Config:
        arbitrary_types_allowed = True


class AgentState(BaseModel):
    """智能体状态"""
    agent_name: str
    status: AgentStatus = AgentStatus.PENDING
    progress: int = 0
    message: str = ""
    error: Optional[str] = None
    started_at: Optional[str] = None
    finished_at: Optional[str] = None


class BaseAgent(ABC):
    """
    智能体基类

    所有智能体都需要继承此类并实现 `run` 方法。
    """

    # 智能体名称（子类必须重写）
    name: str = "base"
    # 显示名称（中文）
    display_name: str = "基础智能体"
    # 智能体描述
    description: str = ""
    # 智能体图标（emoji）
    icon: str = "🤖"
    # 主题色（hex）
    color: str = "#6366F1"

    def __init__(self):
        self.state = AgentState(agent_name=self.name)
        self._retry_count = 0
        self._max_retries = 3
        logger.info(f"智能体 {self.display_name} 已初始化")

    @abstractmethod
    async def run(self, context: WorkflowContext) -> WorkflowContext:
        """
        执行智能体任务

        Args:
            context: 工作流上下文

        Returns:
            更新后的上下文
        """
        ...

    def get_progress(self) -> int:
        """获取当前进度（0-100）"""
        return self.state.progress

    def get_status_message(self) -> str:
        """获取状态描述"""
        return self.state.message or "等待中"

    def update_progress(self, progress: int, message: str = "") -> None:
        """更新进度"""
        self.state.progress = max(0, min(100, progress))
        if message:
            self.state.message = message
        logger.debug(f"[{self.name}] 进度: {progress}% - {message}")

    async def run_with_retry(self, context: WorkflowContext) -> WorkflowContext:
        """
        带重试的执行

        如果失败会自动重试，最多重试 3 次。
        """
        self.state.status = AgentStatus.RUNNING
        self.state.error = None

        last_error = None
        for attempt in range(self._max_retries + 1):
            try:
                self._retry_count = attempt
                if attempt > 0:
                    self.update_progress(0, f"重试中 ({attempt}/{self._max_retries})...")

                result = await self.run(context)
                self.state.status = AgentStatus.SUCCESS
                self.state.progress = 100
                self.state.message = "完成"
                return result

            except Exception as e:
                last_error = e
                logger.error(f"[{self.name}] 执行失败 (第{attempt+1}次): {e}", exc_info=True)
                self.state.error = str(e)
                self.state.message = f"失败: {str(e)[:50]}"

                if attempt < self._max_retries:
                    await asyncio.sleep(2 ** attempt)  # 指数退避

        # 所有重试都失败
        self.state.status = AgentStatus.FAILED
        self.state.message = f"失败: {str(last_error)[:50]}"
        raise last_error

    def reset(self) -> None:
        """重置状态（用于重做）"""
        self.state = AgentState(agent_name=self.name)
        self._retry_count = 0


# 智能体名称常量
AGENT_STORYBOARDER = "storyboarder"
AGENT_ILLUSTRATOR = "illustrator"
AGENT_SCRIPTWRITER = "scriptwriter"
AGENT_VOICE_ACTOR = "voice_actor"
AGENT_EDITOR = "editor"

# 阶段顺序
AGENT_STAGES = [
    AGENT_STORYBOARDER,
    AGENT_ILLUSTRATOR,
    AGENT_SCRIPTWRITER,
    AGENT_VOICE_ACTOR,
    AGENT_EDITOR,
]
