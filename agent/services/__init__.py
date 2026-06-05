"""
Agent 中台服务层
"""
from .backend_client import backend_client
from .data_analyzer import data_analyzer
from .agents import (
    ComicCreatorAgent,
    ImageGeneratorAgent,
    TextWriterAgent,
    VoiceDirectorAgent,
    MusicComposerAgent,
    CommunityModeratorAgent,
)

# 注册所有 Agent 类
from ..core.agent_registry import registry

registry.register_class("comic_creator", ComicCreatorAgent)
registry.register_class("image_generator", ImageGeneratorAgent)
registry.register_class("text_writer", TextWriterAgent)
registry.register_class("voice_director", VoiceDirectorAgent)
registry.register_class("music_composer", MusicComposerAgent)
registry.register_class("community_moderator", CommunityModeratorAgent)


__all__ = [
    "backend_client",
    "data_analyzer",
    "ComicCreatorAgent",
    "ImageGeneratorAgent",
    "TextWriterAgent",
    "VoiceDirectorAgent",
    "MusicComposerAgent",
    "CommunityModeratorAgent",
    "registry",
]
