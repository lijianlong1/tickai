"""
字幕渲染服务

使用 Pillow 在图像上绘制字幕，支持：
- 9 种位置（顶/中/底 × 左/中/右）+ 自定义坐标
- 字号、颜色、描边、背景框
- 简单动画（淡入、打字机）

无需 ASS 文件，直接在每帧画面上绘制。
"""
import os
import logging
from typing import Tuple, Optional
from PIL import Image, ImageDraw, ImageFont
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ============ Pydantic Models ============

class SubtitleConfig(BaseModel):
    """字幕配置"""
    enabled: bool = Field(default=True, description="是否启用字幕")
    position: str = Field(
        default="bottom_center",
        description="字幕位置：top_left/top_center/top_right/middle_left/middle_center/middle_right/bottom_left/bottom_center/bottom_right"
    )
    font_size: int = Field(default=48, ge=16, le=96, description="字号")
    font_color: str = Field(default="#FFFFFF", description="文字颜色（hex）")
    outline_color: str = Field(default="#000000", description="描边颜色（hex）")
    outline_width: int = Field(default=2, ge=0, le=6, description="描边粗细")
    bold: bool = Field(default=True, description="是否加粗")
    bg_enabled: bool = Field(default=True, description="是否显示背景框")
    bg_color: str = Field(default="#00000080", description="背景框颜色（含透明度）")
    margin_top: int = Field(default=30, ge=0, le=300, description="上下边距")
    margin_horizontal: int = Field(default=30, ge=0, le=300, description="左右边距")
    animation: str = Field(default="none", description="动画：none/fade_in/typewriter")


class FrameData(BaseModel):
    """单帧数据"""
    image_path: str = Field(..., description="图像文件路径")
    text: str = Field(default="", description="字幕文字")
    duration_ms: int = Field(default=5000, ge=100, description="单帧持续时长（毫秒）")


# ============ 字幕渲染器 ============

class SubtitleRenderer:
    """字幕渲染器（基于 Pillow）"""

    # 9 种位置预设：(水平对齐, 垂直对齐, 上下边距, 左右边距)
    POSITION_MAP = {
        "top_left": ("left", "top", 30, 30),
        "top_center": ("center", "top", 30, 0),
        "top_right": ("right", "top", 30, 30),
        "middle_left": ("left", "middle", 0, 30),
        "middle_center": ("center", "middle", 0, 0),
        "middle_right": ("right", "middle", 0, 30),
        "bottom_left": ("left", "bottom", 30, 30),
        "bottom_center": ("center", "bottom", 30, 0),
        "bottom_right": ("right", "bottom", 30, 30),
    }

    # 跨平台字体路径
    FONT_PATHS = [
        "C:/Windows/Fonts/msyh.ttc",      # 微软雅黑
        "C:/Windows/Fonts/msyh.ttf",
        "C:/Windows/Fonts/simhei.ttf",    # 黑体
        "C:/Windows/Fonts/simsun.ttc",    # 宋体
        "/System/Library/Fonts/PingFang.ttc",  # macOS
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",  # Linux
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux fallback
    ]

    def __init__(self):
        """初始化字体缓存"""
        self._font_cache: dict = {}

    def render_subtitle_on_frame(
        self,
        image: Image.Image,
        text: str,
        config: SubtitleConfig,
        frame_in_panel: int = 0,
        total_frames_in_panel: int = 1,
    ) -> Image.Image:
        """
        在单帧图像上绘制字幕

        Args:
            image: PIL Image 对象
            text: 字幕文字
            config: 字幕配置
            frame_in_panel: 当前帧在镜头中的索引
            total_frames_in_panel: 该镜头总帧数

        Returns:
            处理后的 Image 对象
        """
        if not text or not config.enabled:
            return image

        # 转换为 RGBA 以支持半透明
        if image.mode != "RGBA":
            image = image.convert("RGBA")

        # 应用动画
        text = self._apply_animation(
            text, config, frame_in_panel, total_frames_in_panel
        )

        if not text:
            return image

        # 创建绘图层
        overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        # 获取字体
        font = self._get_font(config.font_size, config.bold)

        # 自动换行
        max_width = image.size[0] - 2 * config.margin_horizontal
        lines = self._wrap_text(text, font, max_width)

        # 绘制字幕
        self._draw_lines(draw, lines, font, config, image.size)

        # 合成
        result = Image.alpha_composite(image, overlay)
        return result

    def _draw_lines(
        self,
        draw: ImageDraw.ImageDraw,
        lines: list,
        font: ImageFont.FreeTypeFont,
        config: SubtitleConfig,
        canvas_size: Tuple[int, int],
    ) -> None:
        """在图像上逐行绘制字幕"""
        width, height = canvas_size

        # 获取位置参数
        position, v_align, default_margin_top, default_margin_h = self.POSITION_MAP.get(
            config.position, self.POSITION_MAP["bottom_center"]
        )
        margin_top = config.margin_top if config.margin_top else default_margin_top
        margin_h = config.margin_horizontal if config.margin_horizontal else default_margin_h

        # 计算每行高度
        line_height = int(config.font_size * 1.5)
        total_text_height = len(lines) * line_height

        # 计算 Y 起始坐标
        if v_align == "top":
            y_start = margin_top
        elif v_align == "middle":
            y_start = (height - total_text_height) // 2
        else:  # bottom
            y_start = height - total_text_height - margin_top

        # 颜色转换
        font_color = self._hex_to_rgba(config.font_color, 255)
        outline_color = self._hex_to_rgba(config.outline_color, 255)
        bg_color = self._hex_to_rgba(config.bg_color, 128)

        # 逐行绘制
        for i, line in enumerate(lines):
            if not line:
                continue
            # 计算 X 坐标
            text_w = draw.textlength(line, font=font)
            if position == "left":
                x = margin_h
            elif position == "right":
                x = width - text_w - margin_h
            else:  # center
                x = (width - text_w) // 2

            y = y_start + i * line_height

            # 绘制背景框
            if config.bg_enabled:
                padding = 10
                draw.rectangle(
                    [
                        x - padding,
                        y - padding,
                        x + text_w + padding,
                        y + line_height - padding,
                    ],
                    fill=bg_color,
                )

            # 绘制描边（4 个方向）
            if config.outline_width > 0:
                ow = config.outline_width
                for dx in [-ow, 0, ow]:
                    for dy in [-ow, 0, ow]:
                        if dx == 0 and dy == 0:
                            continue
                        draw.text((x + dx, y + dy), line, font=font, fill=outline_color)

            # 绘制主文字
            draw.text((x, y), line, font=font, fill=font_color)

    def _get_font(self, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        """
        获取字体（支持中文 + 跨平台）

        Args:
            size: 字号
            bold: 是否加粗

        Returns:
            PIL 字体对象
        """
        cache_key = (size, bold)
        if cache_key in self._font_cache:
            return self._font_cache[cache_key]

        # 尝试加载系统字体
        font = None
        for path in self.FONT_PATHS:
            if os.path.exists(path):
                try:
                    font = ImageFont.truetype(path, size)
                    logger.debug(f"已加载字体: {path}, size={size}")
                    break
                except OSError:
                    continue

        if font is None:
            logger.warning("未找到系统中文字体，使用默认字体")
            font = ImageFont.load_default()

        self._font_cache[cache_key] = font
        return font

    def _wrap_text(
        self, text: str, font: ImageFont.FreeTypeFont, max_width: int
    ) -> list:
        """自动换行（按字符宽度计算）"""
        if not text:
            return []

        # 简单按字符换行（中文按字、英文按词）
        lines = []
        current_line = ""

        # 优先按换行符分割
        paragraphs = text.split("\n")
        for para in paragraphs:
            if not para:
                lines.append("")
                continue

            current_line = ""
            for char in para:
                test_line = current_line + char
                # 估算宽度
                try:
                    test_w = font.getbbox(test_line)[2]
                except (AttributeError, OSError):
                    # 旧版 PIL 兼容
                    test_w = len(test_line) * font.size

                if test_w <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = char

            if current_line:
                lines.append(current_line)

        return lines

    def _hex_to_rgba(self, hex_color: str, default_alpha: int = 255) -> Tuple[int, int, int, int]:
        """
        将 hex 颜色转换为 RGBA 元组

        支持格式：
        - #FFFFFF
        - #FFFFFFFF
        - #FFFFFF80
        """
        hex_color = hex_color.lstrip("#")

        if len(hex_color) == 6:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            return (r, g, b, default_alpha)
        elif len(hex_color) == 8:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            a = int(hex_color[6:8], 16)
            return (r, g, b, a)
        else:
            # 默认白色
            return (255, 255, 255, default_alpha)

    def _apply_animation(
        self,
        text: str,
        config: SubtitleConfig,
        frame_index: int,
        total_frames: int,
    ) -> str:
        """
        应用字幕动画

        Args:
            text: 原始文字
            config: 字幕配置
            frame_index: 当前帧在镜头中的索引
            total_frames: 该镜头总帧数

        Returns:
            处理后的文字
        """
        if total_frames <= 1 or frame_index >= total_frames:
            return text

        if config.animation == "fade_in":
            # 淡入：前 30% 帧逐渐显示完整文字
            fade_threshold = max(1, int(total_frames * 0.3))
            if frame_index < fade_threshold:
                # 用透明度通过字符逐步显示
                ratio = frame_index / fade_threshold
                char_count = max(1, int(len(text) * ratio))
                return text[:char_count]
            return text

        elif config.animation == "typewriter":
            # 打字机效果：按字符逐步显示
            ratio = (frame_index + 1) / total_frames
            char_count = max(1, int(len(text) * ratio))
            return text[:char_count]

        return text


# 单例实例（避免重复加载字体）
_renderer_instance: Optional[SubtitleRenderer] = None


def get_subtitle_renderer() -> SubtitleRenderer:
    """获取字幕渲染器单例"""
    global _renderer_instance
    if _renderer_instance is None:
        _renderer_instance = SubtitleRenderer()
    return _renderer_instance
