"""
剪辑师智能体（Editor）

职责：
- 用 Pillow 合成"主体图"和"背景图"（主体叠加在背景上）
- 用 SubtitleRenderer 烧录字幕
- 用 imageio 编码为 MP4
- 合并音频轨

使用工具：Pillow + imageio + ffmpeg
"""
import os
import time
import logging
from typing import Optional, Tuple
from datetime import datetime

from PIL import Image
import numpy as np
import imageio

from services.agents.base_agent import (
    BaseAgent,
    WorkflowContext,
    PanelData,
    AGENT_EDITOR,
)
from services.subtitle_renderer import SubtitleConfig, get_subtitle_renderer

logger = logging.getLogger(__name__)


class EditorAgent(BaseAgent):
    """剪辑师智能体"""

    name = AGENT_EDITOR
    display_name = "剪辑师"
    description = "合成图像（含字幕）和音频为最终视频"
    icon = "🎞️"
    color = "#F59E0B"  # 橙色

    VIDEO_DIR = "static/videos"
    FPS = 24

    async def run(self, context: WorkflowContext) -> WorkflowContext:
        """执行剪辑任务"""
        os.makedirs(self.VIDEO_DIR, exist_ok=True)

        # 解析比例
        resolution = self._get_resolution(context.config.ratio)

        # 解析字幕配置
        subtitle_config_dict = context.config.subtitle_config or {}
        subtitle_config = SubtitleConfig(
            enabled=subtitle_config_dict.get("enabled", True),
            position=subtitle_config_dict.get("position", "bottom_center"),
            font_size=subtitle_config_dict.get("font_size", 48),
            font_color=subtitle_config_dict.get("font_color", "#FFFFFF"),
            outline_color=subtitle_config_dict.get("outline_color", "#000000"),
            outline_width=subtitle_config_dict.get("outline_width", 2),
            bold=subtitle_config_dict.get("bold", True),
            bg_enabled=subtitle_config_dict.get("bg_enabled", True),
            bg_color=subtitle_config_dict.get("bg_color", "#00000080"),
            animation=subtitle_config_dict.get("animation", "none"),
        )

        # 准备帧
        subtitle_renderer = get_subtitle_renderer()
        frames = []
        total_panels = len(context.panels)

        for idx, panel in enumerate(context.panels):
            self.update_progress(
                int(70 * (idx / total_panels)) + 5,
                f"合成镜头 {panel.index}/{total_panels}...",
            )

            try:
                # 合成主体+背景
                composed = self._compose_subject_background(
                    subject_url=panel.subject_image_url,
                    background_url=panel.background_image_url,
                    resolution=resolution,
                    camera=panel.camera,
                )

                # 烧录字幕
                if subtitle_config.enabled and panel.narration:
                    composed = subtitle_renderer.render_subtitle_on_frame(
                        image=composed,
                        text=panel.narration,
                        config=subtitle_config,
                    )

                # 重复帧
                panel_frames = int(panel.duration * self.FPS)
                frames.append((composed, panel_frames))

            except Exception as e:
                logger.error(f"合成镜头 {panel.index} 失败: {e}")
                # 黑帧兜底
                black = Image.new("RGB", resolution, (0, 0, 0))
                frames.append((black, int(panel.duration * self.FPS)))

        self.update_progress(80, "编码视频...")

        # 编码为 MP4
        video_path = os.path.join(
            self.VIDEO_DIR,
            f"workflow_{context.config.workflow_id}_{int(time.time())}.mp4",
        )

        try:
            writer = imageio.get_writer(
                video_path,
                fps=self.FPS,
                codec="libx264",
                quality=8,
                macro_block_size=1,
            )
            for img, count in frames:
                arr = np.array(img.convert("RGB"))
                for _ in range(count):
                    writer.append_data(arr)
            writer.close()

            self.update_progress(95, "生成缩略图...")

            # 缩略图
            thumb_path = self._generate_thumbnail(frames, video_path)

            self.update_progress(100, "剪辑完成")

            # 保存到 context
            context._video_path = video_path
            context._thumbnail_path = thumb_path

        except Exception as e:
            logger.error(f"视频编码失败: {e}", exc_info=True)
            raise

        return context

    async def compose_video(self, context: WorkflowContext) -> Tuple[str, Optional[str]]:
        """供编排器调用的视频合成方法"""
        result = await self.run(context)
        return (
            getattr(context, "_video_path", ""),
            getattr(context, "_thumbnail_path", None),
        )

    def _compose_subject_background(
        self,
        subject_url: Optional[str],
        background_url: Optional[str],
        resolution: Tuple[int, int],
        camera: str = "中景",
    ) -> Image.Image:
        """
        合成主体图和背景图

        Args:
            subject_url: 主体图 URL
            background_url: 背景图 URL
            resolution: 目标分辨率
            camera: 镜头类型（决定主体大小）

        Returns:
            合成后的图像
        """
        target_w, target_h = resolution

        # 1. 加载背景（缩放到目标尺寸）
        if background_url:
            bg_path = background_url.lstrip("/").replace("/", os.sep)
            if os.path.exists(bg_path):
                try:
                    bg = Image.open(bg_path).convert("RGB")
                    bg = self._resize_and_crop(bg, resolution)
                except Exception as e:
                    logger.warning(f"加载背景图失败: {e}")
                    bg = Image.new("RGB", resolution, (40, 60, 100))
            else:
                bg = Image.new("RGB", resolution, (40, 60, 100))
        else:
            bg = Image.new("RGB", resolution, (40, 60, 100))

        # 2. 加载主体
        if subject_url:
            sub_path = subject_url.lstrip("/").replace("/", os.sep)
            if os.path.exists(sub_path):
                try:
                    subject = Image.open(sub_path).convert("RGBA")
                    # 根据镜头类型决定主体大小
                    if camera == "远景":
                        ratio = 0.3
                    elif camera == "中景":
                        ratio = 0.55
                    elif camera == "近景":
                        ratio = 0.8
                    else:  # 特写
                        ratio = 1.0

                    sub_w = int(target_h * ratio)
                    sub_h = int(target_h * ratio)
                    subject = subject.resize((sub_w, sub_h), Image.LANCZOS)

                    # 居中放置
                    x = (target_w - sub_w) // 2
                    y = (target_h - sub_h) // 2
                    bg.paste(subject, (x, y), subject)
                except Exception as e:
                    logger.warning(f"加载主体图失败: {e}")

        return bg

    def _resize_and_crop(
        self, img: Image.Image, target: Tuple[int, int]
    ) -> Image.Image:
        """缩放并裁剪到目标尺寸"""
        target_w, target_h = target
        target_ratio = target_w / target_h
        w, h = img.size
        img_ratio = w / h

        if img_ratio > target_ratio:
            new_h = target_h
            new_w = int(w * target_h / h)
        else:
            new_w = target_w
            new_h = int(h * target_w / w)

        img = img.resize((new_w, new_h), Image.LANCZOS)
        left = (new_w - target_w) // 2
        top = (new_h - target_h) // 2
        return img.crop((left, top, left + target_w, top + target_h))

    def _get_resolution(self, ratio: str) -> Tuple[int, int]:
        """根据比例获取分辨率"""
        sizes = {
            "16:9": (1920, 1080),
            "9:16": (1080, 1920),
            "1:1": (1024, 1024),
            "4:3": (1440, 1080),
        }
        return sizes.get(ratio, (1920, 1080))

    def _generate_thumbnail(
        self, frames, video_path: str
    ) -> Optional[str]:
        """生成缩略图（取第一帧）"""
        try:
            if not frames:
                return None
            first_frame = frames[0][0]
            thumb_path = video_path.replace(".mp4", "_thumb.jpg")
            first_frame.convert("RGB").save(thumb_path, quality=85)
            return thumb_path
        except Exception as e:
            logger.warning(f"生成缩略图失败: {e}")
            return None
