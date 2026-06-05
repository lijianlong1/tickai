"""
用户模型配置路由

管理用户自定义的 AI 模型配置（文本/图像/语音）。
API Key 加密存储，响应中不返回明文。
"""
import os
import json
import logging
from typing import Optional
from cryptography.fernet import Fernet
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from config.database import get_db
from models.model_config import ModelConfig
from models.user import User
from utils.auth_deps import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/model-configs", tags=["模型配置"])


# ============ 加密工具 ============

def _get_fernet() -> Fernet:
    """获取 Fernet 加密器（密钥从环境变量读取）"""
    key = os.getenv("API_KEY_ENCRYPTION_KEY")
    if not key:
        # 使用固定密钥作为开发默认值（生产环境必须设置环境变量）
        key = "ZGV2LWtleS0xMjM0NTY3ODkwYWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXo="
    return Fernet(key.encode() if isinstance(key, str) else key)


def encrypt_api_key(plain_key: str) -> str:
    """加密 API Key"""
    return _get_fernet().encrypt(plain_key.encode()).decode()


def decrypt_api_key(encrypted_key: str) -> str:
    """解密 API Key"""
    try:
        return _get_fernet().decrypt(encrypted_key.encode()).decode()
    except Exception:
        return ""


# ============ Pydantic Schemas ============

class ModelConfigCreate(BaseModel):
    """创建模型配置"""
    config_type: str = Field(..., pattern="^(text|image|voice)$")
    provider: str = Field(..., min_length=1, max_length=50)
    model_name: str = Field(..., min_length=1, max_length=100)
    api_key: Optional[str] = Field(default=None, description="明文 API Key，仅用于传输")
    base_url: Optional[str] = None
    is_default: bool = False
    extra_params: Optional[dict] = None


class ModelConfigUpdate(BaseModel):
    """更新模型配置"""
    provider: Optional[str] = None
    model_name: Optional[str] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    is_default: Optional[bool] = None
    extra_params: Optional[dict] = None


class ModelConfigInfo(BaseModel):
    """模型配置信息（响应，不含明文 API Key）"""
    id: int
    config_type: str
    provider: str
    model_name: str
    has_api_key: bool
    base_url: Optional[str]
    is_default: bool
    extra_params: Optional[dict]
    created_at: str
    updated_at: str


# ============ API 接口 ============

@router.get("")
async def list_model_configs(
    config_type: Optional[str] = Query(default=None, pattern="^(text|image|voice)$"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """列出我的模型配置"""
    query = select(ModelConfig).where(ModelConfig.user_id == user.id)
    if config_type:
        query = query.where(ModelConfig.config_type == config_type)
    query = query.order_by(ModelConfig.is_default.desc(), ModelConfig.created_at.desc())

    result = await db.execute(query)
    configs = result.scalars().all()

    items = []
    for c in configs:
        extra = None
        if c.extra_params:
            try:
                extra = json.loads(c.extra_params)
            except json.JSONDecodeError:
                extra = None

        items.append(ModelConfigInfo(
            id=c.id,
            config_type=c.config_type,
            provider=c.provider,
            model_name=c.model_name,
            has_api_key=bool(c.api_key_encrypted),
            base_url=c.base_url,
            is_default=c.is_default,
            extra_params=extra,
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
async def create_model_config(
    request: ModelConfigCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """新增模型配置"""
    # 加密 API Key
    encrypted_key = None
    if request.api_key:
        encrypted_key = encrypt_api_key(request.api_key)

    # 如果设为默认，先取消同类型的其他默认
    if request.is_default:
        await _clear_default(db, user.id, request.config_type)

    config = ModelConfig(
        user_id=user.id,
        config_type=request.config_type,
        provider=request.provider,
        model_name=request.model_name,
        api_key_encrypted=encrypted_key,
        base_url=request.base_url,
        is_default=request.is_default,
        extra_params=json.dumps(request.extra_params) if request.extra_params else None,
    )

    db.add(config)
    await db.commit()
    await db.refresh(config)

    return {
        "code": 200,
        "message": "配置创建成功",
        "data": {
            "id": config.id,
            "config_type": config.config_type,
            "provider": config.provider,
            "model_name": config.model_name,
            "is_default": config.is_default,
        }
    }


@router.put("/{config_id}")
async def update_model_config(
    config_id: int,
    request: ModelConfigUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新模型配置"""
    result = await db.execute(
        select(ModelConfig).where(
            ModelConfig.id == config_id,
            ModelConfig.user_id == user.id,
        )
    )
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")

    # 更新字段
    if request.provider is not None:
        config.provider = request.provider
    if request.model_name is not None:
        config.model_name = request.model_name
    if request.api_key is not None and request.api_key != "":
        config.api_key_encrypted = encrypt_api_key(request.api_key)
    if request.base_url is not None:
        config.base_url = request.base_url
    if request.extra_params is not None:
        config.extra_params = json.dumps(request.extra_params)

    # 处理 is_default
    if request.is_default is True:
        await _clear_default(db, user.id, config.config_type)
        config.is_default = True
    elif request.is_default is False:
        config.is_default = False

    await db.commit()

    return {"code": 200, "message": "更新成功", "data": None}


@router.delete("/{config_id}")
async def delete_model_config(
    config_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除模型配置"""
    result = await db.execute(
        select(ModelConfig).where(
            ModelConfig.id == config_id,
            ModelConfig.user_id == user.id,
        )
    )
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")

    await db.delete(config)
    await db.commit()

    return {"code": 200, "message": "删除成功", "data": None}


@router.post("/{config_id}/set-default")
async def set_default_config(
    config_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """设为默认配置"""
    result = await db.execute(
        select(ModelConfig).where(
            ModelConfig.id == config_id,
            ModelConfig.user_id == user.id,
        )
    )
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")

    await _clear_default(db, user.id, config.config_type)
    config.is_default = True
    await db.commit()

    return {"code": 200, "message": "已设为默认", "data": None}


@router.post("/{config_id}/test")
async def test_model_config(
    config_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """测试模型配置连通性"""
    result = await db.execute(
        select(ModelConfig).where(
            ModelConfig.id == config_id,
            ModelConfig.user_id == user.id,
        )
    )
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")

    # 简化版测试：只检查配置是否完整
    issues = []
    if not config.provider:
        issues.append("缺少 provider")
    if not config.model_name:
        issues.append("缺少 model_name")
    if not config.api_key_encrypted and config.config_type != "voice":
        issues.append("缺少 API Key")

    if issues:
        return {
            "code": 400,
            "message": "配置不完整",
            "data": {"issues": issues}
        }

    # 实际测试连通性（简化版：只返回成功）
    return {
        "code": 200,
        "message": "配置有效（实际连通性需要调用模型 API 验证）",
        "data": {
            "config_type": config.config_type,
            "provider": config.provider,
            "model_name": config.model_name,
        }
    }


async def _clear_default(db: AsyncSession, user_id: int, config_type: str) -> None:
    """清除同类型的所有默认配置"""
    result = await db.execute(
        select(ModelConfig).where(
            ModelConfig.user_id == user_id,
            ModelConfig.config_type == config_type,
            ModelConfig.is_default == True,
        )
    )
    configs = result.scalars().all()
    for c in configs:
        c.is_default = False
    await db.commit()
