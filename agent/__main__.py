"""
Agent 中台启动入口
支持 CLI 和 HTTP 服务模式
"""
import sys
from pathlib import Path

# 添加项目根目录到 path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.cli import main

if __name__ == "__main__":
    main()
