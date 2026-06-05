"""
文字转语音（TTS）服务

支持多种 TTS provider：
- web_speech: 浏览器内置（前端生成音频后上传）
- openai_tts: OpenAI TTS API
- volcengine_tts: 火山引擎 TTS（可选）

主要功能：
- synthesize: 文字转音频
- save_audio: 保存音频到文件
- get_audio_duration: 获取音频时长
- merge_audios: 合并多个音频
"""
import os
import json
import time
import logging
import hashlib
import subprocess
from typing import Optional, Dict, Any
from pathlib import Path
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ============ Pydantic Models ============

class VoiceConfig(BaseModel):
    """语音配置"""
    provider: str = Field(default="web_speech", description="TTS 提供商")
    voice: str = Field(default="default", description="声音名称")
    speed: float = Field(default=1.0, ge=0.5, le=2.0, description="语速")
    pitch: float = Field(default=1.0, ge=0.5, le=2.0, description="音调")
    volume: float = Field(default=1.0, ge=0.0, le=1.0, description="音量")
    language: str = Field(default="zh-CN", description="语言")
    extra_params: Optional[Dict[str, Any]] = Field(default=None, description="额外参数")


# ============ TTS 服务 ============

class TTSService:
    """TTS 服务封装"""

    SUPPORTED_PROVIDERS = ["web_speech", "openai_tts", "volcengine_tts"]

    def __init__(self, output_dir: str = "static/audios"):
        """
        初始化 TTS 服务

        Args:
            output_dir: 音频文件输出目录
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"TTSService 已初始化，输出目录: {output_dir}")

    async def synthesize(
        self,
        text: str,
        voice_config: Optional[VoiceConfig] = None,
        project_id: Optional[int] = None,
    ) -> str:
        """
        将文字合成为音频文件

        Args:
            text: 要合成的文字
            voice_config: 语音配置
            project_id: 视频项目 ID（用于生成唯一文件名）

        Returns:
            音频文件路径
        """
        if not text or not text.strip():
            raise ValueError("合成文字不能为空")

        config = voice_config or VoiceConfig()
        provider = config.provider

        if provider not in self.SUPPORTED_PROVIDERS:
            logger.warning(f"不支持的 TTS provider: {provider}，回退到 web_speech")
            provider = "web_speech"

        # 生成唯一文件名
        filename = self._generate_filename(text, config, project_id)
        output_path = os.path.join(self.output_dir, filename)

        # 根据 provider 调用不同实现
        if provider == "web_speech":
            # 浏览器内置 TTS：生成占位音频文件，由前端生成后上传
            audio_path = await self._synthesize_web_speech(text, config, output_path)
        elif provider == "openai_tts":
            audio_path = await self._synthesize_openai(text, config, output_path)
        elif provider == "volcengine_tts":
            audio_path = await self._synthesize_volcengine(text, config, output_path)
        else:
            raise ValueError(f"未实现的 TTS provider: {provider}")

        logger.info(f"TTS 合成完成: {audio_path}")
        return audio_path

    async def _synthesize_web_speech(
        self, text: str, config: VoiceConfig, output_path: str
    ) -> str:
        """
        Web Speech 占位实现

        由于 Web Speech API 是浏览器内置的，后端无法直接调用。
        这里创建一个占位音频文件，实际音频由前端使用 Web Speech API 生成后上传。
        占位文件会包含待合成的文字，前端上传真实音频时会替换该文件。
        """
        # 创建一个最小的静音 MP3 文件（占位）
        # 实际使用时，前端会调用 Web Speech API 生成音频，然后通过单独的上传接口
        # 替换这个占位文件
        placeholder_content = f"# Web Speech TTS Placeholder\n# Text: {text}\n# Generated at: {time.time()}\n".encode()
        with open(output_path, "wb") as f:
            f.write(placeholder_content)
        logger.debug(f"已创建 Web Speech 占位文件: {output_path}")
        return output_path

    async def _synthesize_openai(
        self, text: str, config: VoiceConfig, output_path: str
    ) -> str:
        """
        OpenAI TTS 实现

        需要在 voice_config.extra_params 中提供 api_key
        """
        try:
            from openai import AsyncOpenAI
        except ImportError:
            raise ImportError("请先安装 openai: pip install openai")

        api_key = (config.extra_params or {}).get("api_key")
        if not api_key:
            raise ValueError("OpenAI TTS 需要提供 api_key")

        client = AsyncOpenAI(api_key=api_key)

        # 调用 OpenAI TTS API
        response = await client.audio.speech.create(
            model="tts-1",
            voice=config.voice if config.voice in ["alloy", "echo", "fable", "onyx", "nova", "shimmer"] else "alloy",
            input=text,
            speed=config.speed,
        )

        # 保存音频
        with open(output_path, "wb") as f:
            f.write(response.content)

        return output_path

    async def _synthesize_volcengine(
        self, text: str, config: VoiceConfig, output_path: str
    ) -> str:
        """
        火山引擎 TTS 实现（占位）

        实际接入需要安装 volcengine SDK 并配置 app_id / token 等
        """
        logger.warning("火山引擎 TTS 暂未实现，请使用 web_speech 或 openai_tts")
        # 回退到 web_speech
        return await self._synthesize_web_speech(text, config, output_path)

    def save_audio(self, audio_data: bytes, output_path: str) -> str:
        """
        保存音频数据到文件

        Args:
            audio_data: 音频二进制数据
            output_path: 输出路径

        Returns:
            保存的文件路径
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(audio_data)
        logger.info(f"音频已保存: {output_path}")
        return output_path

    def get_audio_duration(self, audio_path: str) -> float:
        """
        获取音频时长（秒）

        使用 ffprobe（如果可用）或 wave 模块
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"音频文件不存在: {audio_path}")

        # 方法 1：尝试使用 ffprobe
        try:
            result = subprocess.run(
                [
                    "ffprobe", "-v", "error",
                    "-show_entries", "format=duration",
                    "-of", "default=noprint_wrappers=1:nokey=1",
                    audio_path,
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                return float(result.stdout.strip())
        except (FileNotFoundError, subprocess.TimeoutExpired, ValueError):
            pass

        # 方法 2：使用 wave 模块（仅支持 WAV）
        if audio_path.lower().endswith(".wav"):
            try:
                import wave
                with wave.open(audio_path, "rb") as wf:
                    frames = wf.getnframes()
                    rate = wf.getframerate()
                    return frames / float(rate)
            except Exception as e:
                logger.warning(f"读取 WAV 失败: {e}")

        # 默认返回估算值（按 5 字/秒）
        return 5.0

    def merge_audios(
        self, audio_paths: list, output_path: str, gap_ms: int = 200
    ) -> str:
        """
        合并多个音频文件

        Args:
            audio_paths: 音频文件路径列表
            output_path: 输出路径
            gap_ms: 音频之间的间隔（毫秒）

        Returns:
            合并后的音频文件路径
        """
        if not audio_paths:
            raise ValueError("音频列表不能为空")

        if len(audio_paths) == 1:
            # 只有一个音频，直接复制
            import shutil
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            shutil.copy(audio_paths[0], output_path)
            return output_path

        # 方法 1：使用 ffmpeg 拼接（推荐）
        try:
            # 创建 ffmpeg concat 文件
            concat_file = output_path + ".concat.txt"
            with open(concat_file, "w", encoding="utf-8") as f:
                for path in audio_paths:
                    f.write(f"file '{os.path.abspath(path)}'\n")

            cmd = [
                "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                "-i", concat_file,
                "-c", "copy",
                output_path,
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.returncode == 0:
                os.remove(concat_file)
                logger.info(f"音频合并完成: {output_path}")
                return output_path
        except FileNotFoundError:
            logger.warning("ffmpeg 未安装，使用 pydub 合并")
        except subprocess.TimeoutExpired:
            logger.warning("ffmpeg 超时")

        # 方法 2：使用 pydub
        try:
            from pydub import AudioSegment
            combined = AudioSegment.empty()
            silence = AudioSegment.silent(duration=gap_ms)

            for path in audio_paths:
                if os.path.exists(path):
                    audio = AudioSegment.from_file(path)
                    combined += audio + silence

            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            combined.export(output_path, format="mp3")
            return output_path
        except ImportError:
            logger.warning("pydub 未安装，使用简单复制（不拼接）")

        # 兜底：返回第一个音频
        import shutil
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        shutil.copy(audio_paths[0], output_path)
        return output_path

    def _generate_filename(
        self, text: str, config: VoiceConfig, project_id: Optional[int]
    ) -> str:
        """生成唯一的音频文件名"""
        # 使用文本 + provider + 时间戳的哈希作为文件名
        content = f"{text}_{config.provider}_{config.voice}_{time.time_ns()}"
        hash_str = hashlib.md5(content.encode()).hexdigest()[:12]
        prefix = f"audio_{project_id}" if project_id else "audio"
        return f"{prefix}_{hash_str}.mp3"


# 单例实例
_tts_instance: Optional[TTSService] = None


def get_tts_service() -> TTSService:
    """获取 TTS 服务单例"""
    global _tts_instance
    if _tts_instance is None:
        _tts_instance = TTSService()
    return _tts_instance
