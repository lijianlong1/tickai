"""
创作历史路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from config.database import get_db
from models.user import User
from models.create_history import CreateHistory
from models.consume_record import ConsumeRecord
from utils.auth_deps import get_current_user

router = APIRouter(prefix="/create-history", tags=["创作历史"])


@router.post("/")
async def add_create_history(
    create_type: str,
    input_params: str = "",
    output_url: str = "",
    output_text: str = "",
    cost: float = 0.0,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """添加创作记录"""
    history = CreateHistory(
        user_id=user.id,
        create_type=create_type,
        input_params=input_params,
        output_url=output_url,
        output_text=output_text,
        status="SUCCESS",
        cost=cost
    )
    
    db.add(history)
    
    # 如果有消费，创建消费记录
    if cost > 0:
        consume_record = ConsumeRecord(
            user_id=user.id,
            amount=cost,
            consume_type=create_type,
            related_id=history.id,
            description=f"{create_type}创作消费"
        )
        db.add(consume_record)
        
        # 更新用户余额
        user.balance -= cost
    
    await db.commit()
    await db.refresh(history)
    
    return {
        "code": 200,
        "message": "记录成功",
        "data": {
            "id": history.id,
            "create_type": history.create_type,
            "cost": float(history.cost),
            "created_at": history.created_at.isoformat()
        }
    }


@router.get("/")
async def get_create_history(
    page: int = 1,
    page_size: int = 20,
    create_type: str = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取创作历史"""
    offset = (page - 1) * page_size
    query = select(CreateHistory).where(CreateHistory.user_id == user.id).order_by(CreateHistory.created_at.desc())
    
    if create_type:
        query = query.where(CreateHistory.create_type == create_type)
    
    result = await db.execute(query.offset(offset).limit(page_size))
    histories = result.scalars().all()
    
    return {
        "code": 200,
        "message": "success",
        "data": [{
            "id": history.id,
            "create_type": history.create_type,
            "input_params": history.input_params,
            "output_url": history.output_url,
            "output_text": history.output_text,
            "status": history.status,
            "cost": float(history.cost),
            "created_at": history.created_at.isoformat()
        } for history in histories]
    }
