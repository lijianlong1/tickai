"""
收藏表模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime
from config.database import Base


class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="ID")
    user_id = Column(Integer, nullable=False, comment="用户ID")
    work_id = Column(Integer, nullable=False, comment="作品ID")
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment="创建时间")
