"""
语音合成历史路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from config.database import get_db
from models.user import User
from models.voice_history import VoiceHistory
from utils.auth_deps import get_current_user

router = APIRouter(prefix="/voice-history", tags=["语音合成"])


@router.post("/")
async def add_voice_history(
    text: str,
    voice_type: str = "zh-CN-Wavenet-A",
    speed: float = 1.0,
    pitch: float = 1.0,
    audio_url: str = "",
    duration: int = 0,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """添加语音合成记录"""
    history = VoiceHistory(
        user_id=user.id,
        text=text,
        voice_type=voice_type,
        speed=speed,
        pitch=pitch,
        audio_url=audio_url,
        duration=duration,
        status="SUCCESS"
    )
    
    db.add(history)
    await db.commit()
    await db.refresh(history)
    
    return {
        "code": 200,
        "message": "记录成功",
        "data": {
            "id": history.id,
            "text": history.text,
            "audio_url": history.audio_url,
            "created_at": history.created_at.isoformat()
        }
    }


@router.get("/")
async def get_voice_history(
    page: int = 1,
    page_size: int = 20,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取语音合成历史"""
    offset = (page - 1) * page_size
    result = await db.execute(
        select(VoiceHistory)
        .where(VoiceHistory.user_id == user.id)
        .order_by(VoiceHistory.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    histories = result.scalars().all()
    
    return {
        "code": 200,
        "message": "success",
        "data": [{
            "id": history.id,
            "text": history.text,
            "voice_type": history.voice_type,
            "speed": float(history.speed),
            "pitch": float(history.pitch),
            "audio_url": history.audio_url,
            "duration": history.duration,
            "created_at": history.created_at.isoformat()
        } for history in histories]
    }


@router.delete("/{history_id}")
async def delete_voice_history(
    history_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除语音合成记录"""
    history = await db.get(VoiceHistory, history_id)
    if not history:
        raise HTTPException(status_code=404, detail="记录不存在")
    
    if history.user_id != user.id and user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="无权操作")
    
    await db.delete(history)
    await db.commit()
    
    return {
        "code": 200,
        "message": "删除成功"
    }
