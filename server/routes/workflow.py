"""
工作流 API 路由

提供智能体工作流的 CRUD 和操作接口：
- 启动工作流
- 查询状态
- 重做单个阶段
- 重做单个镜头的图像/语音
- 更新镜头数据
- 重新合成视频
- 时间轴数据
- 草稿列表
"""
import os
import json
import logging
import asyncio
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from config.database import get_db
from models.workflow import Workflow, WorkflowPanelHistory
from models.user import User
from services.agent_orchestrator import get_orchestrator
from utils.auth_deps import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/workflow", tags=["智能体工作流"])


# ============ Pydantic Schemas ============

class ModelConfigItem(BaseModel):
    """单个模型配置项"""
    provider: str
    model: str
    voice: Optional[str] = None
    speed: Optional[float] = 1.0
    size: Optional[str] = None


class SubtitleConfigRequest(BaseModel):
    """字幕配置"""
    enabled: bool = True
    position: str = "bottom_center"
    font_size: int = 48
    font_color: str = "#FFFFFF"
    outline_color: str = "#000000"
    outline_width: int = 2
    bold: bool = True
    bg_enabled: bool = True
    bg_color: str = "#00000080"
    animation: str = "none"


class WorkflowStartRequest(BaseModel):
    """启动工作流请求"""
    title: str = Field(..., min_length=1, max_length=200)
    original_prompt: str = Field(..., min_length=10)
    panel_count: int = Field(default=6, ge=2, le=12)
    ratio: str = Field(default="16:9", pattern="^(16:9|9:16|1:1|4:3)$")
    duration: int = Field(default=30, ge=10, le=300)
    character_ids: List[int] = []
    model_config: Dict[str, Any] = {}
    subtitle_config: Optional[SubtitleConfigRequest] = None


class PanelUpdateRequest(BaseModel):
    """更新镜头数据"""
    scene: Optional[str] = None
    camera: Optional[str] = None
    narration: Optional[str] = None
    duration: Optional[float] = None
    subtitle_position: Optional[str] = None
    subject_image_url: Optional[str] = None
    background_image_url: Optional[str] = None
    audio_url: Optional[str] = None


class RecomposeRequest(BaseModel):
    """重新合成视频请求"""
    regenerate_audio: bool = False


# ============ API 接口 ============

@router.post("/start")
async def start_workflow(
    request: WorkflowStartRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    启动工作流（异步）

    创建工作流记录并启动后台任务
    """
    # 余额检查
    if user.balance is None or float(user.balance) < 5.0:
        raise HTTPException(status_code=400, detail="余额不足，请先充值（至少 5 元）")

    # 序列化配置
    subtitle_dict = None
    if request.subtitle_config:
        subtitle_dict = request.subtitle_config.dict()

    # 创建工作流
    workflow = Workflow(
        user_id=user.id,
        title=request.title,
        original_prompt=request.original_prompt,
        panel_count=request.panel_count,
        ratio=request.ratio,
        duration=request.duration,
        character_ids=json.dumps(request.character_ids),
        model_config=json.dumps(request.model_config, ensure_ascii=False),
        subtitle_config=json.dumps(subtitle_dict, ensure_ascii=False) if subtitle_dict else None,
        current_stage="init",
        progress=0,
    )
    db.add(workflow)
    await db.commit()
    await db.refresh(workflow)

    # 初始化 panels（占位）
    panels = []
    per_duration = max(2, request.duration // request.panel_count)
    for i in range(1, request.panel_count + 1):
        panels.append({
            "index": i,
            "scene": "",
            "camera": "中景",
            "characters": [],
            "subject_image_url": None,
            "background_image_url": None,
            "subject_prompt": "",
            "background_prompt": "",
            "narration": "",
            "audio_url": None,
            "duration": per_duration,
            "subtitle_position": "bottom_center",
        })
    workflow.panels = json.dumps(panels, ensure_ascii=False)
    await db.commit()

    # 启动后台任务
    orchestrator = get_orchestrator()

    async def run_workflow():
        await orchestrator.run_workflow(workflow.id)

    background_tasks.add_task(_run_async_task, run_workflow())

    return {
        "code": 200,
        "message": "工作流已启动",
        "data": {
            "workflow_id": workflow.id,
            "current_stage": "init",
            "progress": 0,
        }
    }


def _run_async_task(coro):
    """运行异步任务（用于 BackgroundTasks）"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@router.get("/{workflow_id}/state")
async def get_workflow_state(
    workflow_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取工作流状态"""
    result = await db.execute(
        select(Workflow).where(
            Workflow.id == workflow_id,
            Workflow.user_id == user.id,
        )
    )
    workflow = result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=404, detail="工作流不存在")

    panels = json.loads(workflow.panels) if workflow.panels else []

    return {
        "code": 200,
        "message": "success",
        "data": {
            "id": workflow.id,
            "title": workflow.title,
            "original_prompt": workflow.original_prompt,
            "current_stage": workflow.current_stage,
            "progress": workflow.progress,
            "current_step": workflow.current_step,
            "panels": panels,
            "video_url": workflow.video_url,
            "thumbnail_url": workflow.thumbnail_url,
            "error_message": workflow.error_message,
            "created_at": workflow.created_at.isoformat() if workflow.created_at else "",
            "updated_at": workflow.updated_at.isoformat() if workflow.updated_at else "",
        }
    }


@router.get("/drafts")
async def list_drafts(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """列出我的草稿"""
    query = select(Workflow).where(Workflow.user_id == user.id)
    query = query.order_by(desc(Workflow.updated_at))
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    workflows = result.scalars().all()

    items = []
    for w in workflows:
        # 解析 panels 数量
        panels_count = 0
        if w.panels:
            try:
                panels = json.loads(w.panels)
                panels_count = len(panels)
            except json.JSONDecodeError:
                pass

        items.append({
            "id": w.id,
            "title": w.title,
            "current_stage": w.current_stage,
            "progress": w.progress,
            "panels_count": panels_count,
            "ratio": w.ratio,
            "video_url": w.video_url,
            "thumbnail_url": w.thumbnail_url,
            "updated_at": w.updated_at.isoformat() if w.updated_at else "",
        })

    return {
        "code": 200,
        "message": "success",
        "data": {
            "items": items,
            "page": page,
            "page_size": page_size,
        }
    }


@router.post("/{workflow_id}/panel/{panel_idx}/regenerate-image")
async def regenerate_panel_image(
    workflow_id: int,
    panel_idx: int,
    image_type: str = Query(default="both", pattern="^(subject|background|both)$"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """重新生成某个镜头的图像"""
    # 验证所有权
    result = await db.execute(
        select(Workflow).where(
            Workflow.id == workflow_id,
            Workflow.user_id == user.id,
        )
    )
    workflow = result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=404, detail="工作流不存在")

    orchestrator = get_orchestrator()
    result = await orchestrator.run_regenerate_panel_image(
        workflow_id=workflow_id,
        panel_index=panel_idx,
        image_type=image_type,
    )

    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "重做失败"))

    return {
        "code": 200,
        "message": "success",
        "data": result,
    }


@router.post("/{workflow_id}/panel/{panel_idx}/regenerate-voice")
async def regenerate_panel_voice(
    workflow_id: int,
    panel_idx: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """重新生成某个镜头的语音"""
    result = await db.execute(
        select(Workflow).where(
            Workflow.id == workflow_id,
            Workflow.user_id == user.id,
        )
    )
    workflow = result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=404, detail="工作流不存在")

    orchestrator = get_orchestrator()
    result = await orchestrator.run_regenerate_panel_voice(
        workflow_id=workflow_id,
        panel_index=panel_idx,
    )

    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "重做失败"))

    return {"code": 200, "message": "success", "data": result}


@router.put("/{workflow_id}/panel/{panel_idx}")
async def update_panel(
    workflow_id: int,
    panel_idx: int,
    request: PanelUpdateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新某个镜头的字段"""
    result = await db.execute(
        select(Workflow).where(
            Workflow.id == workflow_id,
            Workflow.user_id == user.id,
        )
    )
    workflow = result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=404, detail="工作流不存在")

    # 解析 panels
    panels = json.loads(workflow.panels) if workflow.panels else []
    if panel_idx < 1 or panel_idx > len(panels):
        raise HTTPException(status_code=400, detail="镜头索引无效")

    # 更新字段
    panel = panels[panel_idx - 1]
    update_data = request.dict(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            panel[key] = value

    workflow.panels = json.dumps(panels, ensure_ascii=False)
    await db.commit()

    return {
        "code": 200,
        "message": "success",
        "data": {
            "panel_index": panel_idx,
            "panel": panel,
        }
    }


@router.post("/{workflow_id}/recompose")
async def recompose_video(
    workflow_id: int,
    request: RecomposeRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """重新合成视频（不重新生成图像和语音）"""
    result = await db.execute(
        select(Workflow).where(
            Workflow.id == workflow_id,
            Workflow.user_id == user.id,
        )
    )
    workflow = result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=404, detail="工作流不存在")

    orchestrator = get_orchestrator()
    result = await orchestrator.run_recompose(workflow_id=workflow_id)

    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "合成失败"))

    return {"code": 200, "message": "success", "data": result}


@router.get("/{workflow_id}/timeline")
async def get_timeline(
    workflow_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取时间轴数据"""
    result = await db.execute(
        select(Workflow).where(
            Workflow.id == workflow_id,
            Workflow.user_id == user.id,
        )
    )
    workflow = result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=404, detail="工作流不存在")

    panels = json.loads(workflow.panels) if workflow.panels else []

    # 构造时间轴
    timeline = []
    current_time = 0.0
    for panel in panels:
        duration = float(panel.get("duration", 5))
        timeline.append({
            "panel_index": panel.get("index"),
            "start_time": current_time,
            "end_time": current_time + duration,
            "duration": duration,
            "scene": panel.get("scene", ""),
            "narration": panel.get("narration", ""),
            "subject_image_url": panel.get("subject_image_url"),
            "background_image_url": panel.get("background_image_url"),
            "audio_url": panel.get("audio_url"),
            "subtitle_position": panel.get("subtitle_position", "bottom_center"),
        })
        current_time += duration

    return {
        "code": 200,
        "message": "success",
        "data": {
            "workflow_id": workflow_id,
            "total_duration": current_time,
            "ratio": workflow.ratio,
            "timeline": timeline,
            "video_url": workflow.video_url,
        }
    }


@router.delete("/{workflow_id}")
async def delete_workflow(
    workflow_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除工作流"""
    result = await db.execute(
        select(Workflow).where(
            Workflow.id == workflow_id,
            Workflow.user_id == user.id,
        )
    )
    workflow = result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=404, detail="工作流不存在")

    # 删除相关文件
    if workflow.video_url:
        file_path = workflow.video_url.lstrip("/")
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                pass

    # 删除历史记录
    await db.execute(
        WorkflowPanelHistory.__table__.delete().where(
            WorkflowPanelHistory.workflow_id == workflow_id
        )
    )

    await db.delete(workflow)
    await db.commit()

    return {"code": 200, "message": "删除成功", "data": None}
