"""
配音师智能体（VoiceActor）

职责：
- 将旁白转为语音
- 智能调整镜头时长（如果实际音频时长超过分配时间）
- 合并所有音频

使用模型：TTS（默认 OpenAI tts-1）
"""
import os
import logging
import asyncio
from datetime import datetime
from typing import List, Optional

from services.agents.base_agent import (
    BaseAgent,
    WorkflowContext,
    PanelData,
    AGENT_VOICE_ACTOR,
)

logger = logging.getLogger(__name__)


class VoiceActorAgent(BaseAgent):
    """配音师智能体"""

    name = AGENT_VOICE_ACTOR
    display_name = "配音师"
    description = "将旁白转为语音，智能调整镜头时长"
    icon = "🎙️"
    color = "#06B6D4"  # 青色

    AUDIO_DIR = "static/audios"

    async def run(self, context: WorkflowContext) -> WorkflowContext:
        """执行配音任务"""
        os.makedirs(self.AUDIO_DIR, exist_ok=True)

        voice_config = context.config.model_config.get("voice", {})
        provider = voice_config.get("provider", "openai")
        model = voice_config.get("model", "tts-1")
        voice = voice_config.get("voice", "alloy")
        speed = voice_config.get("speed", 1.0)

        total_panels = len(context.panels)
        audio_paths: List[str] = []

        for idx, panel in enumerate(context.panels):
            try:
                if not panel.audio_url and panel.narration:
                    self.update_progress(
                        int(80 * (idx / total_panels)) + 5,
                        f"为镜头 {panel.index}/{total_panels} 生成语音...",
                    )

                    audio_path = await self._synthesize(
                        text=panel.narration,
                        provider=provider,
                        model=model,
                        voice=voice,
                        speed=speed,
                        workflow_id=context.config.workflow_id,
                        panel_index=panel.index,
                    )
                    panel.audio_url = audio_path

                if panel.audio_url:
                    audio_paths.append(panel.audio_url)

                # 估算实际音频时长
                if panel.audio_url:
                    actual_duration = self._estimate_audio_duration(panel.narration, speed)
                    panel.audio_duration = actual_duration

                    # 如果实际时长超过分配时间，延长镜头
                    if actual_duration > panel.duration + 0.5:
                        logger.info(
                            f"镜头 {panel.index} 实际音频 {actual_duration:.1f}s "
                            f"> 分配 {panel.duration:.1f}s，自动延长"
                        )
                        panel.duration = actual_duration

                self.update_progress(
                    int(80 * (idx / total_panels)) + 10,
                    f"镜头 {panel.index} 语音生成完成",
                )

            except Exception as e:
                logger.error(f"镜头 {panel.index} 语音生成失败: {e}", exc_info=True)
                # 创建占位音频
                if not panel.audio_url:
                    panel.audio_url = await self._create_placeholder_audio(
                        panel.narration, context.config.workflow_id, panel.index
                    )
                audio_paths.append(panel.audio_url)

        self.update_progress(95, f"配音完成：{len(audio_paths)}/{total_panels}")

        # 合并所有音频
        if audio_paths:
            try:
                merged_path = self._merge_audios(audio_paths, context.config.workflow_id)
                context._merged_audio_path = merged_path
            except Exception as e:
                logger.error(f"合并音频失败: {e}")

        self.update_progress(100, "配音师完成")

        return context

    async def regenerate_panel_voice(
        self, panel: PanelData, context: WorkflowContext
    ) -> None:
        """重新生成某个镜头的语音"""
        voice_config = context.config.model_config.get("voice", {})
        provider = voice_config.get("provider", "openai")
        model = voice_config.get("model", "tts-1")
        voice = voice_config.get("voice", "alloy")
        speed = voice_config.get("speed", 1.0)

        if not panel.narration:
            return

        audio_path = await self._synthesize(
            text=panel.narration,
            provider=provider,
            model=model,
            voice=voice,
            speed=speed,
            workflow_id=context.config.workflow_id,
            panel_index=panel.index,
        )
        panel.audio_url = audio_path

        actual_duration = self._estimate_audio_duration(panel.narration, speed)
        panel.audio_duration = actual_duration
        if actual_duration > panel.duration + 0.5:
            panel.duration = actual_duration

    async def _synthesize(
        self,
        text: str,
        provider: str,
        model: str,
        voice: str,
        speed: float,
        workflow_id: int,
        panel_index: int,
    ) -> str:
        """合成语音"""
        from services.model_adapter import ModelAdapter

        try:
            adapter = ModelAdapter.from_config({
                "provider": provider,
                "model": model,
            })

            # OpenAI TTS
            if provider == "openai":
                from openai import AsyncOpenAI
                client = AsyncOpenAI(
                    api_key=os.getenv("OPENAI_API_KEY"),
                    timeout=60.0,
                )
                response = await client.audio.speech.create(
                    model=model,
                    voice=voice,
                    input=text,
                    speed=speed,
                )

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"workflow_{workflow_id}_panel_{panel_index}_{timestamp}.mp3"
                save_path = os.path.join(self.AUDIO_DIR, filename)

                with open(save_path, "wb") as f:
                    f.write(response.content)

                return f"/{save_path.replace(os.sep, '/')}"

        except Exception as e:
            logger.warning(f"OpenAI TTS 失败: {e}，使用占位")

        # 占位实现
        return await self._create_placeholder_audio(text, workflow_id, panel_index)

    async def _create_placeholder_audio(
        self, text: str, workflow_id: int, panel_index: int
    ) -> str:
        """创建占位音频文件（实际应由 TTS 生成）"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"workflow_{workflow_id}_panel_{panel_index}_placeholder_{timestamp}.mp3"
        save_path = os.path.join(self.AUDIO_DIR, filename)
        os.makedirs(self.AUDIO_DIR, exist_ok=True)
        with open(save_path, "wb") as f:
            f.write(f"# Placeholder audio for: {text}\n".encode())
        return f"/{save_path.replace(os.sep, '/')}"

    def _estimate_audio_duration(self, text: str, speed: float = 1.0) -> float:
        """
        估算音频时长

        中文 TTS 通常每秒约 4-5 个字（含停顿）。
        """
        if not text:
            return 2.0
        # 去除标点
        char_count = sum(1 for c in text if c.strip())
        # 4 字/秒，可根据 speed 调整
        base_speed = 4.0 * speed
        return max(2.0, char_count / base_speed)

    def _merge_audios(self, audio_paths: List[str], workflow_id: int) -> str:
        """合并所有音频"""
        if len(audio_paths) <= 1:
            return audio_paths[0] if audio_paths else ""

        # 简单实现：返回第一个音频的路径
        # 实际应使用 ffmpeg 或 pydub 拼接
        return audio_paths[0]
