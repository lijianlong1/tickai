"""
Agent 中台 CLI 入口
提供命令行交互能力，承担复杂逻辑处理
"""
import asyncio
import argparse
import sys
import json
import logging
from pathlib import Path
from typing import Optional

# 添加项目根目录到 path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agent.core import config, registry
from agent.services import (
    backend_client,
    data_analyzer,
    ComicCreatorAgent,
    ImageGeneratorAgent,
    TextWriterAgent,
    VoiceDirectorAgent,
    MusicComposerAgent,
    CommunityModeratorAgent,
)


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("agent/logs/agent.log", encoding="utf-8"),
    ]
)
logger = logging.getLogger(__name__)


class AgentCLI:
    """Agent 中台命令行"""

    def __init__(self):
        self.parser = self._build_parser()
        self.current_agent: Optional[object] = None

    def _build_parser(self) -> argparse.ArgumentParser:
        """构建命令行解析器"""
        parser = argparse.ArgumentParser(
            prog="tick-agent",
            description="Tick-AI Agent 中台 - 承担数据处理分析 + 大模型调用 + 智能化能力",
        )
        subparsers = parser.add_subparsers(dest="command", help="可用命令")

        # === 服务管理 ===
        subparsers.add_parser("serve", help="启动 Agent 中台 HTTP 服务")

        subparsers.add_parser("list", help="列出所有可用 Agent")

        # === 用户认证 ===
        login_parser = subparsers.add_parser("login", help="登录后端")
        login_parser.add_argument("--email", required=True, help="邮箱")
        login_parser.add_argument("--password", required=True, help="密码")

        subparsers.add_parser("register", help="注册新用户")
        subparsers.add_argument("--username", required=True, help="用户名")
        subparsers.add_argument("--email", required=True, help="邮箱")
        subparsers.add_argument("--password", required=True, help="密码")

        subparsers.add_parser("me", help="查看当前用户信息")

        # === Agent 对话 ===
        chat_parser = subparsers.add_parser("chat", help="与指定 Agent 对话")
        chat_parser.add_argument("--agent", required=True, help="Agent ID")
        chat_parser.add_argument("--input", "-i", required=True, help="用户输入")

        # === 数据分析 ===
        subparsers.add_parser("analyze-user", help="分析用户行为")
        subparsers.add_argument("--user-id", type=int, required=True, help="用户ID")

        subparsers.add_parser("analyze-community", help="分析社区趋势")

        subparsers.add_parser("report", help="生成用户报告")
        subparsers.add_argument("--user-id", type=int, required=True, help="用户ID")

        # === 内容生成 ===
        gen_parser = subparsers.add_parser("generate", help="内容生成")
        gen_parser.add_argument("--type", required=True,
                                choices=["comic", "image", "text", "voice", "music"],
                                help="生成类型")
        gen_parser.add_argument("--input", "-i", required=True, help="输入描述")

        # === 社区操作 ===
        subparsers.add_parser("works", help="查看社区作品")
        subparsers.add_argument("--type", help="作品类型筛选")
        subparsers.add_argument("--limit", type=int, default=10, help="数量限制")

        subparsers.add_parser("tips", help="生成每日副业技巧")

        subparsers.add_parser("moderate", help="内容审核")
        subparsers.add_argument("--title", required=True, help="内容标题")
        subparsers.add_argument("--content", required=True, help="内容")

        return parser

    async def cmd_serve(self, args):
        """启动服务"""
        from agent.cli.server import run_server
        await run_server()

    async def cmd_list(self, args):
        """列出 Agent"""
        agents = registry.list_classes()
        print("\n=== 可用 Agent ===")
        for a in agents:
            print(f"  - {a}")
        print(f"\n共 {len(agents)} 个 Agent\n")

    async def cmd_login(self, args):
        """登录"""
        result = await backend_client.login(args.email, args.password)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    async def cmd_register(self, args):
        """注册"""
        result = await backend_client.register(args.username, args.email, args.password)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    async def cmd_me(self, args):
        """当前用户"""
        result = await backend_client.get_me()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    async def cmd_chat(self, args):
        """与 Agent 对话"""
        agent = registry.create(args.agent)
        print(f"\n[{agent.name}] 思考中...\n")
        response = await agent.run(args.input)
        print(f"[{agent.name}]:\n{response}\n")

    async def cmd_analyze_user(self, args):
        """分析用户"""
        print(f"分析用户 {args.user_id}...")
        result = await data_analyzer.analyze_user_behavior(args.user_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    async def cmd_analyze_community(self, args):
        """分析社区"""
        print("分析社区趋势...")
        result = await data_analyzer.analyze_community_trends()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    async def cmd_report(self, args):
        """生成报告"""
        report = await data_analyzer.generate_user_report(args.user_id)
        print(report)

    async def cmd_generate(self, args):
        """内容生成"""
        gen_type = args.type

        if gen_type == "comic":
            agent = registry.create("comic_creator")
            result = await agent.create_script(args.input)
        elif gen_type == "image":
            agent = registry.create("image_generator")
            result = await agent.optimize_prompt(args.input)
        elif gen_type == "text":
            agent = registry.create("text_writer")
            result = await agent.write_article(args.input)
        elif gen_type == "voice":
            agent = registry.create("voice_director")
            result = await agent.recommend_voice(args.input)
        elif gen_type == "music":
            agent = registry.create("music_composer")
            result = await agent.compose_music(args.input, "欢快")
        else:
            print(f"未知类型: {gen_type}")
            return

        print(json.dumps(result, ensure_ascii=False, indent=2))

    async def cmd_works(self, args):
        """社区作品"""
        result = await backend_client.list_works(work_type=args.type, size=args.limit)
        records = result.get("data", {}).get("records", [])
        print(f"\n=== 社区作品（{len(records)} 个）===")
        for w in records:
            print(f"  [{w.get('id')}] {w.get('title')} - 点赞: {w.get('likeCount', 0)}")

    async def cmd_tips(self, args):
        """生成每日副业技巧"""
        agent = registry.create("text_writer")
        tips = await agent.scrape_daily_tips()
        print("\n=== 每日副业技巧 ===")
        for i, t in enumerate(tips, 1):
            print(f"  {i}. {t}")

    async def cmd_moderate(self, args):
        """内容审核"""
        agent = registry.create("community_moderator")
        result = await agent.moderate_content(args.title, args.content)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    async def run(self, argv=None):
        """运行 CLI"""
        args = self.parser.parse_args(argv)

        if not args.command:
            self.parser.print_help()
            return

        # 加载配置
        config.load()

        # 派发命令
        handler = getattr(self, f"cmd_{args.command.replace('-', '_')}", None)
        if not handler:
            print(f"未知命令: {args.command}")
            return

        try:
            await handler(args)
        except Exception as e:
            logger.exception(f"命令执行失败: {e}")
            print(f"[错误] {e}")
        finally:
            await backend_client.close()


def main():
    """CLI 入口函数"""
    cli = AgentCLI()
    asyncio.run(cli.run())


if __name__ == "__main__":
    main()
