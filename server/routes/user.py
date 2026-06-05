"""
用户路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from config.database import get_db
from models.user import User
from models.recharge_record import RechargeRecord
from models.consume_record import ConsumeRecord
from utils.auth_deps import get_current_user

router = APIRouter(prefix="/user", tags=["用户"])


@router.put("/update")
async def update_user(
    username: str = None,
    avatar: str = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新用户信息"""
    if username:
        # 检查用户名是否已被使用
        result = await db.execute(select(User).where(User.username == username))
        existing_user = result.scalar_one_or_none()
        if existing_user and existing_user.id != user.id:
            raise HTTPException(status_code=400, detail="该用户名已被使用")
        user.username = username
    
    if avatar:
        user.avatar = avatar
    
    await db.commit()
    await db.refresh(user)
    
    return {
        "code": 200,
        "message": "更新成功",
        "data": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "avatar": user.avatar,
            "balance": float(user.balance)
        }
    }


@router.post("/recharge")
async def recharge(
    amount: float,
    payment_method: str = "ALIPAY",
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """用户充值"""
    if amount <= 0:
        raise HTTPException(status_code=400, detail="充值金额必须大于0")
    
    # 创建充值记录
    recharge_record = RechargeRecord(
        user_id=user.id,
        amount=amount,
        payment_method=payment_method,
        transaction_id=f"RECHARGE_{user.id}_{int(amount*100)}_{id(recharge_record)}",
        status="SUCCESS"
    )
    db.add(recharge_record)
    
    # 更新用户余额
    user.balance += amount
    
    await db.commit()
    await db.refresh(user)
    
    return {
        "code": 200,
        "message": "充值成功",
        "data": {
            "balance": float(user.balance),
            "recharge_amount": amount
        }
    }


@router.get("/balance")
async def get_balance(
    user: User = Depends(get_current_user)
):
    """获取用户余额"""
    return {
        "code": 200,
        "message": "success",
        "data": {
            "balance": float(user.balance)
        }
    }


@router.get("/recharge-records")
async def get_recharge_records(
    page: int = 1,
    page_size: int = 10,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取充值记录"""
    offset = (page - 1) * page_size
    result = await db.execute(
        select(RechargeRecord)
        .where(RechargeRecord.user_id == user.id)
        .order_by(RechargeRecord.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    records = result.scalars().all()
    
    return {
        "code": 200,
        "message": "success",
        "data": [{
            "id": record.id,
            "amount": float(record.amount),
            "payment_method": record.payment_method,
            "transaction_id": record.transaction_id,
            "status": record.status,
            "created_at": record.created_at.isoformat()
        } for record in records]
    }


@router.get("/consume-records")
async def get_consume_records(
    page: int = 1,
    page_size: int = 10,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取消费记录"""
    offset = (page - 1) * page_size
    result = await db.execute(
        select(ConsumeRecord)
        .where(ConsumeRecord.user_id == user.id)
        .order_by(ConsumeRecord.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    records = result.scalars().all()
    
    return {
        "code": 200,
        "message": "success",
        "data": [{
            "id": record.id,
            "amount": float(record.amount),
            "consume_type": record.consume_type,
            "description": record.description,
            "created_at": record.created_at.isoformat()
        } for record in records]
    }
