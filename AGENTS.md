# AGENTS.md

> 本文件定义 AI 编码助手（GitHub Copilot / Trae / Cursor 等）在本项目中工作时必须遵守的规范与约束。

## 项目概述

**Tick-AI** 是一个个人 AI 创作平台，主要功能：
- AI 漫剧制作 / 图片生成 / 文本创作 / 语音合成 / 音乐创作
- 社区作品展示（图片、视频、提示词分享）
- 用户系统（注册、登录、余额、充值、消费）
- Agent 中台（大模型调用 + 智能体编排）

**技术栈**：
- **前端**：React 19 + Vite 8 + TailwindCSS 4 + React Router 7
- **后端**：Python 3.10 + FastAPI + SQLAlchemy + asyncmy
- **数据库**：MySQL 8.0（Docker）
- **AI**：OpenAI 兼容协议（支持 OpenAI / 通义千问 / 智谱 GLM）

## 目录结构

```
aitest/
├── web/                # 前端
│   ├── src/
│   │   ├── pages/      # 页面组件（每个文件对应一个路由）
│   │   ├── components/ # 公共组件
│   │   ├── contexts/   # 全局状态（UserContext 等）
│   │   └── services/   # API 调用层
│   └── vite.config.js  # Vite 配置（含代理）
│
├── server/             # Python 后端
│   ├── main.py         # 入口
│   ├── config/         # 配置（数据库连接）
│   ├── models/         # SQLAlchemy 模型（10 张表）
│   ├── routes/         # FastAPI 路由
│   ├── utils/          # 工具类（JWT、密码、认证）
│   ├── .env            # 环境变量（已 gitignore）
│   └── .env.example    # 环境变量模板
│
├── agent/              # Agent 中台
│   ├── core/           # 核心（LLM Client、Agent 基类）
│   ├── prompts/        # Agent 提示词
│   ├── services/       # 服务（agents、data_analyzer）
│   ├── configs/        # 配置文件
│   └── cli/            # CLI 入口
│
├── docker-compose.yml  # MySQL 容器
├── .gitignore          # 忽略 node_modules、.env、编译文件等
└── README.md           # 项目主文档
```

## 核心约定

### 1. 数据库

- **MySQL** 是唯一的数据库，**不要**引入 SQLite / PostgreSQL / MongoDB 等
- 数据库表由 SQLAlchemy 模型**自动创建**，**不要**手动写建表 SQL
- 修改表结构时：更新 [server/models/](file:///c:/Users/lijianlong/Documents/trae_projects/aitest/server/models/) 中的模型，重启后端即可
- 已有 10 张表：users / works / prompts / create_history / voice_history / recharge_records / consume_records / work_likes / work_comments / favorites
- 数据库连接配置在 [server/.env](file:///c:/Users/lijianlong/Documents/trae_projects/aitest/server/.env)（不要硬编码到代码里）

### 2. 后端 API

- **基础路径**：`/api/*`
- **统一响应格式**：
  ```json
  // 成功
  { "code": 200, "message": "success", "data": {...} }
  // 失败
  { "code": 400, "message": "错误描述", "data": null }
  ```
- **认证方式**：JWT Token，存放在 `Authorization: Bearer <token>` 头
- **密码哈希**：使用 **PBKDF2**（不要使用 bcrypt，会有 72 字节限制问题）
- **新增接口流程**：
  1. 在 [server/routes/](file:///c:/Users/lijianlong/Documents/trae_projects/aitest/server/routes/) 添加路由
  2. 在 [server/main.py](file:///c:/Users/lijianlong/Documents/trae_projects/aitest/server/main.py) 注册路由
  3. 使用 Pydantic 定义请求/响应模型
  4. 通过 [server/utils/auth_deps.py](file:///c:/Users/lijianlong/Documents/trae_projects/aitest/server/utils/auth_deps.py) 的 `get_current_user` 获取当前用户

### 3. 前端

- **端口**：`5173`
- **API 地址**：通过 Vite 代理转发到后端
  - `/api/*` → `http://localhost:8000`
- **状态管理**：使用 React Context API（不要引入 Redux / Zustand）
- **样式**：使用 TailwindCSS，**不要**写内联 style 或单独的 CSS 文件（除非全局样式）
- **API 调用**：统一通过 [web/src/services/api.js](file:///c:/Users/lijianlong/Documents/trae_projects/aitest/web/src/services/api.js)
- **登录状态**：通过 [web/src/contexts/UserContext.jsx](file:///c:/Users/lijianlong/Documents/trae_projects/aitest/web/src/contexts/UserContext.jsx) 管理
- **路由**：在 [web/src/App.jsx](file:///c:/Users/lijianlong/Documents/trae_projects/aitest/web/src/App.jsx) 中添加新路由

### 4. Agent 中台

- **作用**：大模型调用 + 复杂业务逻辑处理
- **独立进程**：默认不启动，前端如需 AI 能力可调用
- **新增 Agent**：
  1. 在 [agent/prompts/](file:///c:/Users/lijianlong/Documents/trae_projects/aitest/agent/prompts/) 写提示词
  2. 在 [agent/core/agent_registry.py](file:///c:/Users/lijianlong/Documents/trae_projects/aitest/agent/core/agent_registry.py) 注册
- **LLM 配置**：在 [agent/configs/config.yaml](file:///c:/Users/lijianlong/Documents/trae_projects/aitest/agent/configs/config.yaml) 中配置

## 严禁事项

### ❌ 不要做的事

1. **不要**使用 SQLite / 文件数据库代替 MySQL
2. **不要**修改 [.gitignore](file:///c:/Users/lijianlong/Documents/trae_projects/aitest/.gitignore) 来强制提交 node_modules / .env / 编译文件
3. **不要**把数据库密码、API Key 硬编码到代码中
4. **不要**使用 bcrypt 进行密码哈希（PBKDF2 已足够）
5. **不要**重新引入 Java 后端 / Spring Boot
6. **不要**创建新的框架（Redux、Zustand、Vue、Angular 等）
7. **不要**在没有启动 MySQL 的情况下让后端尝试连接
8. **不要**忽略前后端数据格式差异：后端返回 `{ code, message, data }`，前端 `api.js` 会自动 unwrap

### ⚠️ 修改前需确认

1. **修改数据库表结构**：影响所有现有数据，需先备份或迁移
2. **修改认证逻辑**：影响所有用户登录状态
3. **修改 API 路径**：需要同步更新前端的 api.js
4. **添加新的依赖**：需要在 [server/requirements.txt](file:///c:/Users/lijianlong/Documents/trae_projects/aitest/server/requirements.txt) 或 [web/package.json](file:///c:/Users/lijianlong/Documents/trae_projects/aitest/web/package.json) 中声明

## 常用命令

### 启动服务

```bash
# 启动 MySQL
docker-compose up -d

# 启动 Python 后端（启动时自动建表）
& "C:\Users\lijianlong\anaconda3\envs\llm\python.exe" "C:\Users\lijianlong\Documents\trae_projects\aitest\server\main.py"

# 启动前端
cd web
npm run dev
```

### 安装依赖

```bash
# Python
pip install -r server/requirements.txt

# Node
npm install  # 在 web/ 目录
```

### 测试 API

```bash
# 健康检查
curl http://localhost:8000/api/health

# 注册
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@test.com","password":"123456"}'

# 登录
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"123456"}'
```

### Git 操作

```bash
# 提交前检查
git status

# 添加文件
git add .

# 提交（推荐使用约定式提交）
git commit -m "feat: 添加用户充值接口"
git commit -m "fix: 修复登录状态丢失"
git commit -m "docs: 更新 API 文档"

# 推送
git push
```

## 提交规范

使用 [约定式提交](https://www.conventionalcommits.org/) 规范：

| 前缀 | 用途 | 示例 |
|------|------|------|
| `feat:` | 新功能 | `feat: 添加图片生成接口` |
| `fix:` | 修复 bug | `fix: 修复登录后余额不刷新` |
| `docs:` | 文档变更 | `docs: 更新 README` |
| `style:` | 格式调整（无逻辑变更）| `style: 格式化代码` |
| `refactor:` | 重构 | `refactor: 重构认证逻辑` |
| `test:` | 测试 | `test: 添加登录测试` |
| `chore:` | 构建/工具变更 | `chore: 更新依赖` |

## 调试指南

### 后端日志

后端启动时会在终端输出 SQL 日志（`sqlalchemy.engine.Engine`），可通过：
```python
# 在 config/database.py 中控制
echo=True   # 显示 SQL
echo=False  # 隐藏 SQL
```

### 前端调试

- 打开浏览器 DevTools 的 Network 面板查看 API 请求
- 打开 Console 查看 `api.js` 中的 `console.log('API 响应:', data)` 输出

### 常见问题

1. **登录不上**：检查后端是否启动、MySQL 是否运行、密码是否使用 PBKDF2
2. **CORS 错误**：后端已配置 CORS，但生产环境需收紧
3. **数据库表不存在**：检查后端启动日志，确认所有表都创建成功
4. **前端样式丢失**：检查 TailwindCSS 配置（postcss.config.js、tailwind.config.js）

## 注意事项

1. **项目使用 PowerShell 环境**（Windows），所有命令需要 PowerShell 兼容
2. **不要使用** `mkdir -p`、`rm -rf`、`ls -la` 等 Linux 命令
3. **使用** `New-Item`、`Remove-Item`、`Get-ChildItem` 等 PowerShell 命令
4. **Python 环境**：项目使用 conda 环境 `llm`
5. **MySQL 凭据**：`root` / `root123456` / `tick_ai` 数据库

## 联系方式

- **项目所有者**：lijianlong1
- **邮箱**：1436631592@qq.com
- **GitHub**：https://github.com/lijianlong1/tickai
