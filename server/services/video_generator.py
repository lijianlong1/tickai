"""
视频生成接口（预留）

这是一个抽象接口层，用于未来接入真正的视频生成模型：
- Runway Gen-2 / Gen-3
- Pika Labs
- Stable Video Diffusion
- 智谱 CogVideo
- 通义 WanX

当前阶段不实现这些具体生成器，只暴露接口让未来无缝扩展。
当未注册任何生成器时，VideoPipeline 会回退到"图像剪辑"方案。
"""
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ============ Pydantic Models ============

class VideoGenRequest(BaseModel):
    """视频生成请求参数"""
    prompt: str = Field(..., description="生成提示词")
    image_path: Optional[str] = Field(default=None, description="参考图路径")
    duration: int = Field(default=5, ge=1, le=60, description="视频时长（秒）")
    ratio: str = Field(default="16:9", description="画面比例")
    seed: Optional[int] = Field(default=None, description="随机种子")
    extra_params: Optional[Dict[str, Any]] = Field(default=None, description="额外参数")


class VideoGenResult(BaseModel):
    """视频生成结果"""
    success: bool = Field(..., description="是否成功")
    video_path: Optional[str] = Field(default=None, description="视频文件路径")
    error_message: Optional[str] = Field(default=None, description="错误信息")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="元数据")


# ============ 抽象接口 ============

class VideoGeneratorInterface(ABC):
    """
    视频生成器抽象接口

    所有具体的视频生成器（Runway / Pika / CogVideo 等）都需要实现此接口。
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """生成器名称（唯一标识）"""
        ...

    @abstractmethod
    async def generate_video(self, request: VideoGenRequest) -> VideoGenResult:
        """
        生成视频

        Args:
            request: 生成请求参数

        Returns:
            生成结果（含视频文件路径或错误信息）
        """
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """
        检查生成器是否可用

        通常检查 API key 是否配置、依赖是否安装等。
        """
        ...

    def get_config_schema(self) -> Dict[str, Any]:
        """
        返回配置 schema（用于前端动态生成表单）

        Returns:
            配置字段定义
        """
        return {}


# ============ 具体实现占位 ============

class RunwayGenerator(VideoGeneratorInterface):
    """Runway Gen-2 生成器（占位实现）"""

    @property
    def name(self) -> str:
        return "runway"

    async def generate_video(self, request: VideoGenRequest) -> VideoGenResult:
        logger.warning("Runway 生成器尚未实现，请使用图像剪辑方案")
        return VideoGenResult(
            success=False,
            error_message="Runway 生成器尚未实现"
        )

    def is_available(self) -> bool:
        return False


class PikaGenerator(VideoGeneratorInterface):
    """Pika Labs 生成器（占位实现）"""

    @property
    def name(self) -> str:
        return "pika"

    async def generate_video(self, request: VideoGenRequest) -> VideoGenResult:
        logger.warning("Pika 生成器尚未实现，请使用图像剪辑方案")
        return VideoGenResult(
            success=False,
            error_message="Pika 生成器尚未实现"
        )

    def is_available(self) -> bool:
        return False


class CogVideoGenerator(VideoGeneratorInterface):
    """智谱 CogVideo 生成器（占位实现）"""

    @property
    def name(self) -> str:
        return "cogvideo"

    async def generate_video(self, request: VideoGenRequest) -> VideoGenResult:
        logger.warning("CogVideo 生成器尚未实现，请使用图像剪辑方案")
        return VideoGenResult(
            success=False,
            error_message="CogVideo 生成器尚未实现"
        )

    def is_available(self) -> bool:
        return False


# ============ 配置器 ============

class ConfigurableVideoGenerator:
    """
    视频生成配置器

    根据配置选择不同的视频生成器。如果未注册任何生成器或都不可用，
    则返回 None，由调用方决定是否回退到图像剪辑方案。
    """

    def __init__(self):
        self._generators: Dict[str, VideoGeneratorInterface] = {}
        self._default: Optional[str] = None
        logger.info("ConfigurableVideoGenerator 已初始化")

    def register(self, generator: VideoGeneratorInterface) -> None:
        """
        注册一个视频生成器

        Args:
            generator: 实现了 VideoGeneratorInterface 的实例
        """
        self._generators[generator.name] = generator
        logger.info(f"已注册视频生成器: {generator.name}")

    def set_default(self, name: str) -> None:
        """
        设置默认生成器

        Args:
            name: 生成器名称
        """
        if name not in self._generators:
            raise ValueError(f"生成器 {name} 未注册")
        self._default = name
        logger.info(f"默认视频生成器已设置为: {name}")

    def list_available(self) -> list:
        """列出所有可用的生成器"""
        return [
            {"name": g.name, "available": g.is_available()}
            for g in self._generators.values()
        ]

    async def generate(
        self,
        request: VideoGenRequest,
        generator_name: Optional[str] = None,
    ) -> Optional[VideoGenResult]:
        """
        调用视频生成器

        Args:
            request: 生成请求
            generator_name: 指定生成器，None 则使用默认

        Returns:
            生成结果；如果无生成器可用则返回 None
        """
        name = generator_name or self._default
        if not name or name not in self._generators:
            logger.debug("未指定视频生成器或生成器不可用")
            return None

        generator = self._generators[name]
        if not generator.is_available():
            logger.warning(f"视频生成器 {name} 不可用")
            return None

        logger.info(f"调用视频生成器: {name}")
        return await generator.generate_video(request)


# 全局单例
_video_generator: Optional[ConfigurableVideoGenerator] = None


def get_video_generator() -> ConfigurableVideoGenerator:
    """获取视频生成配置器单例"""
    global _video_generator
    if _video_generator is None:
        _video_generator = ConfigurableVideoGenerator()
        # 注册占位实现（未来替换为真实实现）
        _video_generator.register(RunwayGenerator())
        _video_generator.register(PikaGenerator())
        _video_generator.register(CogVideoGenerator())
    return _video_generator
