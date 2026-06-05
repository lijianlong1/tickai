"""
画师智能体（Illustrator）

职责：
- 为每个镜头分别生成"主体图"（角色特写）和"背景图"（场景环境）
- 主体图：聚焦角色，1024x1024
- 背景图：环境场景，与目标比例匹配
- 保存到 static/images/ 目录

使用模型：图像模型（默认 MiniMax image-01）
"""
import os
import json
import asyncio
import logging
import httpx
from datetime import datetime
from typing import Optional

from services.agents.base_agent import (
    BaseAgent,
    WorkflowContext,
    PanelData,
    AGENT_ILLUSTRATOR,
)

logger = logging.getLogger(__name__)


class IllustratorAgent(BaseAgent):
    """画师智能体"""

    name = AGENT_ILLUSTRATOR
    display_name = "画师"
    description = "为每个镜头生成主体图（角色特写）和背景图（场景环境）"
    icon = "🎨"
    color = "#EC4899"  # 粉色

    IMAGE_DIR = "static/images"

    async def run(self, context: WorkflowContext) -> WorkflowContext:
        """
        执行绘画任务

        Args:
            context: 工作流上下文

        Returns:
            更新后的上下文
        """
        os.makedirs(self.IMAGE_DIR, exist_ok=True)

        # 解析比例 -> 背景图尺寸
        bg_size = self._get_background_size(context.config.ratio)
        # 主体图始终是正方形
        subject_size = "1024x1024"

        model_config = context.config.model_config.get("subject_image", {})
        provider = model_config.get("provider", "minimax")
        model = model_config.get("model", "minimax-image-01")

        total_panels = len(context.panels)
        completed = 0

        for panel in context.panels:
            try:
                # 如果已经有图（重做时），跳过
                if not panel.subject_image_url and panel.subject_prompt:
                    self.update_progress(
                        int(60 * (completed / total_panels)) + 10,
                        f"生成镜头 {panel.index}/{total_panels} 的主体图...",
                    )
                    subject_url = await self._generate_image(
                        provider=provider,
                        model=model,
                        prompt=panel.subject_prompt,
                        size=subject_size,
                        workflow_id=context.config.workflow_id,
                        panel_index=panel.index,
                        image_type="subject",
                    )
                    panel.subject_image_url = subject_url

                if not panel.background_image_url and panel.background_prompt:
                    self.update_progress(
                        int(60 * (completed / total_panels)) + 15,
                        f"生成镜头 {panel.index}/{total_panels} 的背景图...",
                    )
                    background_url = await self._generate_image(
                        provider=provider,
                        model=model,
                        prompt=panel.background_prompt,
                        size=bg_size,
                        workflow_id=context.config.workflow_id,
                        panel_index=panel.index,
                        image_type="background",
                    )
                    panel.background_image_url = background_url

                completed += 1
                self.update_progress(
                    int(60 * (completed / total_panels)) + 20,
                    f"镜头 {panel.index}/{total_panels} 图像生成完成",
                )

            except Exception as e:
                logger.error(f"镜头 {panel.index} 图像生成失败: {e}", exc_info=True)
                # 单个镜头失败不影响其他镜头

        self.update_progress(100, f"画师完成：{completed}/{total_panels} 个镜头")

        return context

    async def regenerate_panel_image(
        self, panel: PanelData, image_type: str, context: WorkflowContext
    ) -> None:
        """重新生成某个镜头的图像（供编排器调用）"""
        bg_size = self._get_background_size(context.config.ratio)
        model_config = context.config.model_config.get("subject_image", {})
        provider = model_config.get("provider", "minimax")
        model = model_config.get("model", "minimax-image-01")

        if image_type in ("subject", "both") and panel.subject_prompt:
            subject_url = await self._generate_image(
                provider=provider,
                model=model,
                prompt=panel.subject_prompt,
                size="1024x1024",
                workflow_id=context.config.workflow_id,
                panel_index=panel.index,
                image_type="subject",
            )
            panel.subject_image_url = subject_url

        if image_type in ("background", "both") and panel.background_prompt:
            background_url = await self._generate_image(
                provider=provider,
                model=model,
                prompt=panel.background_prompt,
                size=bg_size,
                workflow_id=context.config.workflow_id,
                panel_index=panel.index,
                image_type="background",
            )
            panel.background_image_url = background_url

    def _get_background_size(self, ratio: str) -> str:
        """根据比例获取背景图尺寸"""
        sizes = {
            "16:9": "1920x1080",
            "9:16": "1080x1920",
            "1:1": "1024x1024",
            "4:3": "1440x1080",
        }
        return sizes.get(ratio, "1920x1080")

    async def _generate_image(
        self,
        provider: str,
        model: str,
        prompt: str,
        size: str,
        workflow_id: int,
        panel_index: int,
        image_type: str,
    ) -> str:
        """
        生成图像并保存到本地

        Returns:
            图像 URL 路径
        """
        from services.model_adapter import ModelAdapter
        adapter = ModelAdapter.from_config({
            "provider": provider,
            "model": model,
        })

        response = await adapter.generate_image(
            prompt=prompt,
            size=size,
            n=1,
        )

        if not response.urls and not response.b64_json:
            raise ValueError(f"图像生成失败：{provider} {model} 返回空")

        # 保存图像
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"workflow_{workflow_id}_panel_{panel_index}_{image_type}_{timestamp}.jpg"
        save_path = os.path.join(self.IMAGE_DIR, filename)

        if response.urls:
            # 下载 URL 图像
            await adapter.download_image_to_file(response.urls[0], save_path)
        elif response.b64_json:
            # 保存 base64 图像
            adapter.save_base64_image(response.b64_json[0], save_path)

        return f"/{save_path.replace(os.sep, '/')}"

    async def download_image_to_file(self, url: str, save_path: str) -> str:
        """下载图像到本地文件"""
        os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            with open(save_path, "wb") as f:
                f.write(response.content)
        return save_path
