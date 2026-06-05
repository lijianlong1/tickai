"""
作品路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from config.database import get_db
from models.user import User
from models.work import Work
from models.work_like import WorkLike
from models.work_comment import WorkComment
from models.favorite import Favorite
from utils.auth_deps import get_current_user

router = APIRouter(prefix="/works", tags=["作品"])


@router.post("/")
async def create_work(
    title: str,
    description: str = "",
    work_type: str = "IMAGE",
    media_url: str = "",
    cover_url: str = "",
    prompt: str = "",
    model_params: str = "",
    tags: str = "",
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建作品"""
    work = Work(
        user_id=user.id,
        title=title,
        description=description,
        work_type=work_type,
        media_url=media_url,
        cover_url=cover_url,
        prompt=prompt,
        model_params=model_params,
        tags=tags,
        is_public=1
    )
    
    db.add(work)
    await db.commit()
    await db.refresh(work)
    
    return {
        "code": 200,
        "message": "创建成功",
        "data": {
            "id": work.id,
            "title": work.title,
            "work_type": work.work_type,
            "created_at": work.created_at.isoformat()
        }
    }


@router.get("/")
async def get_works(
    page: int = 1,
    page_size: int = 12,
    work_type: str = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取作品列表"""
    offset = (page - 1) * page_size
    query = select(Work).where(Work.is_public == 1).order_by(Work.created_at.desc())
    
    if work_type:
        query = query.where(Work.work_type == work_type)
    
    result = await db.execute(query.offset(offset).limit(page_size))
    works = result.scalars().all()
    
    return {
        "code": 200,
        "message": "success",
        "data": [{
            "id": work.id,
            "user_id": work.user_id,
            "title": work.title,
            "description": work.description,
            "work_type": work.work_type,
            "media_url": work.media_url,
            "cover_url": work.cover_url,
            "tags": work.tags,
            "view_count": work.view_count,
            "like_count": work.like_count,
            "created_at": work.created_at.isoformat()
        } for work in works]
    }


@router.get("/{work_id}")
async def get_work_detail(
    work_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取作品详情"""
    work = await db.get(Work, work_id)
    if not work:
        raise HTTPException(status_code=404, detail="作品不存在")
    
    # 更新浏览量
    await db.execute(
        update(Work)
        .where(Work.id == work_id)
        .values(view_count=Work.view_count + 1)
    )
    await db.commit()
    await db.refresh(work)
    
    # 获取作者信息
    author = await db.get(User, work.user_id)
    
    return {
        "code": 200,
        "message": "success",
        "data": {
            "id": work.id,
            "user_id": work.user_id,
            "author_name": author.username if author else "未知",
            "author_avatar": author.avatar if author else "👤",
            "title": work.title,
            "description": work.description,
            "work_type": work.work_type,
            "media_url": work.media_url,
            "cover_url": work.cover_url,
            "prompt": work.prompt,
            "model_params": work.model_params,
            "tags": work.tags,
            "view_count": work.view_count,
            "like_count": work.like_count,
            "created_at": work.created_at.isoformat()
        }
    }


@router.put("/{work_id}")
async def update_work(
    work_id: int,
    title: str = None,
    description: str = None,
    is_public: int = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新作品"""
    work = await db.get(Work, work_id)
    if not work:
        raise HTTPException(status_code=404, detail="作品不存在")
    
    if work.user_id != user.id and user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="无权操作")
    
    if title:
        work.title = title
    if description:
        work.description = description
    if is_public is not None:
        work.is_public = is_public
    
    await db.commit()
    await db.refresh(work)
    
    return {
        "code": 200,
        "message": "更新成功",
        "data": {
            "id": work.id,
            "title": work.title,
            "description": work.description,
            "is_public": work.is_public
        }
    }


@router.delete("/{work_id}")
async def delete_work(
    work_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除作品"""
    work = await db.get(Work, work_id)
    if not work:
        raise HTTPException(status_code=404, detail="作品不存在")
    
    if work.user_id != user.id and user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="无权操作")
    
    await db.delete(work)
    await db.commit()
    
    return {
        "code": 200,
        "message": "删除成功"
    }


@router.post("/{work_id}/like")
async def like_work(
    work_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """点赞/取消点赞作品"""
    work = await db.get(Work, work_id)
    if not work:
        raise HTTPException(status_code=404, detail="作品不存在")
    
    result = await db.execute(
        select(WorkLike).where(WorkLike.user_id == user.id).where(WorkLike.work_id == work_id)
    )
    existing_like = result.scalar_one_or_none()
    
    if existing_like:
        # 取消点赞
        await db.delete(existing_like)
        await db.execute(
            update(Work).where(Work.id == work_id).values(like_count=Work.like_count - 1)
        )
        await db.commit()
        return {
            "code": 200,
            "message": "取消点赞成功",
            "liked": False,
            "like_count": work.like_count - 1
        }
    else:
        # 点赞
        like = WorkLike(user_id=user.id, work_id=work_id)
        db.add(like)
        await db.execute(
            update(Work).where(Work.id == work_id).values(like_count=Work.like_count + 1)
        )
        await db.commit()
        return {
            "code": 200,
            "message": "点赞成功",
            "liked": True,
            "like_count": work.like_count + 1
        }


@router.get("/{work_id}/comments")
async def get_work_comments(
    work_id: int,
    page: int = 1,
    page_size: int = 20,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取作品评论"""
    offset = (page - 1) * page_size
    result = await db.execute(
        select(WorkComment)
        .where(WorkComment.work_id == work_id)
        .order_by(WorkComment.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    comments = result.scalars().all()
    
    return {
        "code": 200,
        "message": "success",
        "data": [{
            "id": comment.id,
            "user_id": comment.user_id,
            "parent_id": comment.parent_id,
            "content": comment.content,
            "like_count": comment.like_count,
            "created_at": comment.created_at.isoformat()
        } for comment in comments]
    }


@router.post("/{work_id}/comments")
async def add_comment(
    work_id: int,
    content: str,
    parent_id: int = 0,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """添加评论"""
    work = await db.get(Work, work_id)
    if not work:
        raise HTTPException(status_code=404, detail="作品不存在")
    
    comment = WorkComment(
        user_id=user.id,
        work_id=work_id,
        parent_id=parent_id,
        content=content
    )
    
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    
    return {
        "code": 200,
        "message": "评论成功",
        "data": {
            "id": comment.id,
            "content": comment.content,
            "created_at": comment.created_at.isoformat()
        }
    }


@router.post("/{work_id}/favorite")
async def favorite_work(
    work_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """收藏/取消收藏作品"""
    work = await db.get(Work, work_id)
    if not work:
        raise HTTPException(status_code=404, detail="作品不存在")
    
    result = await db.execute(
        select(Favorite).where(Favorite.user_id == user.id).where(Favorite.work_id == work_id)
    )
    existing_favorite = result.scalar_one_or_none()
    
    if existing_favorite:
        await db.delete(existing_favorite)
        await db.commit()
        return {
            "code": 200,
            "message": "取消收藏成功",
            "favorited": False
        }
    else:
        favorite = Favorite(user_id=user.id, work_id=work_id)
        db.add(favorite)
        await db.commit()
        return {
            "code": 200,
            "message": "收藏成功",
            "favorited": True
        }
