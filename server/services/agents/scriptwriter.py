"""
编剧智能体（Scriptwriter）

职责：
- 先用视觉模型"看"主体图和背景图
- 基于图像内容 + 场景描述生成情感匹配的旁白
- 旁白字数与镜头时长匹配（每秒约 4-5 个字）

使用模型：视觉模型 + 文本模型（默认 minimax-vl-01 + minimax-text-01）
"""
import logging
import json

from services.agents.base_agent import (
    BaseAgent,
    WorkflowContext,
    PanelData,
    AGENT_SCRIPTWRITER,
)

logger = logging.getLogger(__name__)


class ScriptwriterAgent(BaseAgent):
    """编剧智能体"""

    name = AGENT_SCRIPTWRITER
    display_name = "编剧"
    description = "基于图像内容生成情感匹配的旁白"
    icon = "✍️"
    color = "#8B5CF6"  # 紫色

    # 字数规则：每秒约 4 个字
    CHARS_PER_SECOND = 4

    async def run(self, context: WorkflowContext) -> WorkflowContext:
        """执行编剧任务"""
        vision_config = context.config.model_config.get("vision", {})
        narration_config = context.config.model_config.get("narration", {})

        vision_provider = vision_config.get("provider", "minimax")
        vision_model = vision_config.get("model", "minimax-vl-01")

        narration_provider = narration_config.get("provider", "minimax")
        narration_model = narration_config.get("model", "minimax-text-01")

        from services.model_adapter import ModelAdapter

        total_panels = len(context.panels)

        for idx, panel in enumerate(context.panels):
            try:
                # 跳过已有完整旁白的（重做时）
                if not panel.narration:
                    self.update_progress(
                        int(90 * (idx / total_panels)) + 5,
                        f"为镜头 {panel.index}/{total_panels} 撰写旁白...",
                    )

                    # Step 1: 视觉理解（看图）
                    vision_desc = ""
                    if panel.subject_image_url and panel.background_image_url:
                        try:
                            vision_adapter = ModelAdapter.from_config({
                                "provider": vision_provider,
                                "model": vision_model,
                            })
                            # 拼接两张图（用英文逗号分隔多图）
                            image_urls = f"{panel.subject_image_url}, {panel.background_image_url}"
                            vision_desc = await vision_adapter.analyze_image(
                                image_url=image_urls,
                                prompt="详细描述这两张图片：主体人物的外貌动作、场景环境、整体氛围。要求具体、有画面感。",
                            )
                            panel.vision_description = vision_desc
                        except Exception as e:
                            logger.warning(f"视觉理解失败（镜头 {panel.index}）: {e}")
                            vision_desc = ""

                    # Step 2: 基于描述 + 场景生成旁白
                    narration_adapter = ModelAdapter.from_config({
                        "provider": narration_provider,
                        "model": narration_model,
                    })

                    target_chars = max(8, int(panel.duration * self.CHARS_PER_SECOND))

                    user_prompt = self._build_narration_prompt(
                        scene=panel.scene,
                        vision_desc=vision_desc,
                        duration=panel.duration,
                        target_chars=target_chars,
                    )

                    narration = await narration_adapter.generate_text(
                        prompt=user_prompt,
                        system_prompt="你是一个专业的视频旁白编剧，擅长用简洁、有感染力的文字描绘画面。",
                        temperature=0.7,
                        max_tokens=200,
                    )

                    panel.narration = narration.strip().strip('"').strip("'")

            except Exception as e:
                logger.error(f"镜头 {panel.index} 旁白生成失败: {e}", exc_info=True)
                # 失败时使用简单旁白
                if not panel.narration:
                    panel.narration = f"场景 {panel.index}"

        self.update_progress(100, f"编剧完成：{total_panels} 个镜头旁白")

        return context

    def _build_narration_prompt(
        self, scene: str, vision_desc: str, duration: float, target_chars: int
    ) -> str:
        """构造旁白生成提示词"""
        if vision_desc:
            context = f"**画面描述（来自视觉模型）**：\n{vision_desc}\n\n"
        else:
            context = ""

        return f"""{context}**场景设定**：{scene}

**任务**：为这段视频画面写一句旁白。

**要求**：
- 字数：约 {target_chars} 个字（{duration} 秒朗读时长）
- 风格：简洁、有画面感、富有情感
- 内容：基于画面内容，不要凭空添加
- 适合 TTS 朗读，避免生僻字
- 直接输出旁白文字，不要任何解释

**示例**：
- 画面是森林入口："少年踏入了未知的森林，阳光透过树叶洒下。"
- 画面是夜空："星空下，一颗流星划过天际。"

请撰写："""
