@echo off
REM Agent 中台启动脚本 (Windows)

cd /d "%~dp0\.."

echo ==========================================
echo   Tick-AI Agent 中台启动
echo ==========================================

REM 检查 Python
where python >nul 2>nul
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.9+
    pause
    exit /b 1
)

REM 创建虚拟环境
if not exist "venv" (
    echo [信息] 创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 安装依赖
echo [信息] 安装依赖...
pip install -q -r agent\requirements.txt

REM 创建日志目录
if not exist "agent\logs" mkdir agent\logs

REM 启动服务
echo [信息] 启动 Agent 中台 HTTP 服务...
python -m agent.cli.server
