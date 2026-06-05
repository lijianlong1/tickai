"""
提示词路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from config.database import get_db
from models.user import User
from models.prompt import Prompt
from utils.auth_deps import get_current_user

router = APIRouter(prefix="/prompts", tags=["提示词"])


@router.post("/")
async def create_prompt(
    title: str,
    content: str,
    category: str = "",
    model_name: str = "",
    work_id: int = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """分享提示词"""
    prompt = Prompt(
        user_id=user.id,
        work_id=work_id,
        title=title,
        content=content,
        category=category,
        model_name=model_name
    )
    
    db.add(prompt)
    await db.commit()
    await db.refresh(prompt)
    
    return {
        "code": 200,
        "message": "分享成功",
        "data": {
            "id": prompt.id,
            "title": prompt.title,
            "created_at": prompt.created_at.isoformat()
        }
    }


@router.get("/")
async def get_prompts(
    page: int = 1,
    page_size: int = 12,
    category: str = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取提示词列表"""
    offset = (page - 1) * page_size
    query = select(Prompt).order_by(Prompt.created_at.desc())
    
    if category:
        query = query.where(Prompt.category == category)
    
    result = await db.execute(query.offset(offset).limit(page_size))
    prompts = result.scalars().all()
    
    return {
        "code": 200,
        "message": "success",
        "data": [{
            "id": prompt.id,
            "user_id": prompt.user_id,
            "title": prompt.title,
            "content": prompt.content,
            "category": prompt.category,
            "model_name": prompt.model_name,
            "use_count": prompt.use_count,
            "created_at": prompt.created_at.isoformat()
        } for prompt in prompts]
    }


@router.get("/{prompt_id}")
async def get_prompt_detail(
    prompt_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取提示词详情"""
    prompt = await db.get(Prompt, prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="提示词不存在")
    
    # 更新使用次数
    await db.execute(
        update(Prompt)
        .where(Prompt.id == prompt_id)
        .values(use_count=Prompt.use_count + 1)
    )
    await db.commit()
    await db.refresh(prompt)
    
    author = await db.get(User, prompt.user_id)
    
    return {
        "code": 200,
        "message": "success",
        "data": {
            "id": prompt.id,
            "user_id": prompt.user_id,
            "author_name": author.username if author else "未知",
            "title": prompt.title,
            "content": prompt.content,
            "category": prompt.category,
            "model_name": prompt.model_name,
            "work_id": prompt.work_id,
            "use_count": prompt.use_count,
            "created_at": prompt.created_at.isoformat()
        }
    }


@router.delete("/{prompt_id}")
async def delete_prompt(
    prompt_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除提示词"""
    prompt = await db.get(Prompt, prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="提示词不存在")
    
    if prompt.user_id != user.id and user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="无权操作")
    
    await db.delete(prompt)
    await db.commit()
    
    return {
        "code": 200,
        "message": "删除成功"
    }
