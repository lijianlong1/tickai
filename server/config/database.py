"""
数据库配置
使用 SQLAlchemy 异步引擎
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# 从环境变量读取配置
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "tick_ai")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "root123456")

# 构建数据库 URL
DATABASE_URL = f"mysql+asyncmy://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

# 创建异步引擎
async_engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_size=20,
    max_overflow=50,
)

# 创建同步引擎（用于初始化）
sync_database_url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
sync_engine = create_engine(
    sync_database_url,
    echo=True,
)

# 创建会话工厂
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# 声明基类
Base = declarative_base()


async def get_db():
    """获取数据库会话"""
    async with AsyncSessionLocal() as session:
        yield session


def create_tables():
    """创建所有表（同步方式，用于启动时初始化）"""
    Base.metadata.create_all(bind=sync_engine)


def drop_tables():
    """删除所有表"""
    Base.metadata.drop_all(bind=sync_engine)
