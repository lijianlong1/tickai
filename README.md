# Tick-AI 项目

> 个人 AI 创作平台 - 集成多种 AI 能力的 Web 应用

## 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                      Tick-AI 系统架构                            │
└─────────────────────────────────────────────────────────────────┘

       ┌──────────────┐         ┌──────────────┐         ┌──────────────┐
       │   Web 前端   │  HTTP   │  Agent 中台  │  HTTP   │  Java 后端   │
       │   (React)    │ ──────> │   (Python)   │ ──────> │  (Spring)    │
       │  Port: 5173  │ <────── │  Port: 8000  │ <────── │  Port: 8080  │
       │              │         │              │         │              │
       │  web/        │         │  agent/      │         │  backend/    │
       └──────────────┘         └──────┬───────┘         └──────┬───────┘
                                       │                       │
                                       │ 调用 LLM              │ JDBC
                                       ▼                       ▼
                                ┌──────────────┐         ┌──────────────┐
                                │  大模型 API  │         │    MySQL     │
                                │ OpenAI/Qwen  │         │  Port: 3306  │
                                └──────────────┘         └──────────────┘
```

## 项目结构

```
aitest/
├── web/                # 前端 (React + Vite + TailwindCSS)
├── agent/              # Agent 中台 (Python + FastAPI)
├── backend/            # Java 后端 (Spring Boot)
├── docker-compose.yml  # 一键启动所有服务（待补充）
└── README.md           # 本文档
```

## 三大模块职责

### 1. Web 前端 (`web/`)
- 技术栈：React 18 + Vite + TailwindCSS + React Router
- 职责：用户界面、交互展示
- 端口：`5173`
- 详细文档：[web/README.md](web/README.md)

### 2. Agent 中台 (`agent/`)
- 技术栈：Python 3.9+ + FastAPI
- 职责：
  - **数据处理分析**（用户行为、社区趋势）
  - **大模型调用**（OpenAI / 通义 / 智谱）
  - **AI 智能体编排**（6 大 Agent）
  - **CLI 命令行工具**（复杂逻辑处理）
- 端口：`8000`
- 详细文档：[agent/README.md](agent/README.md)

### 3. Java 后端 (`backend/`)
- 技术栈：Spring Boot 3.2 + MyBatis Plus + MySQL 8
- 职责：
  - **数据库表的操作**（CRUD）
  - **复杂业务逻辑**（事务、权限、扣费）
  - **用户认证**（JWT + BCrypt）
- 端口：`8080`
- 数据库：`3306`（Docker 部署）
- 详细文档：[backend/README.md](backend/README.md)

## 核心特性

- 🎨 **个人主页**：动态轮播、科技感动画
- 🤖 **AI 创作工具**：
  - AI 漫剧制作
  - AI 图片生成
  - AI 文本创作
  - AI 语音合成
  - AI 音乐创作
- 👥 **社区功能**：
  - 作品展示（图片 / 视频分类）
  - 提示词分享
  - 点赞、评论、收藏
- 👤 **用户系统**：
  - 注册/登录
  - 创作者中心
  - 余额管理
  - 充值/消费记录
- 🤖 **智能化**（Agent 中台）：
  - 每日副业技巧
  - 内容审核
  - 个性化推荐
  - 创作提示词优化

## 数据库表

Java 后端管理的 10 张表：

| 表名 | 用途 |
|------|------|
| `users` | 用户表 |
| `works` | 社区作品表 |
| `prompts` | 提示词分享表 |
| `create_history` | 创作历史记录 |
| `voice_history` | 语音合成历史 |
| `recharge_records` | 充值记录 |
| `consume_records` | 消费记录 |
| `work_likes` | 作品点赞 |
| `work_comments` | 作品评论 |
| `favorites` | 收藏 |

## 快速开始

### 1. 启动 MySQL + Java 后端

```bash
cd backend/docker
docker-compose up -d
```

### 2. 启动 Agent 中台

```bash
# Linux/Mac
./agent/start.sh

# Windows
agent\start.bat
```

或手动启动：
```bash
cd agent
pip install -r requirements.txt
python -m agent serve
```

### 3. 启动前端

```bash
cd web
npm install
npm run dev
```

### 4. 访问应用

- 前端：http://localhost:5173
- Java 后端：http://localhost:8080/api
- Agent 中台：http://localhost:8000
- Agent 中台 API 文档：http://localhost:8000/docs

## 默认账号

| 邮箱 | 密码 | 角色 |
|------|------|------|
| admin@tickai.com | admin123 | 管理员 |
| test@tickai.com | 123456 | 普通用户 |

## 三个服务的交互关系

```
用户在浏览器操作
       │
       ▼
   Web 前端 (5173)
       │
       ├── 直接调用 Java 后端 (8080) 进行登录/注册/数据查询
       │
       └── 调用 Agent 中台 (8000) 进行 AI 智能操作
                  │
                  └── Agent 中台调用 Java 后端 (8080) 获取数据
                                  │
                                  ▼
                              MySQL (3306)
```

## 开发指南

### 添加新功能

1. **新增 AI 能力**：在 `agent/services/agents.py` 中实现新 Agent
2. **新增数据表**：在 `backend/docker/init.sql` 中加表，并在 Java 后端加对应 Entity/Service/Controller
3. **新增页面**：在 `web/src/pages/` 中加新页面

### 调用流程示例

**用户上传作品并希望 AI 优化提示词**：

1. 前端调用 Java 后端：`POST /api/community/works` 保存作品
2. 前端调用 Agent 中台：`POST /chat { agent: "image_generator", input: "优化这个提示词..." }`
3. Agent 中台调用 LLM API 进行处理
4. Agent 中台返回结果给前端
5. 前端展示给用户

## License

MIT
