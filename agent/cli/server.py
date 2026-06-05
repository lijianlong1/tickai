"""
Agent 中台 HTTP 服务
对外暴露 API，让前端可以调用 Agent 能力
"""
import asyncio
import logging
from typing import Optional, Dict, Any
import json

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from agent.core import config, registry
from agent.services import backend_client, data_analyzer

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Tick-AI Agent 中台",
    description="承担数据处理分析 + 大模型调用 + 智能化能力",
    version="1.0.0",
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============= 请求/响应模型 =============

class ChatRequest(BaseModel):
    agent: str
    input: str
    user_id: Optional[int] = None


class ChatResponse(BaseModel):
    agent: str
    response: str
    success: bool = True


class GenerateRequest(BaseModel):
    type: str  # comic / image / text / voice / music
    input: str
    user_id: Optional[int] = None


class TipsRequest(BaseModel):
    count: int = 5


class ModerateRequest(BaseModel):
    title: str
    content: str


class AnalyzeRequest(BaseModel):
    user_id: Optional[int] = None


# ============= API 路由 =============

@app.get("/")
async def root():
    return {
        "service": "Tick-AI Agent 中台",
        "version": "1.0.0",
        "agents": registry.list_classes(),
        "status": "running",
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/agents")
async def list_agents():
    """列出所有 Agent"""
    return {
        "agents": registry.list_classes(),
        "details": [registry.get(a).to_dict() for a in registry.list_classes()],
    }


@app.post("/chat")
async def chat(request: ChatRequest):
    """与 Agent 对话"""
    try:
        agent = registry.create(request.agent)
        response = await agent.run(request.input)
        return ChatResponse(agent=request.agent, response=response)
    except Exception as e:
        logger.exception("对话失败")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """流式对话"""
    from fastapi.responses import StreamingResponse

    async def generate():
        try:
            agent = registry.create(request.agent)
            async for chunk in agent.stream_run(request.input):
                yield f"data: {json.dumps({'chunk': chunk}, ensure_ascii=False)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.post("/generate")
async def generate(request: GenerateRequest):
    """内容生成"""
    try:
        gen_type = request.type

        if gen_type == "comic":
            agent = registry.create("comic_creator")
            result = await agent.create_script(request.input)
        elif gen_type == "image":
            agent = registry.create("image_generator")
            result = await agent.optimize_prompt(request.input)
        elif gen_type == "text":
            agent = registry.create("text_writer")
            result = await agent.write_article(request.input)
        elif gen_type == "voice":
            agent = registry.create("voice_director")
            result = await agent.recommend_voice(request.input)
        elif gen_type == "music":
            agent = registry.create("music_composer")
            result = await agent.compose_music(request.input, "欢快")
        else:
            raise HTTPException(status_code=400, detail=f"未知类型: {gen_type}")

        return {"type": gen_type, "result": result}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("生成失败")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tips")
async def daily_tips(request: TipsRequest = TipsRequest()):
    """每日副业技巧"""
    try:
        agent = registry.create("text_writer")
        tips = await agent.scrape_daily_tips()
        return {"tips": tips[:request.count]}
    except Exception as e:
        logger.exception("生成技巧失败")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/moderate")
async def moderate(request: ModerateRequest):
    """内容审核"""
    try:
        agent = registry.create("community_moderator")
        result = await agent.moderate_content(request.title, request.content)
        return result
    except Exception as e:
        logger.exception("审核失败")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/user")
async def analyze_user(request: AnalyzeRequest):
    """用户行为分析"""
    if not request.user_id:
        raise HTTPException(status_code=400, detail="缺少 user_id")
    try:
        result = await data_analyzer.analyze_user_behavior(request.user_id)
        return result
    except Exception as e:
        logger.exception("分析失败")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/community")
async def analyze_community():
    """社区趋势分析"""
    try:
        result = await data_analyzer.analyze_community_trends()
        return result
    except Exception as e:
        logger.exception("社区分析失败")
        raise HTTPException(status_code=500, detail=str(e))


async def run_server():
    """启动服务"""
    host = config.get("agent.host", "0.0.0.0")
    port = config.get("agent.port", 8000)
    workers = config.get("agent.workers", 1)

    logger.info(f"Agent 中台启动: http://{host}:{port}")
    config_uvicorn = uvicorn.Config(
        "agent.cli.server:app",
        host=host,
        port=port,
        log_level=config.get("agent.log_level", "info").lower(),
    )
    server = uvicorn.Server(config_uvicorn)
    await server.serve()


def run_sync():
    """同步启动服务"""
    uvicorn.run("agent.cli.server:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    run_sync()
