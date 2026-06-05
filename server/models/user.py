"""
用户表模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DECIMAL, DateTime
from config.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="用户ID")
    username = Column(String(50), nullable=False, comment="用户名")
    email = Column(String(100), nullable=False, unique=True, comment="邮箱")
    password = Column(String(255), nullable=False, comment="密码（BCrypt加密）")
    account = Column(String(50), nullable=False, unique=True, comment="账号")
    avatar = Column(String(255), default="👤", comment="头像emoji或URL")
    balance = Column(DECIMAL(10, 2), nullable=False, default=0.00, comment="账户余额")
    role = Column(String(20), nullable=False, default="USER", comment="用户角色：USER/ADMIN")
    status = Column(Integer, nullable=False, default=1, comment="状态：1-正常 0-禁用")
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment="更新时间")
