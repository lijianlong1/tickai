"""
具体 AI 智能体实现
- ComicCreatorAgent: AI 漫剧导演
- ImageGeneratorAgent: AI 图像大师
- TextWriterAgent: AI 写作助手
- VoiceDirectorAgent: AI 语音导演
- MusicComposerAgent: AI 音乐家
- CommunityModeratorAgent: 社区审核员
"""
import json
import logging
from typing import Dict, Any, List

from ..core.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class ComicCreatorAgent(BaseAgent):
    """AI 漫剧导演 Agent"""

    def __init__(self, agent_id: str = None, name: str = None):
        super().__init__(agent_id, name or "AI 漫剧导演")
        self.description = "负责 AI 漫剧剧本创作和分镜设计"
        self.llm_provider = "openai"
        self.load_system_prompt()

    async def create_script(self, theme: str, style: str = "日式漫画", episodes: int = 1) -> Dict:
        """生成漫剧剧本"""
        prompt = f"""请根据以下要求创作一个漫剧剧本：
- 主题：{theme}
- 风格：{style}
- 集数：{episodes}

请输出 JSON 格式：
{{
  "title": "作品名称",
  "synopsis": "故事简介",
  "characters": [{{"name": "角色名", "description": "角色描述"}}],
  "storyboard": [
    {{
      "scene": 1,
      "description": "场景描述",
      "dialogue": "对白",
      "shot_type": "镜头类型（特写/中景/远景）"
    }}
  ]
}}"""
        response = await self.run(prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"raw_response": response}


class ImageGeneratorAgent(BaseAgent):
    """AI 图像大师 Agent"""

    def __init__(self, agent_id: str = None, name: str = None):
        super().__init__(agent_id, name or "AI 图像大师")
        self.description = "负责图片生成提示词优化和风格把控"
        self.llm_provider = "openai"
        self.load_system_prompt()

    async def optimize_prompt(self, user_input: str, style: str = "写实") -> Dict:
        """优化图片生成提示词"""
        prompt = f"""请将以下描述优化为专业的 AI 图像生成提示词：

原始描述：{user_input}
目标风格：{style}

请输出：
1. 英文提示词（用于 Midjourney/Stable Diffusion）
2. 中文提示词
3. 推荐的负面提示词
4. 参数建议（尺寸、风格强度等）

格式：
```json
{{
  "en_prompt": "...",
  "zh_prompt": "...",
  "negative_prompt": "...",
  "params": {{"width": 1024, "height": 1024, "style_strength": 0.7}}
}}
```"""
        response = await self.run(prompt)
        try:
            # 提取 JSON 部分
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(response[start:end])
        except (json.JSONDecodeError, ValueError):
            pass
        return {"raw_response": response}

    async def suggest_styles(self, theme: str) -> List[str]:
        """推荐风格"""
        prompt = f"为主题「{theme}」推荐 5 种适合的 AI 图像生成风格，每种风格一行，不要编号。"
        response = await self.run(prompt)
        return [s.strip("- ").strip() for s in response.split("\n") if s.strip()]


class TextWriterAgent(BaseAgent):
    """AI 写作助手 Agent"""

    def __init__(self, agent_id: str = None, name: str = None):
        super().__init__(agent_id, name or "AI 写作助手")
        self.description = "负责各类文本内容创作"
        self.llm_provider = "dashscope"
        self.load_system_prompt()

    async def write_article(self, topic: str, style: str = "科普", length: int = 800) -> str:
        """撰写文章"""
        prompt = f"""请撰写一篇关于「{topic}」的{style}风格文章。
要求：
- 字数约 {length} 字
- 结构清晰，开头吸引人
- 包含小标题分段
- 结尾有总结或行动建议"""
        return await self.run(prompt)

    async def summarize(self, content: str, max_length: int = 200) -> str:
        """文本摘要"""
        prompt = f"请将以下内容总结为不超过 {max_length} 字的摘要：\n\n{content}"
        return await self.run(prompt)

    async def polish(self, content: str) -> str:
        """润色文本"""
        prompt = f"请润色以下文本，提升表达质量，保留原意：\n\n{content}"
        return await self.run(prompt)

    async def scrape_daily_tips(self) -> List[str]:
        """生成每日副业技巧（实际应接入真实爬虫）"""
        prompt = """请生成 5 条实用的副业技巧，每条 30-50 字，涵盖：
- AI 工具应用
- 自媒体运营
- 自由接单
- 内容创作
- 数字产品

每条以 "💡" 开头。"""
        response = await self.run(prompt)
        tips = []
        for line in response.split("\n"):
            line = line.strip()
            if line and ("💡" in line or line.startswith("-")):
                tips.append(line.lstrip("- 💡").strip())
        return [t for t in tips if t][:5]


class VoiceDirectorAgent(BaseAgent):
    """AI 语音导演 Agent"""

    def __init__(self, agent_id: str = None, name: str = None):
        super().__init__(agent_id, name or "AI 语音导演")
        self.description = "负责语音合成参数优化和情感把控"
        self.llm_provider = "zhipu"
        self.load_system_prompt()

    async def recommend_voice(self, text: str) -> Dict:
        """推荐音色"""
        prompt = f"""请根据以下文本推荐最适合的语音合成参数：

文本内容：{text[:200]}

请输出 JSON：
{{
  "voice_type": "推荐音色（如：温柔女声/磁性男声/活泼少女）",
  "emotion": "情感（平静/欢快/悲伤/激昂）",
  "speed": 1.0,  // 语速 0.5-2.0
  "pitch": 1.0,  // 音调 0.5-2.0
  "reason": "推荐理由"
}}"""
        response = await self.run(prompt)
        try:
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(response[start:end])
        except (json.JSONDecodeError, ValueError):
            pass
        return {"raw_response": response}


class MusicComposerAgent(BaseAgent):
    """AI 音乐家 Agent"""

    def __init__(self, agent_id: str = None, name: str = None):
        super().__init__(agent_id, name or "AI 音乐家")
        self.description = "负责音乐创作和编曲"
        self.llm_provider = "openai"
        self.load_system_prompt()

    async def compose_music(self, genre: str, mood: str, duration: int = 60) -> Dict:
        """创作音乐"""
        prompt = f"""请为一首{genre}风格的{mood}音乐设计创作方案：
- 时长：{duration} 秒
- 风格：{genre}
- 情绪：{mood}

请输出 JSON：
{{
  "title": "曲名",
  "bpm": 120,
  "key": "C major",
  "instruments": ["乐器1", "乐器2"],
  "structure": [
    {{"section": "前奏", "duration": 8, "description": "..."}},
    {{"section": "主歌", "duration": 16, "description": "..."}}
  ],
  "lyrics": "歌词（如果是歌曲）"
}}"""
        response = await self.run(prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"raw_response": response}


class CommunityModeratorAgent(BaseAgent):
    """社区审核员 Agent"""

    def __init__(self, agent_id: str = None, name: str = None):
        super().__init__(agent_id, name or "社区审核员")
        self.description = "负责社区内容审核和质量评估"
        self.llm_provider = "zhipu"
        self.load_system_prompt()

    async def moderate_content(self, title: str, content: str) -> Dict:
        """审核内容"""
        prompt = f"""请审核以下内容：

标题：{title}
内容：{content}

请输出 JSON：
{{
  "is_appropriate": true/false,
  "risk_level": "LOW/MEDIUM/HIGH",
  "issues": ["问题列表"],
  "suggestions": ["改进建议"],
  "quality_score": 0-10,
  "category": "内容分类"
}}"""
        response = await self.run(prompt)
        try:
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(response[start:end])
        except (json.JSONDecodeError, ValueError):
            pass
        return {"raw_response": response}

    async def recommend_works(self, user_preferences: Dict) -> List[str]:
        """推荐作品"""
        prompt = f"基于用户偏好 {json.dumps(user_preferences, ensure_ascii=False)}，推荐 5 个值得关注的创作方向。"
        response = await self.run(prompt)
        return [s.strip() for s in response.split("\n") if s.strip()][:5]
