"""
社区作品表模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from config.database import Base


class Work(Base):
    __tablename__ = "works"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="作品ID")
    user_id = Column(Integer, nullable=False, comment="创建者用户ID")
    title = Column(String(200), nullable=False, comment="作品标题")
    description = Column(Text, comment="作品描述")
    work_type = Column(String(20), nullable=False, comment="作品类型：COMIC/IMAGE/TEXT/VOICE/MUSIC/VIDEO")
    media_url = Column(String(500), comment="媒体文件URL")
    cover_url = Column(String(500), comment="封面图URL")
    prompt = Column(Text, comment="AI提示词")
    model_params = Column(Text, comment="模型参数（JSON）")
    tags = Column(String(500), comment="标签（逗号分隔）")
    view_count = Column(Integer, nullable=False, default=0, comment="浏览数")
    like_count = Column(Integer, nullable=False, default=0, comment="点赞数")
    is_public = Column(Integer, nullable=False, default=1, comment="是否公开：1-公开 0-私有")
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment="更新时间")
