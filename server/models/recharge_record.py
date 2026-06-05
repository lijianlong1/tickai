"""
充值记录表模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DECIMAL, DateTime
from config.database import Base


class RechargeRecord(Base):
    __tablename__ = "recharge_records"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="ID")
    user_id = Column(Integer, nullable=False, comment="用户ID")
    amount = Column(DECIMAL(10, 2), nullable=False, comment="充值金额")
    payment_method = Column(String(20), comment="支付方式：ALIPAY/WECHAT/CARD")
    transaction_id = Column(String(100), unique=True, comment="交易流水号")
    status = Column(String(20), nullable=False, default="PENDING", comment="状态：PENDING/SUCCESS/FAILED")
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment="更新时间")
