"""
作品评论表模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from config.database import Base


class WorkComment(Base):
    __tablename__ = "work_comments"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="ID")
    user_id = Column(Integer, nullable=False, comment="评论者ID")
    work_id = Column(Integer, nullable=False, comment="作品ID")
    parent_id = Column(Integer, default=0, comment="父评论ID（0表示一级评论）")
    content = Column(Text, nullable=False, comment="评论内容")
    like_count = Column(Integer, nullable=False, default=0, comment="点赞数")
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment="创建时间")
