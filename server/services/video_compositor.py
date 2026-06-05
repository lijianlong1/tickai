"""
视频合成主类（Pillow 驱动）

负责将图像序列 + 音频 + 字幕合成为最终 MP4 视频。
不依赖 FFmpeg（虽然使用 ffmpeg 合并音频），使用 Pillow 处理每一帧。

核心流程：
1. 计算每帧需要的重复次数
2. 遍历每个分镜：
   a. 加载并缩放图像
   b. 用 SubtitleRenderer 烧录字幕
3. 用 imageio 将帧序列编码为 MP4
4. （可选）合并音频轨
"""
import os
import time
import logging
import subprocess
from typing import List, Optional, Tuple
from PIL import Image

import numpy as np
import imageio

from services.subtitle_renderer import (
    SubtitleRenderer,
    SubtitleConfig,
    FrameData,
    get_subtitle_renderer,
)

logger = logging.getLogger(__name__)


class VideoCompositor:
    """视频合成器（Pillow + imageio）"""

    # 比例 → 分辨率
    RATIO_RESOLUTIONS = {
        "16:9": (1920, 1080),
        "9:16": (1080, 1920),
        "1:1": (1024, 1024),
        "4:3": (1440, 1080),
    }

    def __init__(self, fps: int = 24, output_dir: str = "static/videos"):
        """
        初始化视频合成器

        Args:
            fps: 帧率（默认 24fps）
            output_dir: 输出目录
        """
        self.fps = fps
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.subtitle_renderer = get_subtitle_renderer()
        logger.info(f"VideoCompositor 已初始化: fps={fps}, output={output_dir}")

    def compose(
        self,
        frames: List[FrameData],
        audio_path: Optional[str] = None,
        ratio: str = "16:9",
        duration: int = 30,
        subtitle_config: Optional[SubtitleConfig] = None,
        output_filename: Optional[str] = None,
    ) -> str:
        """
        合成视频

        Args:
            frames: 帧数据列表
            audio_path: 合并后的音频文件路径（可选）
            ratio: 画面比例
            duration: 视频总时长（秒）
            subtitle_config: 字幕配置
            output_filename: 输出文件名（不含路径）

        Returns:
            最终视频文件路径
        """
        if not frames:
            raise ValueError("frames 不能为空")

        resolution = self.RATIO_RESOLUTIONS.get(ratio, (1920, 1080))
        subtitle_config = subtitle_config or SubtitleConfig(enabled=False)

        # 生成输出文件名
        if not output_filename:
            output_filename = f"video_{int(time.time())}.mp4"
        video_no_audio = os.path.join(self.output_dir, f"temp_{output_filename}")
        final_output = os.path.join(self.output_dir, output_filename)

        logger.info(f"开始合成视频: {len(frames)} 帧, ratio={ratio}, duration={duration}s")
        start_time = time.time()

        # 1. 计算帧分配
        total_frames = int(duration * self.fps)
        frames_per_panel = max(1, total_frames // len(frames))
        logger.info(f"总帧数: {total_frames}, 每镜头: {frames_per_panel} 帧")

        # 2. 渲染所有帧
        video_frames: List[np.ndarray] = []
        for panel_idx, panel in enumerate(frames):
            logger.info(f"渲染镜头 {panel_idx + 1}/{len(frames)}: {panel.image_path}")
            for frame_in_panel in range(frames_per_panel):
                try:
                    frame_img = self._render_frame(
                        image_path=panel.image_path,
                        text=panel.text,
                        config=subtitle_config,
                        resolution=resolution,
                        frame_in_panel=frame_in_panel,
                        total_frames_in_panel=frames_per_panel,
                    )
                    video_frames.append(np.array(frame_img.convert("RGB")))
                except Exception as e:
                    logger.error(f"渲染帧失败: {e}")
                    # 失败时插入黑帧
                    black_frame = Image.new("RGB", resolution, (0, 0, 0))
                    video_frames.append(np.array(black_frame))

        # 3. 写入 MP4
        logger.info(f"写入 MP4，共 {len(video_frames)} 帧")
        try:
            writer = imageio.get_writer(
                video_no_audio,
                fps=self.fps,
                codec="libx264",
                quality=8,
                macro_block_size=1,
            )
            for frame in video_frames:
                writer.append_data(frame)
            writer.close()
        except Exception as e:
            logger.error(f"imageio 写入失败: {e}")
            raise RuntimeError(f"视频编码失败: {e}")

        # 4. 合并音频
        elapsed = time.time() - start_time
        logger.info(f"视频帧合成耗时: {elapsed:.2f}s")

        if audio_path and os.path.exists(audio_path):
            try:
                self._merge_audio(video_no_audio, audio_path, final_output)
                os.remove(video_no_audio)  # 删除临时文件
                logger.info(f"视频合成完成: {final_output}")
                return final_output
            except Exception as e:
                logger.error(f"音频合并失败: {e}，返回无音频视频")
                # 合并失败时使用无音频版本
                if os.path.exists(video_no_audio):
                    os.rename(video_no_audio, final_output)
                return final_output
        else:
            # 无音频
            if os.path.exists(video_no_audio):
                os.rename(video_no_audio, final_output)
            logger.info(f"视频合成完成（无音频）: {final_output}")
            return final_output

    def _render_frame(
        self,
        image_path: str,
        text: str,
        config: SubtitleConfig,
        resolution: Tuple[int, int],
        frame_in_panel: int = 0,
        total_frames_in_panel: int = 1,
    ) -> Image.Image:
        """
        渲染单帧：加载图像 + 缩放 + 烧录字幕

        Args:
            image_path: 图像路径
            text: 字幕文字
            config: 字幕配置
            resolution: 目标分辨率
            frame_in_panel: 当前帧在镜头中的索引（用于动画）
            total_frames_in_panel: 镜头总帧数

        Returns:
            PIL Image 对象
        """
        # 1. 加载并缩放图像
        if not os.path.exists(image_path):
            logger.warning(f"图像不存在: {image_path}，使用占位黑图")
            img = Image.new("RGB", resolution, (30, 30, 30))
        else:
            try:
                img = Image.open(image_path).convert("RGB")
                img = self._resize_and_crop(img, resolution)
            except Exception as e:
                logger.error(f"加载图像失败: {e}")
                img = Image.new("RGB", resolution, (30, 30, 30))

        # 2. 烧录字幕
        if text and config.enabled:
            try:
                img = self.subtitle_renderer.render_subtitle_on_frame(
                    image=img,
                    text=text,
                    config=config,
                    frame_in_panel=frame_in_panel,
                    total_frames_in_panel=total_frames_in_panel,
                )
            except Exception as e:
                logger.error(f"字幕渲染失败: {e}")

        return img

    def _resize_and_crop(
        self, img: Image.Image, target: Tuple[int, int]
    ) -> Image.Image:
        """
        缩放并裁剪到目标尺寸（保持比例，覆盖整个区域）

        Args:
            img: 原图
            target: 目标尺寸 (宽, 高)

        Returns:
            处理后的图像
        """
        target_w, target_h = target
        target_ratio = target_w / target_h
        w, h = img.size
        img_ratio = w / h

        # 等比缩放（覆盖目标区域）
        if img_ratio > target_ratio:
            # 原图更宽 → 按高度缩放
            new_h = target_h
            new_w = int(w * target_h / h)
        else:
            # 原图更高 → 按宽度缩放
            new_w = target_w
            new_h = int(h * target_w / w)

        img = img.resize((new_w, new_h), Image.LANCZOS)

        # 中心裁剪
        left = (new_w - target_w) // 2
        top = (new_h - target_h) // 2
        return img.crop((left, top, left + target_w, top + target_h))

    def _merge_audio(
        self, video_path: str, audio_path: str, output_path: str
    ) -> str:
        """
        合并视频和音频

        使用 ffmpeg（如果可用）或 moviepy
        """
        # 方法 1：使用 ffmpeg
        try:
            cmd = [
                "ffmpeg", "-y",
                "-i", video_path,
                "-i", audio_path,
                "-c:v", "copy",
                "-c:a", "aac",
                "-shortest",
                output_path,
            ]
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=120
            )
            if result.returncode == 0:
                return output_path
        except FileNotFoundError:
            logger.warning("ffmpeg 未安装")
        except subprocess.TimeoutExpired:
            logger.warning("ffmpeg 合并超时")

        # 方法 2：使用 moviepy
        try:
            from moviepy.editor import VideoFileClip, AudioFileClip
            video_clip = VideoFileClip(video_path)
            audio_clip = AudioFileClip(audio_path)
            # 调整音频长度匹配视频
            if audio_clip.duration > video_clip.duration:
                audio_clip = audio_clip.subclip(0, video_clip.duration)
            final_clip = video_clip.set_audio(audio_clip)
            final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac", verbose=False, logger=None)
            video_clip.close()
            audio_clip.close()
            return output_path
        except ImportError:
            logger.warning("moviepy 未安装")
        except Exception as e:
            logger.error(f"moviepy 合并失败: {e}")

        # 兜底：复制视频
        import shutil
        shutil.copy(video_path, output_path)
        return output_path

    def generate_thumbnail(
        self,
        video_path: str,
        output_path: Optional[str] = None,
        time_offset: float = 1.0,
    ) -> str:
        """
        从视频中提取缩略图

        Args:
            video_path: 视频路径
            output_path: 输出路径
            time_offset: 时间偏移（秒）

        Returns:
            缩略图路径
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"视频不存在: {video_path}")

        if not output_path:
            base, _ = os.path.splitext(video_path)
            output_path = f"{base}_thumb.jpg"

        # 使用 ffmpeg 提取
        try:
            cmd = [
                "ffmpeg", "-y",
                "-ss", str(time_offset),
                "-i", video_path,
                "-vframes", "1",
                "-q:v", "2",
                output_path,
            ]
            subprocess.run(cmd, capture_output=True, timeout=30)
            if os.path.exists(output_path):
                return output_path
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        # 使用 imageio 读取第一帧
        try:
            reader = imageio.get_reader(video_path)
            frame = reader.get_data(int(time_offset * self.fps))
            Image.fromarray(frame).save(output_path, quality=85)
            reader.close()
            return output_path
        except Exception as e:
            logger.error(f"生成缩略图失败: {e}")
            raise
