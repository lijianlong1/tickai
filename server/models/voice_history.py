"""
语音合成历史表模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DECIMAL, DateTime
from config.database import Base


class VoiceHistory(Base):
    __tablename__ = "voice_history"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="ID")
    user_id = Column(Integer, nullable=False, comment="用户ID")
    text = Column(Text, nullable=False, comment="合成文本")
    voice_type = Column(String(50), comment="语音类型")
    speed = Column(DECIMAL(3, 1), default=1.0, comment="语速")
    pitch = Column(DECIMAL(3, 1), default=1.0, comment="音调")
    audio_url = Column(String(500), comment="音频URL")
    duration = Column(Integer, default=0, comment="时长（秒）")
    status = Column(String(20), default="SUCCESS", comment="状态")
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment="创建时间")
