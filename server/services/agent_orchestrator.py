"""
智能体编排器

负责协调 5 个智能体按顺序执行：
1. Storyboarder（分镜师）
2. Illustrator（画师）
3. Scriptwriter（编剧）
4. VoiceActor（配音师）
5. Editor（剪辑师）

支持：
- 状态持久化（断点续传）
- 错误恢复
- 单个阶段重做
- 进度追踪
"""
import json
import asyncio
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from config.database import get_db
from models.workflow import Workflow, WorkflowPanelHistory
from services.agents.base_agent import (
    BaseAgent,
    WorkflowContext,
    WorkflowConfig,
    PanelData,
    AgentStatus,
    AgentState,
    AGENT_STAGES,
    AGENT_STORYBOARDER,
    AGENT_ILLUSTRATOR,
    AGENT_SCRIPTWRITER,
    AGENT_VOICE_ACTOR,
    AGENT_EDITOR,
)

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """智能体编排器"""

    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}
        # 进度回调（用于推送实时状态）
        self._progress_callbacks: Dict[int, list] = {}
        logger.info("AgentOrchestrator 已初始化")

    def register_agent(self, agent: BaseAgent) -> None:
        """注册智能体"""
        self._agents[agent.name] = agent
        logger.info(f"已注册智能体: {agent.name} ({agent.display_name})")

    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """获取智能体"""
        return self._agents.get(name)

    def add_progress_callback(self, workflow_id: int, callback) -> None:
        """添加进度回调"""
        if workflow_id not in self._progress_callbacks:
            self._progress_callbacks[workflow_id] = []
        self._progress_callbacks[workflow_id].append(callback)

    def remove_progress_callbacks(self, workflow_id: int) -> None:
        """移除进度回调"""
        self._progress_callbacks.pop(workflow_id, None)

    async def _notify_progress(self, workflow_id: int, stage: str, progress: int, message: str) -> None:
        """通知进度更新"""
        callbacks = self._progress_callbacks.get(workflow_id, [])
        for cb in callbacks:
            try:
                if asyncio.iscoroutinefunction(cb):
                    await cb(stage, progress, message)
                else:
                    cb(stage, progress, message)
            except Exception as e:
                logger.error(f"进度回调失败: {e}")

    async def run_workflow(self, workflow_id: int) -> Dict[str, Any]:
        """
        运行完整工作流

        Args:
            workflow_id: 工作流 ID

        Returns:
            运行结果
        """
        logger.info(f"开始运行工作流 {workflow_id}")

        # 1. 加载工作流
        workflow = await self._load_workflow(workflow_id)
        if not workflow:
            return {"success": False, "error": "工作流不存在"}

        # 2. 构建上下文
        context = await self._build_context(workflow)
        if not context:
            return {"success": False, "error": "构建上下文失败"}

        # 3. 按阶段执行
        try:
            for stage in AGENT_STAGES:
                if stage not in self._agents:
                    logger.warning(f"智能体 {stage} 未注册，跳过")
                    continue

                await self._update_stage(workflow_id, stage, "running", 0, f"开始 {stage}")
                await self._notify_progress(workflow_id, stage, 0, f"开始 {stage}")

                agent = self._agents[stage]
                agent.reset()

                # 执行
                context = await agent.run_with_retry(context)

                # 保存历史
                await self._save_panel_history(workflow_id, context, stage)

                # 持久化
                await self._save_workflow_state(workflow_id, context, stage, "success", 100)

                await self._notify_progress(workflow_id, stage, 100, f"{stage} 完成")

            # 标记完成
            await self._update_workflow_status(workflow_id, "completed", 100, "所有阶段完成")

            return {
                "success": True,
                "workflow_id": workflow_id,
                "panels": [p.dict() for p in context.panels],
            }

        except Exception as e:
            logger.error(f"工作流 {workflow_id} 失败: {e}", exc_info=True)
            await self._update_workflow_status(workflow_id, "failed", 0, str(e))
            return {"success": False, "workflow_id": workflow_id, "error": str(e)}

    async def run_stage(self, workflow_id: int, stage: str) -> Dict[str, Any]:
        """
        单独执行某个阶段（用于重做）

        Args:
            workflow_id: 工作流 ID
            stage: 阶段名称

        Returns:
            执行结果
        """
        logger.info(f"运行工作流 {workflow_id} 的 {stage} 阶段")

        workflow = await self._load_workflow(workflow_id)
        if not workflow:
            return {"success": False, "error": "工作流不存在"}

        context = await self._build_context(workflow)
        if not context:
            return {"success": False, "error": "构建上下文失败"}

        if stage not in self._agents:
            return {"success": False, "error": f"智能体 {stage} 未注册"}

        try:
            agent = self._agents[stage]
            agent.reset()
            context = await agent.run_with_retry(context)
            await self._save_panel_history(workflow_id, context, stage)
            await self._save_workflow_state(workflow_id, context, stage, "success", 100)

            return {
                "success": True,
                "stage": stage,
                "panels": [p.dict() for p in context.panels],
            }
        except Exception as e:
            logger.error(f"阶段 {stage} 失败: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    async def run_regenerate_panel_image(
        self, workflow_id: int, panel_index: int, image_type: str = "both"
    ) -> Dict[str, Any]:
        """
        重新生成某个镜头的图像

        Args:
            workflow_id: 工作流 ID
            panel_index: 镜头索引（1-based）
            image_type: subject / background / both
        """
        logger.info(f"重新生成工作流 {workflow_id} 镜头 {panel_index} 的图像")

        workflow = await self._load_workflow(workflow_id)
        if not workflow:
            return {"success": False, "error": "工作流不存在"}

        context = await self._build_context(workflow)
        if not context:
            return {"success": False, "error": "构建上下文失败"}

        illustrator = self._agents.get(AGENT_ILLUSTRATOR)
        if not illustrator:
            return {"success": False, "error": "Illustrator 未注册"}

        try:
            # 调用 illustrator 的单镜头重做方法
            panel = context.panels[panel_index - 1]
            await illustrator.regenerate_panel_image(panel, image_type, context)
            await self._save_workflow_state(workflow_id, context, AGENT_ILLUSTRATOR, "success", 100)

            return {
                "success": True,
                "panel_index": panel_index,
                "panel": panel.dict(),
            }
        except Exception as e:
            logger.error(f"重做图像失败: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    async def run_regenerate_panel_voice(
        self, workflow_id: int, panel_index: int
    ) -> Dict[str, Any]:
        """重新生成某个镜头的语音"""
        logger.info(f"重新生成工作流 {workflow_id} 镜头 {panel_index} 的语音")

        workflow = await self._load_workflow(workflow_id)
        if not workflow:
            return {"success": False, "error": "工作流不存在"}

        context = await self._build_context(workflow)
        if not context:
            return {"success": False, "error": "构建上下文失败"}

        voice_actor = self._agents.get(AGENT_VOICE_ACTOR)
        if not voice_actor:
            return {"success": False, "error": "VoiceActor 未注册"}

        try:
            panel = context.panels[panel_index - 1]
            await voice_actor.regenerate_panel_voice(panel, context)
            await self._save_workflow_state(workflow_id, context, AGENT_VOICE_ACTOR, "success", 100)

            return {"success": True, "panel_index": panel_index, "panel": panel.dict()}
        except Exception as e:
            logger.error(f"重做语音失败: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    async def run_recompose(self, workflow_id: int) -> Dict[str, Any]:
        """重新合成视频（不重新生成图像/语音）"""
        logger.info(f"重新合成工作流 {workflow_id} 的视频")

        workflow = await self._load_workflow(workflow_id)
        if not workflow:
            return {"success": False, "error": "工作流不存在"}

        context = await self._build_context(workflow)
        if not context:
            return {"success": False, "error": "构建上下文失败"}

        editor = self._agents.get(AGENT_EDITOR)
        if not editor:
            return {"success": False, "error": "Editor 未注册"}

        try:
            video_path, thumbnail_path = await editor.compose_video(context)
            await self._update_workflow_videos(workflow_id, video_path, thumbnail_path)
            return {
                "success": True,
                "video_url": f"/static/videos/{video_path.split('/')[-1]}",
                "thumbnail_url": f"/static/images/{thumbnail_path.split('/')[-1]}" if thumbnail_path else None,
            }
        except Exception as e:
            logger.error(f"重新合成失败: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    # ============ 内部辅助方法 ============

    async def _load_workflow(self, workflow_id: int) -> Optional[Workflow]:
        """加载工作流"""
        async for db in get_db():
            result = await db.execute(
                select(Workflow).where(Workflow.id == workflow_id)
            )
            return result.scalar_one_or_none()
        return None

    async def _build_context(self, workflow: Workflow) -> Optional[WorkflowContext]:
        """构建工作流上下文"""
        try:
            # 解析 panels
            panels_data = json.loads(workflow.panels) if workflow.panels else []
            panels = []
            for p in panels_data:
                panels.append(PanelData(**p))

            # 如果 panels 为空，根据 panel_count 创建空白
            if not panels:
                panel_count = workflow.panel_count or 6
                per_duration = max(2, (workflow.duration or 30) // panel_count)
                for i in range(1, panel_count + 1):
                    panels.append(PanelData(
                        index=i,
                        scene="",
                        camera="中景",
                        duration=per_duration,
                    ))

            # 解析配置
            model_config = json.loads(workflow.model_config) if workflow.model_config else {}
            character_ids = json.loads(workflow.character_ids) if workflow.character_ids else []
            subtitle_config = json.loads(workflow.subtitle_config) if workflow.subtitle_config else None

            # 加载角色
            from models.character import Character
            characters = []
            if character_ids:
                async for db in get_db():
                    result = await db.execute(
                        select(Character).where(Character.id.in_(character_ids))
                    )
                    characters = [
                        {
                            "id": c.id,
                            "name": c.name,
                            "description": c.description,
                            "avatar": c.avatar,
                        }
                        for c in result.scalars().all()
                    ]
                    break

            # 构建配置
            config = WorkflowConfig(
                user_id=workflow.user_id,
                workflow_id=workflow.id,
                title=workflow.title,
                original_prompt=workflow.original_prompt,
                panel_count=workflow.panel_count,
                ratio=workflow.ratio,
                target_duration=workflow.duration or 30,
                character_ids=character_ids,
                model_config=model_config,
                subtitle_config=subtitle_config,
            )

            return WorkflowContext(
                config=config,
                panels=panels,
                characters=characters,
            )
        except Exception as e:
            logger.error(f"构建上下文失败: {e}", exc_info=True)
            return None

    async def _save_panel_history(
        self, workflow_id: int, context: WorkflowContext, stage: str
    ) -> None:
        """保存镜头历史"""
        async for db in get_db():
            try:
                # 找到当前版本号
                result = await db.execute(
                    select(WorkflowPanelHistory).where(
                        WorkflowPanelHistory.workflow_id == workflow_id,
                        WorkflowPanelHistory.stage == stage,
                    ).order_by(WorkflowPanelHistory.version.desc()).limit(1)
                )
                last = result.scalar_one_or_none()
                next_version = (last.version + 1) if last else 1

                # 只保存有内容的 panels
                for panel in context.panels:
                    # 只保存该阶段相关的数据
                    data = {}
                    if stage == AGENT_STORYBOARDER:
                        data = {
                            "scene": panel.scene,
                            "camera": panel.camera,
                            "characters": panel.characters,
                            "subject_prompt": panel.subject_prompt,
                            "background_prompt": panel.background_prompt,
                            "duration": panel.duration,
                        }
                    elif stage == AGENT_ILLUSTRATOR:
                        data = {
                            "subject_image_url": panel.subject_image_url,
                            "background_image_url": panel.background_image_url,
                        }
                    elif stage == AGENT_SCRIPTWRITER:
                        data = {
                            "narration": panel.narration,
                            "vision_description": panel.vision_description,
                        }
                    elif stage == AGENT_VOICE_ACTOR:
                        data = {
                            "audio_url": panel.audio_url,
                            "audio_duration": panel.audio_duration,
                        }

                    if data:
                        history = WorkflowPanelHistory(
                            workflow_id=workflow_id,
                            panel_index=panel.index,
                            stage=stage,
                            data=json.dumps(data, ensure_ascii=False),
                            version=next_version,
                        )
                        db.add(history)
                await db.commit()
            except Exception as e:
                logger.error(f"保存历史失败: {e}", exc_info=True)
                await db.rollback()
            finally:
                break

    async def _save_workflow_state(
        self, workflow_id: int, context: WorkflowContext, stage: str, status: str, progress: int
    ) -> None:
        """保存工作流状态"""
        async for db in get_db():
            try:
                result = await db.execute(
                    select(Workflow).where(Workflow.id == workflow_id)
                )
                workflow = result.scalar_one_or_none()
                if workflow:
                    workflow.panels = json.dumps(
                        [p.dict() for p in context.panels], ensure_ascii=False
                    )
                    workflow.current_stage = stage
                    workflow.progress = progress
                    workflow.current_step = f"{stage} 完成"
                    await db.commit()
            except Exception as e:
                logger.error(f"保存状态失败: {e}", exc_info=True)
                await db.rollback()
            finally:
                break

    async def _update_stage(
        self, workflow_id: int, stage: str, status: str, progress: int, message: str
    ) -> None:
        """更新工作流阶段"""
        async for db in get_db():
            try:
                result = await db.execute(
                    select(Workflow).where(Workflow.id == workflow_id)
                )
                workflow = result.scalar_one_or_none()
                if workflow:
                    workflow.current_stage = stage if status == "running" else workflow.current_stage
                    workflow.current_step = message
                    workflow.progress = progress
                    await db.commit()
            except Exception as e:
                logger.error(f"更新阶段失败: {e}", exc_info=True)
                await db.rollback()
            finally:
                break

    async def _update_workflow_status(
        self, workflow_id: int, status: str, progress: int, message: str
    ) -> None:
        """更新工作流状态"""
        async for db in get_db():
            try:
                result = await db.execute(
                    select(Workflow).where(Workflow.id == workflow_id)
                )
                workflow = result.scalar_one_or_none()
                if workflow:
                    workflow.current_stage = status
                    workflow.progress = progress
                    workflow.current_step = message
                    if status == "failed":
                        workflow.error_message = message
                    await db.commit()
            except Exception as e:
                logger.error(f"更新状态失败: {e}", exc_info=True)
                await db.rollback()
            finally:
                break

    async def _update_workflow_videos(
        self, workflow_id: int, video_path: str, thumbnail_path: Optional[str]
    ) -> None:
        """更新工作流的视频文件路径"""
        async for db in get_db():
            try:
                result = await db.execute(
                    select(Workflow).where(Workflow.id == workflow_id)
                )
                workflow = result.scalar_one_or_none()
                if workflow:
                    workflow.video_url = f"/static/videos/{video_path.split('/')[-1]}"
                    if thumbnail_path:
                        workflow.thumbnail_url = f"/static/images/{thumbnail_path.split('/')[-1]}"
                    await db.commit()
            except Exception as e:
                logger.error(f"更新视频路径失败: {e}", exc_info=True)
                await db.rollback()
            finally:
                break


# ============ 全局单例 ============

_orchestrator_instance: Optional[AgentOrchestrator] = None


def get_orchestrator() -> AgentOrchestrator:
    """获取编排器单例（懒加载）"""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        from services.agents.storyboarder import StoryboarderAgent
        from services.agents.illustrator import IllustratorAgent
        from services.agents.scriptwriter import ScriptwriterAgent
        from services.agents.voice_actor import VoiceActorAgent
        from services.agents.editor import EditorAgent

        _orchestrator_instance = AgentOrchestrator()
        _orchestrator_instance.register_agent(StoryboarderAgent())
        _orchestrator_instance.register_agent(IllustratorAgent())
        _orchestrator_instance.register_agent(ScriptwriterAgent())
        _orchestrator_instance.register_agent(VoiceActorAgent())
        _orchestrator_instance.register_agent(EditorAgent())
        logger.info("编排器已注册 5 个智能体")
    return _orchestrator_instance
