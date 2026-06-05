"""
视频项目路由

提供视频项目的 CRUD、生成、状态查询、下载等接口。
"""
import os
import json
import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from config.database import get_db
from models.video_project import VideoProject
from models.user import User
from services.subtitle_renderer import SubtitleConfig
from services.video_pipeline import get_video_pipeline
from utils.auth_deps import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/video", tags=["视频生成"])


# ============ Pydantic Schemas ============

class SubtitleConfigRequest(BaseModel):
    """字幕配置请求"""
    enabled: bool = True
    position: str = "bottom_center"
    font_size: int = 48
    font_color: str = "#FFFFFF"
    outline_color: str = "#000000"
    outline_width: int = 2
    bold: bool = True
    bg_enabled: bool = True
    bg_color: str = "#00000080"
    margin_top: int = 30
    margin_horizontal: int = 30
    animation: str = "none"


class ModelConfigItem(BaseModel):
    """单个模型配置项"""
    provider: str
    model: str
    config_id: Optional[int] = None


class VideoGenerateRequest(BaseModel):
    """视频生成请求"""
    title: str = Field(..., min_length=1, max_length=200)
    script_prompt: str = Field(..., min_length=10)
    ratio: str = Field(default="16:9", pattern="^(16:9|9:16|1:1|4:3)$")
    duration: int = Field(default=30, ge=10, le=300)
    character_ids: list = []
    model_config: dict = {}
    subtitle_config: Optional[SubtitleConfigRequest] = None


class VideoProjectInfo(BaseModel):
    """视频项目信息（响应）"""
    id: int
    title: str
    status: str
    progress: int
    current_step: Optional[str]
    ratio: str
    duration: int
    video_url: Optional[str]
    thumbnail_url: Optional[str]
    error_message: Optional[str]
    cost: float
    created_at: str
    updated_at: str


# ============ 预设数据 ============

SUBTITLE_PRESETS = [
    {
        "id": "default",
        "name": "通用默认",
        "description": "白字黑边 + 半透明背景",
        "config": {
            "enabled": True,
            "position": "bottom_center",
            "font_size": 48,
            "font_color": "#FFFFFF",
            "outline_color": "#000000",
            "outline_width": 2,
            "bg_enabled": True,
            "bg_color": "#00000080",
        }
    },
    {
        "id": "cinema",
        "name": "电影风格",
        "description": "大号白字 + 黑色描边",
        "config": {
            "enabled": True,
            "position": "bottom_center",
            "font_size": 56,
            "font_color": "#FFFFFF",
            "outline_color": "#000000",
            "outline_width": 3,
            "bg_enabled": False,
        }
    },
    {
        "id": "news",
        "name": "新闻风格",
        "description": "小号白字 + 蓝色条带",
        "config": {
            "enabled": True,
            "position": "bottom_center",
            "font_size": 40,
            "font_color": "#FFFFFF",
            "outline_color": "#000000",
            "outline_width": 1,
            "bg_enabled": True,
            "bg_color": "#1E3A8ACC",
        }
    },
    {
        "id": "lyric",
        "name": "歌词风格",
        "description": "居中 + 黄色字",
        "config": {
            "enabled": True,
            "position": "middle_center",
            "font_size": 52,
            "font_color": "#FFEB3B",
            "outline_color": "#000000",
            "outline_width": 2,
            "bg_enabled": False,
        }
    },
    {
        "id": "kawaii",
        "name": "二次元",
        "description": "圆体 + 粉色描边",
        "config": {
            "enabled": True,
            "position": "bottom_center",
            "font_size": 46,
            "font_color": "#FFFFFF",
            "outline_color": "#FF69B4",
            "outline_width": 3,
            "bg_enabled": True,
            "bg_color": "#00000080",
        }
    },
]


# ============ API 接口 ============

@router.post("/generate")
async def generate_video(
    request: VideoGenerateRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    启动视频生成（异步任务）

    流程：
    1. 创建 VideoProject 记录
    2. 启动后台任务执行 VideoPipeline
    3. 立即返回 project_id，前端可轮询状态
    """
    # 余额检查
    if user.balance is None or float(user.balance) < 10.0:
        raise HTTPException(status_code=400, detail="余额不足，请先充值（至少需要 10 元）")

    # 创建项目
    subtitle_dict = None
    if request.subtitle_config:
        subtitle_dict = request.subtitle_config.dict()

    project = VideoProject(
        user_id=user.id,
        title=request.title,
        script_prompt=request.script_prompt,
        ratio=request.ratio,
        duration=request.duration,
        character_ids=json.dumps(request.character_ids),
        model_config=json.dumps(request.model_config, ensure_ascii=False),
        subtitle_config=json.dumps(subtitle_dict, ensure_ascii=False) if subtitle_dict else None,
        status="pending",
        progress=0,
    )

    db.add(project)
    await db.commit()
    await db.refresh(project)

    # 启动后台任务
    pipeline = get_video_pipeline()

    async def run_pipeline():
        await pipeline.run(project.id)

    background_tasks.add_task(asyncio_task, run_pipeline())

    return {
        "code": 200,
        "message": "视频生成任务已启动",
        "data": {
            "project_id": project.id,
            "status": "pending",
            "estimated_time": request.duration * 2,  # 估算：每秒 2 倍生成时间
        }
    }


def asyncio_task(coro):
    """简单的异步任务运行器（用于 BackgroundTasks）"""
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@router.get("/projects")
async def list_projects(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),
    status: Optional[str] = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """列出我的视频项目"""
    query = select(VideoProject).where(VideoProject.user_id == user.id)
    if status:
        query = query.where(VideoProject.status == status)
    query = query.order_by(desc(VideoProject.created_at))
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    projects = result.scalars().all()

    items = [
        VideoProjectInfo(
            id=p.id,
            title=p.title,
            status=p.status,
            progress=p.progress,
            current_step=p.current_step,
            ratio=p.ratio,
            duration=p.duration,
            video_url=p.video_url,
            thumbnail_url=p.thumbnail_url,
            error_message=p.error_message,
            cost=float(p.cost),
            created_at=p.created_at.isoformat() if p.created_at else "",
            updated_at=p.updated_at.isoformat() if p.updated_at else "",
        )
        for p in projects
    ]

    return {
        "code": 200,
        "message": "success",
        "data": {
            "items": [item.dict() for item in items],
            "page": page,
            "page_size": page_size,
        }
    }


@router.get("/projects/{project_id}")
async def get_project(
    project_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取项目详情"""
    result = await db.execute(
        select(VideoProject).where(
            VideoProject.id == project_id,
            VideoProject.user_id == user.id,
        )
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    return {
        "code": 200,
        "message": "success",
        "data": {
            "id": project.id,
            "title": project.title,
            "script_prompt": project.script_prompt,
            "status": project.status,
            "progress": project.progress,
            "current_step": project.current_step,
            "ratio": project.ratio,
            "duration": project.duration,
            "character_ids": json.loads(project.character_ids) if project.character_ids else [],
            "model_config": json.loads(project.model_config) if project.model_config else {},
            "storyboard": json.loads(project.storyboard) if project.storyboard else None,
            "subtitle_config": json.loads(project.subtitle_config) if project.subtitle_config else None,
            "video_url": project.video_url,
            "thumbnail_url": project.thumbnail_url,
            "error_message": project.error_message,
            "cost": float(project.cost),
            "created_at": project.created_at.isoformat() if project.created_at else "",
            "updated_at": project.updated_at.isoformat() if project.updated_at else "",
        }
    }


@router.get("/projects/{project_id}/status")
async def get_project_status(
    project_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """查询生成状态（轻量接口，用于轮询）"""
    result = await db.execute(
        select(VideoProject).where(
            VideoProject.id == project_id,
            VideoProject.user_id == user.id,
        )
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    return {
        "code": 200,
        "message": "success",
        "data": {
            "project_id": project.id,
            "status": project.status,
            "progress": project.progress,
            "current_step": project.current_step,
            "video_url": project.video_url,
            "thumbnail_url": project.thumbnail_url,
            "error_message": project.error_message,
        }
    }


@router.delete("/projects/{project_id}")
async def delete_project(
    project_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除项目"""
    result = await db.execute(
        select(VideoProject).where(
            VideoProject.id == project_id,
            VideoProject.user_id == user.id,
        )
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    # 删除文件
    if project.video_url:
        file_path = project.video_url.lstrip("/")
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                pass

    await db.delete(project)
    await db.commit()

    return {"code": 200, "message": "删除成功", "data": None}


@router.get("/projects/{project_id}/download")
async def download_video(
    project_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """下载视频文件"""
    result = await db.execute(
        select(VideoProject).where(
            VideoProject.id == project_id,
            VideoProject.user_id == user.id,
        )
    )
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    if not project.video_url:
        raise HTTPException(status_code=400, detail="视频尚未生成")

    if project.status != "completed":
        raise HTTPException(status_code=400, detail="视频未完成生成")

    # 构造文件路径
    file_path = project.video_url.lstrip("/")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="视频文件不存在")

    return FileResponse(
        path=file_path,
        media_type="video/mp4",
        filename=f"{project.title}.mp4",
    )


@router.get("/subtitle-presets")
async def get_subtitle_presets():
    """获取字幕预设列表"""
    return {
        "code": 200,
        "message": "success",
        "data": SUBTITLE_PRESETS
    }


@router.post("/preview-subtitle")
async def preview_subtitle(
    config: SubtitleConfigRequest,
    text: str = Query(..., min_length=1, max_length=200),
    user: User = Depends(get_current_user),
):
    """
    生成字幕预览图（用占位图 + 字幕烧录）

    返回带字幕的预览图（Base64 或 URL）
    """
    from services.subtitle_renderer import get_subtitle_renderer, SubtitleConfig
    from PIL import Image, ImageDraw
    import io
    import base64

    # 创建占位图
    img = Image.new("RGB", (1920, 1080), (40, 60, 100))
    draw = ImageDraw.Draw(img)
    draw.text((100, 100), "Preview Background", fill=(200, 200, 200))

    # 渲染字幕
    subtitle_config = SubtitleConfig(**config.dict())
    renderer = get_subtitle_renderer()
    result_img = renderer.render_subtitle_on_frame(
        image=img, text=text, config=subtitle_config
    )

    # 保存到预览目录
    preview_dir = "static/previews"
    os.makedirs(preview_dir, exist_ok=True)
    preview_path = os.path.join(preview_dir, f"preview_{user.id}_{int(__import__('time').time())}.jpg")
    result_img.convert("RGB").save(preview_path, quality=85)

    return {
        "code": 200,
        "message": "success",
        "data": {
            "preview_url": f"/{preview_path}",
        }
    }
