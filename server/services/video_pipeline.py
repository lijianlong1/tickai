"""
视频生成流水线

编排整个视频生成流程：
1. 文本模型 → 分镜剧本（包含画面描述、字幕文本）
2. 图像模型 → 为每个分镜生成画面
3. TTS 服务 → 为每个分镜生成音频
4. 视频合成器 → 合并图像 + 音频 + 字幕 → MP4
5. 状态更新 + 进度通知

异步执行，使用 FastAPI BackgroundTasks 启动。
"""
import os
import json
import time
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import get_db
from models.video_project import VideoProject
from models.character import Character
from services.subtitle_renderer import SubtitleConfig, FrameData
from services.tts_service import TTSService, VoiceConfig, get_tts_service
from services.video_compositor import VideoCompositor
from services.video_generator import get_video_generator, VideoGenRequest

logger = logging.getLogger(__name__)


class VideoPipeline:
    """视频生成流水线"""

    # 状态常量
    STATUS_PENDING = "pending"
    STATUS_GENERATING_SCRIPT = "generating_script"
    STATUS_GENERATING_IMAGES = "generating_images"
    STATUS_GENERATING_VOICE = "generating_voice"
    STATUS_COMPOSING = "composing"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"

    # 进度权重
    PROGRESS_WEIGHTS = {
        "script": 15,       # 剧本 15%
        "images": 35,       # 图像 35%
        "voice": 20,        # 语音 20%
        "compose": 30,      # 合成 30%
    }

    def __init__(self):
        """初始化流水线"""
        self.tts_service = get_tts_service()
        self.compositor = VideoCompositor()
        logger.info("VideoPipeline 已初始化")

    async def run(self, project_id: int) -> Dict[str, Any]:
        """
        执行完整的视频生成流程

        Args:
            project_id: 视频项目 ID

        Returns:
            执行结果 {"success": bool, "video_path": str, "error": str}
        """
        start_time = time.time()
        logger.info(f"[Pipeline] 开始处理项目 {project_id}")

        try:
            # 加载项目
            project = await self._load_project(project_id)
            if not project:
                raise ValueError(f"项目 {project_id} 不存在")

            # 解析配置
            model_config = json.loads(project.model_config) if project.model_config else {}
            subtitle_config = self._parse_subtitle_config(project.subtitle_config)
            character_ids = json.loads(project.character_ids) if project.character_ids else []

            # 加载角色
            characters = await self._load_characters(character_ids)

            # 步骤 1：生成剧本
            await self._update_status(
                project_id, self.STATUS_GENERATING_SCRIPT, 5,
                "正在生成分镜剧本..."
            )
            storyboard = await self._step1_generate_script(
                project, model_config, characters
            )
            await self._save_storyboard(project_id, storyboard)
            await self._update_status(
                project_id, self.STATUS_GENERATING_SCRIPT, 15,
                f"剧本完成，共 {len(storyboard['panels'])} 个分镜"
            )

            # 步骤 2：生成图像
            await self._update_status(
                project_id, self.STATUS_GENERATING_IMAGES, 20,
                "正在生成分镜画面..."
            )
            image_paths = await self._step2_generate_images(
                project, storyboard, model_config
            )

            # 步骤 3：生成语音
            await self._update_status(
                project_id, self.STATUS_GENERATING_VOICE, 55,
                "正在生成语音..."
            )
            audio_path = await self._step3_generate_voice(
                project, storyboard, model_config
            )

            # 步骤 4：合成视频
            await self._update_status(
                project_id, self.STATUS_COMPOSING, 75,
                "正在合成视频..."
            )
            video_path = await self._step4_compose_video(
                project, storyboard, image_paths, audio_path, subtitle_config
            )

            # 生成缩略图
            thumbnail_path = None
            try:
                thumbnail_path = self.compositor.generate_thumbnail(video_path)
            except Exception as e:
                logger.warning(f"生成缩略图失败: {e}")

            # 更新项目状态
            await self._update_project_success(
                project_id, video_path, thumbnail_path
            )

            elapsed = time.time() - start_time
            logger.info(f"[Pipeline] 项目 {project_id} 完成，耗时 {elapsed:.2f}s")

            return {
                "success": True,
                "project_id": project_id,
                "video_path": video_path,
                "elapsed": elapsed,
            }

        except Exception as e:
            logger.error(f"[Pipeline] 项目 {project_id} 失败: {e}", exc_info=True)
            await self._update_status(
                project_id, self.STATUS_FAILED, 0,
                f"生成失败: {str(e)}",
                error_message=str(e),
            )
            return {
                "success": False,
                "project_id": project_id,
                "error": str(e),
            }

    async def _step1_generate_script(
        self,
        project: VideoProject,
        model_config: Dict[str, Any],
        characters: List[Character],
    ) -> Dict[str, Any]:
        """
        步骤 1：使用文本模型生成分镜剧本

        Returns:
            {
                "panels": [
                    {
                        "index": 1,
                        "scene": "画面描述",
                        "narration": "旁白文字（用作字幕）",
                        "character_id": 1,
                        "duration": 5  # 秒
                    }
                ]
            }
        """
        duration = project.duration
        # 估算分镜数（每 5 秒一个分镜）
        panel_count = max(2, min(8, duration // 5))

        # 构造角色描述
        char_desc = ""
        if characters:
            char_desc = "\n\n可用角色：\n"
            for ch in characters:
                char_desc += f"- {ch.name}：{ch.description}\n"

        # 构造提示词
        prompt = f"""请根据以下内容创作一个视频分镜剧本。

用户需求：{project.script_prompt}

视频参数：
- 总时长：{duration} 秒
- 分镜数量：{panel_count} 个
- 画面比例：{project.ratio}
{char_desc}

要求：
1. 每个分镜需要包含：index（序号）、scene（画面描述，用于生成图像）、narration（旁白/对白文字）、character_id（使用的角色ID，0表示无角色）、duration（单镜头时长，秒）
2. 所有分镜的 duration 之和应等于 {duration} 秒
3. 画面描述要详细、生动，包含场景、氛围、人物动作
4. 旁白要简洁、有感染力
5. 输出严格的 JSON 格式，不要包含任何解释文字

输出格式：
{{
  "panels": [
    {{
      "index": 1,
      "scene": "...",
      "narration": "...",
      "character_id": 0,
      "duration": 5
    }}
  ]
}}"""

        # 调用文本模型（简化版：使用占位实现）
        # 实际实现时调用 LLMClient
        storyboard = await self._call_text_model(prompt, model_config.get("text", {}))

        # 兜底：如果模型调用失败，使用简单的分镜模板
        if not storyboard or "panels" not in storyboard:
            logger.warning("文本模型返回无效，使用默认分镜")
            storyboard = self._generate_default_storyboard(
                project.script_prompt, duration, panel_count, characters
            )

        return storyboard

    async def _step2_generate_images(
        self,
        project: VideoProject,
        storyboard: Dict[str, Any],
        model_config: Dict[str, Any],
    ) -> List[str]:
        """
        步骤 2：为每个分镜生成图像
        """
        panels = storyboard.get("panels", [])
        image_dir = "static/images"
        os.makedirs(image_dir, exist_ok=True)

        image_paths = []
        total = len(panels)

        for i, panel in enumerate(panels):
            # 更新进度
            progress = 20 + int(35 * (i / total))
            await self._update_status(
                project.project_id if hasattr(project, 'project_id') else project.id,
                self.STATUS_GENERATING_IMAGES, progress,
                f"正在生成第 {i + 1}/{total} 帧画面..."
            )

            # 调用图像模型（简化版：生成占位图）
            image_path = await self._generate_panel_image(
                panel, project.ratio, image_dir, project.id
            )
            image_paths.append(image_path)

        return image_paths

    async def _step3_generate_voice(
        self,
        project: VideoProject,
        storyboard: Dict[str, Any],
        model_config: Dict[str, Any],
    ) -> Optional[str]:
        """
        步骤 3：生成语音（合并所有分镜的旁白为单个音频）
        """
        panels = storyboard.get("panels", [])
        if not panels:
            return None

        # 收集所有旁白
        narrations = [p.get("narration", "") for p in panels if p.get("narration")]
        if not narrations:
            return None

        # 为每段旁白生成音频
        audio_paths = []
        voice_config_dict = model_config.get("voice", {})
        voice_config = VoiceConfig(
            provider=voice_config_dict.get("provider", "web_speech"),
            voice=voice_config_dict.get("voice", "default"),
            language=voice_config_dict.get("language", "zh-CN"),
        )

        for i, narration in enumerate(narrations):
            await self._update_status(
                project.id, self.STATUS_GENERATING_VOICE,
                55 + int(20 * (i / len(narrations))),
                f"正在生成第 {i + 1}/{len(narrations)} 段旁白..."
            )
            audio_path = await self.tts_service.synthesize(
                text=narration,
                voice_config=voice_config,
                project_id=project.id,
            )
            audio_paths.append(audio_path)

        # 合并所有音频
        merged_path = f"static/audios/video_{project.id}_merged.mp3"
        return self.tts_service.merge_audios(audio_paths, merged_path)

    async def _step4_compose_video(
        self,
        project: VideoProject,
        storyboard: Dict[str, Any],
        image_paths: List[str],
        audio_path: Optional[str],
        subtitle_config: SubtitleConfig,
    ) -> str:
        """
        步骤 4：合成视频
        """
        panels = storyboard.get("panels", [])

        # 构造帧数据
        frames: List[FrameData] = []
        for i, panel in enumerate(panels):
            if i < len(image_paths):
                frames.append(FrameData(
                    image_path=image_paths[i],
                    text=panel.get("narration", ""),
                    duration_ms=int(panel.get("duration", 5) * 1000),
                ))

        if not frames:
            raise ValueError("没有可用的帧数据")

        # 合成视频
        output_filename = f"video_{project.id}.mp4"
        return self.compositor.compose(
            frames=frames,
            audio_path=audio_path,
            ratio=project.ratio,
            duration=project.duration,
            subtitle_config=subtitle_config,
            output_filename=output_filename,
        )

    async def _call_text_model(
        self, prompt: str, config: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        调用文本模型（简化版）

        实际实现时需要：
        1. 加载用户配置（API key 等）
        2. 调用 LLMClient
        3. 解析返回的 JSON
        """
        # 简化实现：返回 None 让流程回退到默认分镜
        logger.info("文本模型调用（占位实现）")
        return None

    def _generate_default_storyboard(
        self,
        user_prompt: str,
        total_duration: int,
        panel_count: int,
        characters: List[Character],
    ) -> Dict[str, Any]:
        """
        生成默认分镜（当 LLM 调用失败时使用）
        """
        per_panel = max(2, total_duration // panel_count)
        panels = []

        for i in range(panel_count):
            char_id = 0
            if characters and i < len(characters):
                char_id = characters[i].id

            panels.append({
                "index": i + 1,
                "scene": f"场景 {i + 1}：{user_prompt[:50]}...",
                "narration": f"这是第 {i + 1} 段旁白。",
                "character_id": char_id,
                "duration": per_panel,
            })

        return {"panels": panels}

    async def _generate_panel_image(
        self,
        panel: Dict[str, Any],
        ratio: str,
        output_dir: str,
        project_id: int,
    ) -> str:
        """
        生成分镜图像（简化版：生成占位图）

        实际实现时调用图像生成 API。
        """
        from PIL import Image, ImageDraw, ImageFont

        # 比例 → 分辨率
        resolutions = {"16:9": (1280, 720), "9:16": (720, 1280), "1:1": (1024, 1024), "4:3": (960, 720)}
        resolution = resolutions.get(ratio, (1280, 720))

        # 创建占位图（带文字说明）
        img = Image.new("RGB", resolution, (60, 80, 120))
        draw = ImageDraw.Draw(img)

        # 尝试加载字体
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 36)
        except OSError:
            font = ImageFont.load_default()

        # 绘制文字
        text = f"分镜 {panel.get('index', '?')}\n{panel.get('scene', '')[:50]}"
        draw.text((50, 50), text, font=font, fill=(255, 255, 255))

        # 保存
        image_path = os.path.join(output_dir, f"project_{project_id}_panel_{panel.get('index', 0)}.jpg")
        img.save(image_path, quality=85)
        return image_path

    def _parse_subtitle_config(self, json_str: Optional[str]) -> SubtitleConfig:
        """解析字幕配置 JSON"""
        if not json_str:
            return SubtitleConfig(enabled=False)
        try:
            data = json.loads(json_str)
            return SubtitleConfig(**data)
        except Exception as e:
            logger.warning(f"解析字幕配置失败: {e}")
            return SubtitleConfig(enabled=False)

    async def _load_project(self, project_id: int) -> Optional[VideoProject]:
        """加载项目"""
        async for db in get_db():
            result = await db.execute(
                select(VideoProject).where(VideoProject.id == project_id)
            )
            return result.scalar_one_or_none()
        return None

    async def _load_characters(self, character_ids: List[int]) -> List[Character]:
        """加载角色"""
        if not character_ids:
            return []
        async for db in get_db():
            result = await db.execute(
                select(Character).where(Character.id.in_(character_ids))
            )
            return list(result.scalars().all())
        return []

    async def _save_storyboard(self, project_id: int, storyboard: Dict[str, Any]) -> None:
        """保存分镜数据"""
        async for db in get_db():
            result = await db.execute(
                select(VideoProject).where(VideoProject.id == project_id)
            )
            project = result.scalar_one_or_none()
            if project:
                project.storyboard = json.dumps(storyboard, ensure_ascii=False)
                await db.commit()

    async def _update_status(
        self,
        project_id: int,
        status: str,
        progress: int,
        current_step: str,
        error_message: Optional[str] = None,
    ) -> None:
        """更新项目状态和进度"""
        async for db in get_db():
            result = await db.execute(
                select(VideoProject).where(VideoProject.id == project_id)
            )
            project = result.scalar_one_or_none()
            if project:
                project.status = status
                project.progress = progress
                project.current_step = current_step
                if error_message:
                    project.error_message = error_message
                await db.commit()
                logger.info(f"项目 {project_id} 状态: {status} ({progress}%) - {current_step}")

    async def _update_project_success(
        self,
        project_id: int,
        video_path: str,
        thumbnail_path: Optional[str],
    ) -> None:
        """标记项目成功"""
        async for db in get_db():
            result = await db.execute(
                select(VideoProject).where(VideoProject.id == project_id)
            )
            project = result.scalar_one_or_none()
            if project:
                project.status = self.STATUS_COMPLETED
                project.progress = 100
                project.current_step = "生成完成"
                project.video_url = f"/static/videos/{os.path.basename(video_path)}"
                if thumbnail_path:
                    project.thumbnail_url = f"/static/images/{os.path.basename(thumbnail_path)}"
                await db.commit()


# 单例
_pipeline_instance: Optional[VideoPipeline] = None


def get_video_pipeline() -> VideoPipeline:
    """获取视频流水线单例"""
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = VideoPipeline()
    return _pipeline_instance
