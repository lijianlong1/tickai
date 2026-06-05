#!/bin/bash
# Agent 中台启动脚本

# 切换到脚本所在目录
cd "$(dirname "$0")/.."

echo "=========================================="
echo "  Tick-AI Agent 中台启动"
echo "=========================================="

# 检查 Python 环境
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到 python3，请先安装 Python 3.9+"
    exit 1
fi

# 检查依赖
if [ ! -d "venv" ]; then
    echo "[信息] 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null

# 安装依赖
echo "[信息] 安装依赖..."
pip install -q -r agent/requirements.txt

# 创建日志目录
mkdir -p agent/logs

# 启动服务
echo "[信息] 启动 Agent 中台 HTTP 服务..."
python -m agent.cli.server
