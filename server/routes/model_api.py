"""
模型调用 API 路由

提供实时的 AI 模型调用接口（无需等待视频生成）：
- POST /api/model/chat - 文本对话
- POST /api/model/image - 图像生成
- POST /api/model/script - 生成剧本
- POST /api/model/analyze-image - 图像理解
- GET  /api/model/providers - 列出可用 provider 和模型
- GET  /api/model/health - 健康检查
"""
import json
import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from models.user import User
from services.model_service import (
    ModelService,
    ScriptGenRequest,
    ScriptGenResponse,
    get_model_service,
)
from services.model_adapter import ModelAdapter
from services.minimax_client import MiniMaxClient
from services.llm_client import PROVIDER_CONFIGS
from utils.auth_deps import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/model", tags=["模型调用"])


# ============ Pydantic Schemas ============

class ChatRequest(BaseModel):
    """文本对话请求"""
    prompt: str = Field(..., min_length=1, max_length=32000)
    system_prompt: Optional[str] = Field(default=None, max_length=4000)
    provider: str = Field(default="minimax")
    model: Optional[str] = None
    temperature: float = Field(default=0.7, ge=0, le=2)
    max_tokens: Optional[int] = Field(default=None, ge=1, le=8192)
    response_format: Optional[dict] = None


class ImageGenApiRequest(BaseModel):
    """图像生成 API 请求"""
    prompt: str = Field(..., min_length=1, max_length=4000)
    negative_prompt: Optional[str] = None
    provider: str = Field(default="minimax")
    model: Optional[str] = None
    size: str = Field(default="1024x1024")
    n: int = Field(default=1, ge=1, le=4)


class ScriptGenApiRequest(BaseModel):
    """剧本生成 API 请求"""
    prompt: str = Field(..., min_length=1, max_length=4000)
    duration: int = Field(default=30, ge=10, le=300)
    panel_count: int = Field(default=6, ge=2, le=20)
    characters: List[dict] = Field(default_factory=list)
    style: str = Field(default="cinematic")
    language: str = Field(default="zh-CN")
    provider: str = Field(default="minimax")
    model: Optional[str] = None


class AnalyzeImageRequest(BaseModel):
    """图像分析请求"""
    image_url: str = Field(..., min_length=1)
    prompt: str = Field(default="请详细描述这张图片的内容")
    provider: str = Field(default="minimax")
    model: Optional[str] = None


# ============ API 接口 ============

@router.get("/providers")
async def list_providers():
    """
    列出所有可用的 provider 和模型
    """
    return {
        "code": 200,
        "message": "success",
        "data": {
            "providers": PROVIDER_CONFIGS,
        }
    }


@router.get("/models")
async def list_models(provider: Optional[str] = None, model_type: Optional[str] = None):
    """
    列出模型
    """
    if provider == "minimax":
        models = MiniMaxClient.list_supported_models(model_type)
    else:
        models = []
    return {
        "code": 200,
        "message": "success",
        "data": {
            "provider": provider,
            "type": model_type,
            "models": models,
        }
    }


@router.post("/chat")
async def chat_completion(
    request: ChatRequest,
    user: User = Depends(get_current_user),
):
    """
    实时文本对话

    支持 MiniMax、OpenAI、通义千问等（OpenAI 兼容格式）
    """
    service = get_model_service()

    # 确定模型名称
    model = request.model
    if not model:
        # 使用 provider 默认模型
        defaults = {
            "minimax": "minimax-text-01",
            "openai": "gpt-3.5-turbo",
            "qwen": "qwen-turbo",
        }
        model = defaults.get(request.provider, "minimax-text-01")

    try:
        content = await service.text_completion(
            prompt=request.prompt,
            system_prompt=request.system_prompt,
            provider=request.provider,
            model=model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        return {
            "code": 200,
            "message": "success",
            "data": {
                "content": content,
                "model": model,
                "provider": request.provider,
            }
        }
    except Exception as e:
        logger.error(f"文本生成失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"文本生成失败: {str(e)}"
        )


@router.post("/image")
async def generate_image_api(
    request: ImageGenApiRequest,
    user: User = Depends(get_current_user),
):
    """
    实时图像生成

    默认使用 MiniMax 图像模型，可通过参数切换 provider
    """
    service = get_model_service()

    # 确定模型
    model = request.model or "minimax-image-01"

    try:
        # 合并 prompt 和 negative_prompt
        full_prompt = request.prompt
        if request.negative_prompt:
            full_prompt = f"{request.prompt}\n负面: {request.negative_prompt}"

        response = await service.generate_image(
            prompt=full_prompt,
            provider=request.provider,
            model=model,
            size=request.size,
            n=request.n,
        )

        return {
            "code": 200,
            "message": "success",
            "data": {
                "urls": response.urls,
                "b64_json": response.b64_json,
                "model": response.model or model,
                "revised_prompt": response.revised_prompt,
            }
        }
    except Exception as e:
        logger.error(f"图像生成失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"图像生成失败: {str(e)}"
        )


@router.post("/script")
async def generate_script_api(
    request: ScriptGenApiRequest,
    user: User = Depends(get_current_user),
):
    """
    生成视频分镜剧本
    """
    service = get_model_service()

    model = request.model or "minimax-text-01"

    try:
        script_request = ScriptGenRequest(
            prompt=request.prompt,
            duration=request.duration,
            panel_count=request.panel_count,
            characters=request.characters,
            style=request.style,
            language=request.language,
        )

        response = await service.generate_script(
            request=script_request,
            provider=request.provider,
            model=model,
        )

        return {
            "code": 200,
            "message": "success",
            "data": response.dict()
        }
    except Exception as e:
        logger.error(f"剧本生成失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"剧本生成失败: {str(e)}"
        )


@router.post("/analyze-image")
async def analyze_image_api(
    request: AnalyzeImageRequest,
    user: User = Depends(get_current_user),
):
    """
    图像理解
    """
    service = get_model_service()

    model = request.model or "minimax-vl-01"

    try:
        content = await service.analyze_image(
            image_url=request.image_url,
            prompt=request.prompt,
            provider=request.provider,
            model=model,
        )

        return {
            "code": 200,
            "message": "success",
            "data": {
                "content": content,
                "model": model,
            }
        }
    except Exception as e:
        logger.error(f"图像分析失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"图像分析失败: {str(e)}"
        )


@router.get("/health")
async def health_check(
    provider: str = "minimax",
    user: User = Depends(get_current_user),
):
    """
    健康检查（验证 provider 是否可用）
    """
    try:
        adapter = ModelAdapter.from_env(provider, "minimax-text-01")
        available = await adapter.health_check()

        return {
            "code": 200,
            "message": "success",
            "data": {
                "provider": provider,
                "available": available,
            }
        }
    except Exception as e:
        return {
            "code": 200,
            "message": "success",
            "data": {
                "provider": provider,
                "available": False,
                "error": str(e),
            }
        }
