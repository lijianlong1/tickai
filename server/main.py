"""
Tick-AI 后端主应用
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入数据库配置和模型
from config.database import create_tables
from routes.auth import router as auth_router
from routes.user import router as user_router
from routes.works import router as works_router
from routes.prompts import router as prompts_router
from routes.voice_history import router as voice_history_router
from routes.create_history import router as create_history_router

# 创建应用实例
app = FastAPI(
    title="Tick-AI API",
    description="Tick-AI 后端接口文档",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth_router, prefix="/api")
app.include_router(user_router, prefix="/api")
app.include_router(works_router, prefix="/api")
app.include_router(prompts_router, prefix="/api")
app.include_router(voice_history_router, prefix="/api")
app.include_router(create_history_router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    """启动时执行的操作"""
    print("🎯 正在初始化数据库...")
    try:
        create_tables()
        print("✅ 数据库表创建成功")
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")


@app.get("/")
async def root():
    """健康检查接口"""
    return {"message": "Tick-AI API is running"}


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
