"""
消费记录表模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DECIMAL, DateTime
from config.database import Base


class ConsumeRecord(Base):
    __tablename__ = "consume_records"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="ID")
    user_id = Column(Integer, nullable=False, comment="用户ID")
    amount = Column(DECIMAL(10, 2), nullable=False, comment="消费金额")
    consume_type = Column(String(20), nullable=False, comment="消费类型：COMIC/IMAGE/TEXT/VOICE/MUSIC/VIDEO")
    related_id = Column(Integer, comment="关联记录ID")
    description = Column(String(255), comment="消费描述")
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment="创建时间")
