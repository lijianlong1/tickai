"""
分镜师智能体（Storyboarder）

职责：
- 接收用户的原始需求
- 根据镜头数生成结构化的分镜剧本
- 每个镜头包含：场景描述、镜头语言、角色动作、主体/背景图像生成提示词

使用模型：文本模型（默认 MiniMax text-01）
"""
import json
import logging
from typing import List

from services.agents.base_agent import (
    BaseAgent,
    WorkflowContext,
    PanelData,
    AGENT_STORYBOARDER,
)

logger = logging.getLogger(__name__)


class StoryboarderAgent(BaseAgent):
    """分镜师智能体"""

    name = AGENT_STORYBOARDER
    display_name = "分镜师"
    description = "专业的视频分镜编剧，将用户需求拆分为结构化的分镜剧本"
    icon = "🎬"
    color = "#6366F1"  # 蓝色

    # 系统提示词
    SYSTEM_PROMPT = """你是一个专业的视频分镜编剧，擅长将用户的文字需求转换为结构化的分镜剧本。

你的任务是：
1. 理解用户的核心需求和故事主线
2. 设计镜头之间的叙事节奏（起承转合）
3. 为每个镜头编写详细的画面描述
4. 给出图像生成的提示词（分主体和背景）
5. 镜头之间要有视觉差异，避免重复

镜头设计原则：
- 远景：建立环境，展示整体氛围
- 中景：展示人物动作和互动
- 近景：展示表情和细节
- 特写：聚焦关键元素，制造张力

输出必须是严格的 JSON 格式。"""

    async def run(self, context: WorkflowContext) -> WorkflowContext:
        """
        执行分镜任务

        Args:
            context: 工作流上下文

        Returns:
            更新后的上下文
        """
        self.update_progress(5, "正在分析用户需求...")

        # 构造用户提示词
        user_prompt = self._build_user_prompt(context)

        # 获取模型配置
        model_config = context.config.model_config.get("storyboard", {})
        provider = model_config.get("provider", "minimax")
        model = model_config.get("model", "minimax-text-01")

        # 动态创建模型适配器
        from services.model_adapter import ModelAdapter
        adapter = ModelAdapter.from_config({
            "provider": provider,
            "model": model,
        })

        self.update_progress(15, f"调用 {provider} {model} 生成分镜...")

        # 调用文本模型
        try:
            data = await adapter.generate_json(
                prompt=user_prompt,
                system_prompt=self.SYSTEM_PROMPT,
                temperature=0.8,
                max_tokens=4000,
            )
        except Exception as e:
            logger.warning(f"使用 {provider} 失败，尝试回退: {e}")
            # 回退到环境变量默认
            adapter = ModelAdapter.from_env("minimax", "minimax-text-01")
            data = await adapter.generate_json(
                prompt=user_prompt,
                system_prompt=self.SYSTEM_PROMPT,
                temperature=0.8,
                max_tokens=4000,
            )

        self.update_progress(60, "解析分镜数据...")

        # 解析 panels
        panels_data = data.get("panels", [])
        if not panels_data:
            logger.warning("模型未返回 panels，使用默认分镜")
            panels_data = self._generate_default_panels(context)

        # 计算每镜时长
        target_duration = context.config.target_duration
        per_duration = max(2, target_duration // context.config.panel_count)

        # 填充到 panels
        for i, panel_data in enumerate(panels_data):
            if i >= len(context.panels):
                # 如果模型生成的数量多于预期，截断
                break
            if i < len(context.panels):
                panel = context.panels[i]
                panel.scene = panel_data.get("scene", "")
                panel.camera = panel_data.get("camera", "中景")
                panel.characters = panel_data.get("characters", [])
                panel.subject_prompt = panel_data.get("subject_prompt", panel.scene)
                panel.background_prompt = panel_data.get("background_prompt", panel.scene)
                if not panel.duration or panel.duration <= 0:
                    panel.duration = per_duration

        self.update_progress(100, f"分镜完成，共 {len(panels_data)} 个镜头")

        return context

    def _build_user_prompt(self, context: WorkflowContext) -> str:
        """构造用户提示词"""
        characters_desc = ""
        if context.characters:
            characters_desc = "\n\n可用角色：\n"
            for ch in context.characters:
                characters_desc += f"- 角色 ID {ch.get('id', 0)}: {ch.get('name', '未命名')}\n"
                characters_desc += f"  描述: {ch.get('description', '无')}\n"

        return f"""请根据以下需求创作视频分镜剧本：

**用户需求**：
{context.config.original_prompt}

**参数**：
- 镜头数量：{context.config.panel_count} 个
- 画面比例：{context.config.ratio}
- 目标总时长：{context.config.target_duration} 秒（每个镜头约 {max(2, context.config.target_duration // context.config.panel_count)} 秒）
- 标题：{context.config.title}
{characters_desc}

**输出 JSON 格式**（严格遵守）：
```json
{{
  "panels": [
    {{
      "index": 1,
      "scene": "详细的画面描述（中文，200字以内）",
      "camera": "镜头类型：远景/中景/近景/特写",
      "characters": [
        {{ "id": 1, "name": "角色名", "action": "角色动作描述" }}
      ],
      "subject_prompt": "用于生成主体图的英文 prompt（角色特写，简洁）",
      "background_prompt": "用于生成背景图的英文 prompt（场景环境，无人物）",
      "duration": 5
    }}
  ]
}}
```

**要求**：
1. 所有 panels 的 duration 之和 ≈ {context.config.target_duration} 秒
2. scene 描述要详细、生动、有画面感
3. 镜头之间要有叙事连贯性和视觉差异
4. subject_prompt 聚焦角色，background_prompt 聚焦场景
5. 严格输出 JSON，不要包含任何解释文字"""

    def _generate_default_panels(self, context: WorkflowContext) -> List[dict]:
        """生成默认分镜（兜底）"""
        per_duration = max(2, context.config.target_duration // context.config.panel_count)
        panels = []
        for i in range(1, context.config.panel_count + 1):
            panels.append({
                "index": i,
                "scene": f"场景 {i}：{context.config.original_prompt[:50]}",
                "camera": "中景",
                "characters": [],
                "subject_prompt": f"a character, {context.config.original_prompt[:50]}",
                "background_prompt": f"a background, {context.config.original_prompt[:50]}",
                "duration": per_duration,
            })
        return panels
