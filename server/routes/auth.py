"""
认证路由
"""
import random
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from config.database import get_db
from models.user import User
from utils.jwt_utils import verify_password, get_password_hash, create_access_token
from utils.auth_deps import get_current_user

router = APIRouter(prefix="/auth", tags=["认证"])

AVATARS = [
    "👨‍💻", "👩‍💻", "🧑‍🎨", "👨‍🎨", "👩‍🎨",
    "🧑‍🚀", "👨‍🚀", "👩‍🚀", "🦸‍♂️", "🦸‍♀️",
    "🧙‍♂️", "🧙‍♀️", "🦊", "🐱", "🐼"
]


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/register")
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """用户注册"""
    # 检查邮箱是否已存在
    result = await db.execute(select(User).where(User.email == request.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="该邮箱已注册")
    
    # 检查用户名是否已存在
    result = await db.execute(select(User).where(User.username == request.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="该用户名已被使用")
    
    # 创建用户
    user = User(
        username=request.username,
        email=request.email,
        password=get_password_hash(request.password),
        account=request.email,
        avatar=random.choice(AVATARS),
        balance=0.00,
        role="USER",
        status=1
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # 生成 Token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return {
        "code": 200,
        "message": "注册成功",
        "data": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "account": user.account,
            "avatar": user.avatar,
            "balance": float(user.balance),
            "role": user.role,
            "token": access_token
        }
    }


@router.post("/login")
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """用户登录"""
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()
    
    if user is None or not verify_password(request.password, user.password):
        raise HTTPException(status_code=401, detail="邮箱或密码错误")
    
    if user.status != 1:
        raise HTTPException(status_code=401, detail="账号已被禁用")
    
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return {
        "code": 200,
        "message": "登录成功",
        "data": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "account": user.account,
            "avatar": user.avatar,
            "balance": float(user.balance),
            "role": user.role,
            "token": access_token
        }
    }


@router.get("/me")
async def get_current_user_info(
    user: User = Depends(get_current_user)
):
    """获取当前用户信息"""
    return {
        "code": 200,
        "message": "success",
        "data": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "account": user.account,
            "avatar": user.avatar,
            "balance": float(user.balance),
            "role": user.role,
            "status": user.status,
            "created_at": user.created_at.isoformat()
        }
    }
