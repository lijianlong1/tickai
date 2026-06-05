"""
角色管理路由

管理角色库：列出可见角色（系统 + 用户）、创建、更新、删除用户角色。
启动时预置 5 个系统角色。
"""
import os
import json
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from config.database import get_db
from models.character import Character
from models.user import User
from utils.auth_deps import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/characters", tags=["角色管理"])


# ============ 系统预置角色 ============

SYSTEM_CHARACTERS = [
    {
        "name": "少年",
        "description": "一个充满朝气的少年，约 16 岁，有黑色短发和明亮的眼睛。性格勇敢、好奇、善良。穿着简单的 T 恤和牛仔裤。",
        "avatar": "👦",
        "color": "#3B82F6",
    },
    {
        "name": "少女",
        "description": "一个温柔的少女，约 15 岁，有长长的棕色头发和大大的眼睛。性格温柔、聪明、富有想象力。穿着白色连衣裙。",
        "avatar": "👧",
        "color": "#EC4899",
    },
    {
        "name": "老人",
        "description": "一位慈祥的老人，约 70 岁，满头白发，留着白胡须。性格睿智、幽默、富有耐心。穿着传统的中式长衫。",
        "avatar": "👴",
        "color": "#6B7280",
    },
    {
        "name": "狐狸",
        "description": "一只神奇的狐狸，毛色火红，眼睛闪着灵光。会说人话，聪明机灵，富有灵性。",
        "avatar": "🦊",
        "color": "#F97316",
    },
    {
        "name": "机器人",
        "description": "一个友善的机器人助手，外表光滑闪亮，蓝色眼睛。性格理性、乐于助人、富有逻辑。",
        "avatar": "🤖",
        "color": "#06B6D4",
    },
]


# ============ Pydantic Schemas ============

class CharacterCreate(BaseModel):
    """创建角色"""
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1)
    reference_image: Optional[str] = None
    voice_config: Optional[dict] = None
    avatar: Optional[str] = Field(default=None, max_length=10)
    color: Optional[str] = Field(default=None, max_length=20)
    is_public: bool = True


class CharacterUpdate(BaseModel):
    """更新角色"""
    name: Optional[str] = None
    description: Optional[str] = None
    reference_image: Optional[str] = None
    voice_config: Optional[dict] = None
    avatar: Optional[str] = None
    color: Optional[str] = None
    is_public: Optional[bool] = None


class CharacterInfo(BaseModel):
    """角色信息（响应）"""
    id: int
    user_id: Optional[int]
    name: str
    description: str
    reference_image: Optional[str]
    voice_config: Optional[dict]
    avatar: Optional[str]
    color: Optional[str]
    is_public: bool
    is_system: bool
    created_at: str
    updated_at: str


# ============ API 接口 ============

@router.get("")
async def list_characters(
    keyword: Optional[str] = Query(default=None, description="搜索关键词"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """列出可见角色（系统 + 我的 + 公开的）"""
    query = select(Character).where(
        or_(
            Character.user_id == None,  # 系统预置
            Character.user_id == user.id,  # 我的
            Character.is_public == True,  # 公开的
        )
    )

    if keyword:
        query = query.where(
            or_(
                Character.name.like(f"%{keyword}%"),
                Character.description.like(f"%{keyword}%"),
            )
        )

    query = query.order_by(Character.user_id.is_(None).desc(), Character.id.asc())

    result = await db.execute(query)
    characters = result.scalars().all()

    items = []
    for c in characters:
        voice_cfg = None
        if c.voice_config:
            try:
                voice_cfg = json.loads(c.voice_config)
            except json.JSONDecodeError:
                pass

        items.append(CharacterInfo(
            id=c.id,
            user_id=c.user_id,
            name=c.name,
            description=c.description,
            reference_image=c.reference_image,
            voice_config=voice_cfg,
            avatar=c.avatar,
            color=c.color,
            is_public=c.is_public,
            is_system=c.user_id is None,
            created_at=c.created_at.isoformat() if c.created_at else "",
            updated_at=c.updated_at.isoformat() if c.updated_at else "",
        ))

    return {
        "code": 200,
        "message": "success",
        "data": {
            "items": [item.dict() for item in items]
        }
    }


@router.post("")
async def create_character(
    request: CharacterCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建角色"""
    character = Character(
        user_id=user.id,
        name=request.name,
        description=request.description,
        reference_image=request.reference_image,
        voice_config=json.dumps(request.voice_config) if request.voice_config else None,
        avatar=request.avatar,
        color=request.color,
        is_public=request.is_public,
    )

    db.add(character)
    await db.commit()
    await db.refresh(character)

    return {
        "code": 200,
        "message": "角色创建成功",
        "data": {
            "id": character.id,
            "name": character.name,
        }
    }


@router.put("/{character_id}")
async def update_character(
    character_id: int,
    request: CharacterUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新角色（仅自己的）"""
    result = await db.execute(
        select(Character).where(
            Character.id == character_id,
            Character.user_id == user.id,
        )
    )
    character = result.scalar_one_or_none()

    if not character:
        raise HTTPException(status_code=404, detail="角色不存在或无权限")

    if request.name is not None:
        character.name = request.name
    if request.description is not None:
        character.description = request.description
    if request.reference_image is not None:
        character.reference_image = request.reference_image
    if request.voice_config is not None:
        character.voice_config = json.dumps(request.voice_config)
    if request.avatar is not None:
        character.avatar = request.avatar
    if request.color is not None:
        character.color = request.color
    if request.is_public is not None:
        character.is_public = request.is_public

    await db.commit()

    return {"code": 200, "message": "更新成功", "data": None}


@router.delete("/{character_id}")
async def delete_character(
    character_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除角色（仅自己的）"""
    result = await db.execute(
        select(Character).where(
            Character.id == character_id,
            Character.user_id == user.id,
        )
    )
    character = result.scalar_one_or_none()

    if not character:
        raise HTTPException(status_code=404, detail="角色不存在或无权限")

    await db.delete(character)
    await db.commit()

    return {"code": 200, "message": "删除成功", "data": None}


async def init_default_characters() -> None:
    """初始化系统预置角色（应用启动时调用）"""
    async for db in get_db():
        try:
            # 检查是否已存在
            result = await db.execute(
                select(Character).where(Character.user_id.is_(None))
            )
            existing = result.scalars().all()

            existing_names = {c.name for c in existing}

            for char_data in SYSTEM_CHARACTERS:
                if char_data["name"] not in existing_names:
                    character = Character(
                        user_id=None,  # 系统预置
                        name=char_data["name"],
                        description=char_data["description"],
                        avatar=char_data.get("avatar"),
                        color=char_data.get("color"),
                        is_public=True,
                    )
                    db.add(character)

            await db.commit()
            logger.info(f"系统预置角色初始化完成，共 {len(SYSTEM_CHARACTERS)} 个")
        except Exception as e:
            logger.error(f"初始化系统角色失败: {e}")
            await db.rollback()
        finally:
            break
