"""
模型调用服务

封装对各种 AI 模型的实时调用，供业务层使用。
- 文本生成（生成剧本、故事描述等）
- 图像生成（生成漫画、视频帧等）
- 视觉理解（理解上传的图像）

使用 ModelAdapter 统一接口，支持多种 provider。
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from services.model_adapter import ModelAdapter, ModelConfig
from services.llm_client import ImageGenResponse, TextCompletionResponse

logger = logging.getLogger(__name__)


# ============ Pydantic Models ============

class ScriptGenRequest(BaseModel):
    """剧本生成请求"""
    prompt: str = Field(..., min_length=1)
    duration: int = Field(default=30, ge=10, le=300)
    panel_count: int = Field(default=6, ge=2, le=20)
    characters: List[Dict[str, Any]] = Field(default_factory=list)
    style: str = Field(default="cinematic")
    language: str = Field(default="zh-CN")


class ScriptGenResponse(BaseModel):
    """剧本生成响应"""
    panels: List[Dict[str, Any]] = Field(default_factory=list)
    title: Optional[str] = None
    summary: Optional[str] = None
    total_duration: int = 0


# ============ 服务 ============

class ModelService:
    """
    模型调用服务

    为上层业务提供：
    - 剧本生成
    - 图像生成
    - 图像理解
    - 文本生成
    """

    def __init__(self):
        """初始化"""
        logger.info("ModelService 初始化")

    def _create_adapter(
        self,
        provider: str,
        model: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> ModelAdapter:
        """
        创建模型适配器

        优先级：传入参数 > 数据库配置 > 环境变量
        """
        # 如果有显式传入，使用它们
        if api_key and base_url:
            return ModelAdapter(ModelConfig(
                provider=provider,
                model=model,
                api_key=api_key,
                base_url=base_url,
            ))

        # 否则从环境变量创建
        return ModelAdapter.from_env(provider, model)

    async def generate_script(
        self,
        request: ScriptGenRequest,
        provider: str = "minimax",
        model: str = "minimax-text-01",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> ScriptGenResponse:
        """
        生成分镜剧本

        Args:
            request: 剧本生成请求
            provider: 文本模型提供商
            model: 文本模型名称
            api_key: API Key
            base_url: 自定义端点

        Returns:
            剧本响应
        """
        adapter = self._create_adapter(provider, model, api_key, base_url)

        # 构造角色描述
        char_desc = ""
        if request.characters:
            char_desc = "\n\n可用角色：\n"
            for ch in request.characters:
                char_desc += f"- 角色 ID {ch.get('id', 0)}: {ch.get('name', '未知')}\n"
                char_desc += f"  描述: {ch.get('description', '无')}\n"

        # 构造提示词
        system_prompt = f"""你是一个专业的视频分镜编剧，擅长将文字描述转换为结构化的分镜剧本。
输出必须是严格的 JSON 格式，不要包含任何解释文字。
剧本风格：{request.style}
语言：{request.language}"""

        user_prompt = f"""请根据以下描述创作视频分镜剧本：

主题：{request.prompt}

参数：
- 总时长：{request.duration} 秒
- 分镜数量：{request.panel_count} 个
- 每个分镜约 {request.duration // request.panel_count} 秒
{char_desc}

输出 JSON 格式：
{{
  "title": "视频标题",
  "summary": "剧情简介",
  "panels": [
    {{
      "index": 1,
      "scene": "详细的画面描述（用于生成图像）",
      "narration": "旁白/对白文字（用作字幕）",
      "character_id": 0,
      "duration": 5,
      "camera": "镜头类型：远景/中景/近景/特写"
    }}
  ]
}}

要求：
1. 所有 panels 的 duration 之和 = {request.duration}
2. scene 描述要详细、生动，包含场景、氛围、人物动作
3. narration 简洁有感染力，单个分镜不超过 50 字
4. character_id 为 0 表示无角色，否则使用上面提供的角色 ID"""

        try:
            data = await adapter.generate_json(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.8,
                max_tokens=4000,
            )

            panels = data.get("panels", [])
            total_duration = sum(p.get("duration", 0) for p in panels)

            return ScriptGenResponse(
                panels=panels,
                title=data.get("title"),
                summary=data.get("summary"),
                total_duration=total_duration,
            )
        except Exception as e:
            logger.error(f"剧本生成失败: {e}")
            # 兜底：返回空响应
            return ScriptGenResponse(panels=[], title=None, summary=str(e))

    async def generate_image(
        self,
        prompt: str,
        provider: str = "minimax",
        model: str = "minimax-image-01",
        size: str = "1024x1024",
        n: int = 1,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> ImageGenResponse:
        """
        生成图像

        Args:
            prompt: 图像描述
            provider: 图像模型提供商
            model: 图像模型名称
            size: 图像尺寸
            n: 生成数量

        Returns:
            图像响应
        """
        adapter = self._create_adapter(provider, model, api_key, base_url)
        return await adapter.generate_image(
            prompt=prompt,
            size=size,
            n=n,
        )

    async def generate_storyboard_images(
        self,
        panels: List[Dict[str, Any]],
        style: str = "cinematic",
        provider: str = "minimax",
        model: str = "minimax-image-01",
        size: str = "1024x1024",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> List[str]:
        """
        为分镜批量生成图像

        Args:
            panels: 分镜列表
            style: 风格
            provider/model: 图像模型
            size: 尺寸

        Returns:
            图像 URL 列表
        """
        adapter = self._create_adapter(provider, model, api_key, base_url)

        urls = []
        for panel in panels:
            scene = panel.get("scene", "")
            if not scene:
                urls.append("")
                continue

            # 构造图像 prompt
            full_prompt = f"{style} 风格，{scene}，高质量，细腻，富有表现力"

            try:
                response = await adapter.generate_image(
                    prompt=full_prompt,
                    size=size,
                )
                if response.urls:
                    urls.append(response.urls[0])
                else:
                    urls.append("")
            except Exception as e:
                logger.error(f"生成图像失败 (panel {panel.get('index')}): {e}")
                urls.append("")

        return urls

    async def text_completion(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        provider: str = "minimax",
        model: str = "minimax-text-01",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> str:
        """
        通用文本补全

        Args:
            prompt: 提示词
            system_prompt: 系统提示词
            provider/model: 文本模型
            temperature: 温度

        Returns:
            生成的文本
        """
        adapter = self._create_adapter(provider, model, api_key, base_url)
        return await adapter.generate_text(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    async def analyze_image(
        self,
        image_url: str,
        prompt: str = "请详细描述这张图片的内容",
        provider: str = "minimax",
        model: str = "minimax-vl-01",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> str:
        """
        分析图像

        Args:
            image_url: 图像 URL
            prompt: 提示词
            provider/model: 视觉模型

        Returns:
            描述文本
        """
        adapter = self._create_adapter(provider, model, api_key, base_url)
        return await adapter.analyze_image(image_url=image_url, prompt=prompt)


# ============ 单例 ============

_service_instance: Optional[ModelService] = None


def get_model_service() -> ModelService:
    """获取模型服务单例"""
    global _service_instance
    if _service_instance is None:
        _service_instance = ModelService()
    return _service_instance
