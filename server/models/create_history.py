"""
创作历史记录表模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DECIMAL, DateTime
from config.database import Base


class CreateHistory(Base):
    __tablename__ = "create_history"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="历史记录ID")
    user_id = Column(Integer, nullable=False, comment="用户ID")
    create_type = Column(String(20), nullable=False, comment="创作类型：COMIC/IMAGE/TEXT/VOICE/MUSIC/VIDEO")
    input_params = Column(Text, comment="输入参数（JSON）")
    output_url = Column(String(500), comment="输出文件URL")
    output_text = Column(Text, comment="输出文本（用于文本生成）")
    status = Column(String(20), nullable=False, default="SUCCESS", comment="状态：SUCCESS/FAILED/PENDING")
    cost = Column(DECIMAL(10, 2), nullable=False, default=0.00, comment="消费金额")
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment="创建时间")
