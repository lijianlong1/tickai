"""
提示词分享表模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from config.database import Base


class Prompt(Base):
    __tablename__ = "prompts"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="提示词ID")
    user_id = Column(Integer, nullable=False, comment="分享者用户ID")
    work_id = Column(Integer, comment="关联作品ID")
    title = Column(String(200), nullable=False, comment="提示词标题")
    content = Column(Text, nullable=False, comment="提示词内容")
    category = Column(String(50), comment="分类：COMIC/IMAGE/TEXT/VOICE/MUSIC")
    model_name = Column(String(50), comment="AI模型名称")
    use_count = Column(Integer, nullable=False, default=0, comment="使用次数")
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment="创建时间")
