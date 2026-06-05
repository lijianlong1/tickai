# Tick-AI 项目

> 个人 AI 创作平台 - 集成多种 AI 能力的 Web 应用

## 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                      Tick-AI 系统架构                            │
└─────────────────────────────────────────────────────────────────┘

       ┌──────────────┐         ┌──────────────────────┐         ┌──────────────┐
       │   Web 前端   │  HTTP   │   Python 后端        │  SQL    │    MySQL     │
       │   (React)    │ ──────> │  (FastAPI + Agent)   │ ──────> │  Port: 3306  │
       │  Port: 5173  │ <────── │    Port: 8000        │ <────── │              │
       │              │         │                      │         │              │
       │  web/        │         │  server/  +  agent/  │         │  Docker      │
       └──────────────┘         └──────────┬───────────┘         └──────────────┘
                                           │
                                           │ 调用 LLM
                                           ▼
                                    ┌──────────────┐
                                    │  大模型 API  │
                                    │ OpenAI/Qwen  │
                                    │ 智谱 / 通义  │
                                    └──────────────┘
```

## 项目结构

```
aitest/
├── web/                # 前端 (React + Vite + TailwindCSS)
├── server/             # Python 后端 - 数据库 CRUD + 业务逻辑
├── agent/              # Python Agent 中台 - 大模型调用 + 智能体
├── docker-compose.yml  # 一键启动 MySQL
├── .gitignore          # Git 忽略规则
└── README.md           # 本文档
```

## 三大模块职责

### 1. Web 前端 (`web/`)
- **技术栈**：React 18 + Vite + TailwindCSS + React Router
- **职责**：用户界面、交互展示
- **端口**：`5173`
- **目录结构**：
  ```
  web/
  ├── src/
  │   ├── pages/        # 页面组件
  │   ├── components/   # 公共组件
  │   ├── contexts/     # 全局状态
  │   └── services/     # API 调用
  └── package.json
  ```

### 2. Python 后端 (`server/`) ⭐ 核心服务
- **技术栈**：Python 3.9+ + FastAPI + SQLAlchemy + asyncmy
- **职责**：
  - **数据库表操作**（10 张表 CRUD）
  - **用户认证**（JWT + PBKDF2 密码哈希）
  - **业务逻辑**（充值、消费、扣费、事务）
  - **自动建表**（启动时自动创建数据库表）
- **端口**：`8000`
- **API 文档**：`http://localhost:8000/docs`

### 3. Python Agent 中台 (`agent/`)
- **技术栈**：Python 3.9+ + FastAPI + OpenAI SDK
- **职责**：
  - **大模型调用**（OpenAI / 通义千问 / 智谱 GLM）
  - **AI 智能体编排**（6 大 Agent）
  - **数据处理分析**（用户行为、社区趋势）
  - **CLI 命令行工具**（复杂逻辑处理）
- **入口**：`python -m agent serve` 或 `python -m agent chat`
- **6 大 Agent**：
  1. `comic_creator` - AI 漫剧创作
  2. `image_generator` - AI 图片生成
  3. `text_writer` - AI 文本创作
  4. `voice_director` - AI 语音合成
  5. `music_composer` - AI 音乐创作
  6. `community_moderator` - 社区内容审核

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
  - 注册 / 登录（JWT 认证）
  - 创作者中心
  - 余额管理
  - 充值 / 消费记录
- 🤖 **智能化**（Agent 中台）：
  - 每日副业技巧
  - 内容审核
  - 个性化推荐
  - 创作提示词优化

## 数据库表（10 张）

由 Python 后端自动创建（启动时执行）：

| 表名 | 用途 |
|------|------|
| `users` | 用户表（账号、密码、余额、角色）|
| `works` | 社区作品表（标题、内容、作者、分类）|
| `prompts` | 提示词分享表（提示词、模型参数）|
| `create_history` | 创作历史记录 |
| `voice_history` | 语音合成历史 |
| `recharge_records` | 充值记录 |
| `consume_records` | 消费记录 |
| `work_likes` | 作品点赞关联表 |
| `work_comments` | 作品评论表 |
| `favorites` | 收藏表 |

## 快速开始

### 环境要求
- Python 3.9+（推荐 3.10）
- Node.js 18+
- Docker Desktop（运行 MySQL）

### 1. 启动 MySQL

```bash
docker-compose up -d
```

### 2. 启动 Python 后端

```bash
# 创建并激活 conda 环境（首次）
conda create -n tick-ai python=3.10 -y
conda activate tick-ai

# 安装依赖
cd server
pip install -r requirements.txt

# 配置环境变量（参考 .env.example）
copy .env.example .env
# 编辑 .env，填入数据库密码

# 启动后端（启动时自动创建表）
cd ..
& "C:\Users\lijianlong\anaconda3\envs\llm\python.exe" "server\main.py"
```

后端启动后：
- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/api/health

### 3. 启动 Agent 中台（可选）

```bash
# 在新的终端中
cd agent
pip install -r requirements.txt

# 配置 LLM（在 configs/config.yaml 中填入 API Key）
# 然后启动：
python -m agent serve
```

### 4. 启动前端

```bash
cd web
npm install
npm run dev
```

### 5. 访问应用

- **前端**：http://localhost:5173
- **Python 后端**：http://localhost:8000
- **API 文档**：http://localhost:8000/docs
- **Agent 中台**：http://localhost:8001（启动后）

## 测试账号

通过前端注册接口或后端 API 创建：

| 邮箱 | 密码 | 备注 |
|------|------|------|
| `test@example.com` | `123456` | 已通过 API 注册的测试用户 |

**注册接口示例**：
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"你的用户名","email":"你的邮箱","password":"你的密码"}'
```

## 服务交互关系

```
用户在浏览器操作
       │
       ▼
   Web 前端 (5173)
       │
       │ HTTP /api/...
       ▼
   Python 后端 (8000) ──SQL──> MySQL (3306)
       │
       │ HTTP (如需 AI 能力)
       ▼
   Agent 中台 (8001) ──HTTPS──> 大模型 API
   (OpenAI / 通义 / 智谱)
```

## API 接口分类

### 认证
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `GET  /api/auth/me` - 获取当前用户信息

### 用户
- `PUT  /api/user/update` - 更新用户信息
- `POST /api/user/recharge?amount=100` - 用户充值
- `GET  /api/user/balance` - 查询余额
- `GET  /api/user/recharge-records` - 充值记录
- `GET  /api/user/consume-records` - 消费记录

### 作品
- `GET    /api/works?type=image` - 作品列表
- `POST   /api/works` - 创建作品
- `GET    /api/works/{id}` - 作品详情
- `PUT    /api/works/{id}` - 更新作品
- `DELETE /api/works/{id}` - 删除作品
- `POST   /api/works/{id}/like` - 点赞
- `POST   /api/works/{id}/favorite` - 收藏
- `GET    /api/works/{id}/comments` - 评论列表
- `POST   /api/works/{id}/comments` - 发表评论

### 提示词
- `GET    /api/prompts` - 提示词列表
- `POST   /api/prompts` - 分享提示词
- `GET    /api/prompts/{id}` - 提示词详情
- `DELETE /api/prompts/{id}` - 删除提示词

### 创作历史
- `GET  /api/create-history` - 历史列表
- `POST /api/create-history` - 保存记录

### 语音历史
- `GET    /api/voice-history` - 列表
- `POST   /api/voice-history` - 保存
- `DELETE /api/voice-history/{id}` - 删除

## 开发指南

### 添加新功能

1. **新增 AI 能力**：
   - 在 `agent/prompts/` 中添加新的提示词文件
   - 在 `agent/core/agent_registry.py` 中注册新 Agent

2. **新增数据表**：
   - 在 `server/models/` 中添加新的 SQLAlchemy 模型
   - 在 `server/routes/` 中添加对应的路由
   - 重启后端服务（自动建表）

3. **新增页面**：
   - 在 `web/src/pages/` 中添加新的 React 组件
   - 在 `web/src/App.jsx` 中配置路由

### 调用流程示例

**用户注册流程**：
```
1. 前端调用 Python 后端：POST /api/auth/register
2. 后端验证邮箱唯一性
3. 后端对密码进行 PBKDF2 哈希
4. 后端将用户写入 MySQL
5. 后端生成 JWT Token 返回给前端
6. 前端保存 Token 到 localStorage
```

**用户充值流程**：
```
1. 前端调用 Python 后端：POST /api/user/recharge?amount=100
2. 后端验证用户身份（JWT）
3. 后端开启数据库事务
4. 后端更新用户余额
5. 后端插入充值记录
6. 后端提交事务
7. 返回新的余额给前端
```

## 技术栈

### 前端
- React 19
- Vite 8
- TailwindCSS 4
- React Router 7
- React Context API（状态管理）

### 后端
- Python 3.10
- FastAPI（Web 框架）
- SQLAlchemy（ORM）
- asyncmy（MySQL 异步驱动）
- python-jose（JWT）
- passlib（密码哈希）
- pydantic（数据验证）

### 数据库
- MySQL 8.0（Docker 部署）

### AI 集成
- OpenAI Python SDK
- 通义千问 Dashscope
- 智谱 GLM

## 部署说明

### 开发环境
- 前端：`npm run dev`（HMR 热更新）
- 后端：`uvicorn main:app --reload`（自动重载）
- 数据库：Docker Compose

### 生产环境（待补充）
- 前端：`npm run build` 产出 `dist/`，由 Nginx 托管
- 后端：Gunicorn + Uvicorn workers
- 数据库：独立 MySQL 服务或云数据库

## License

MIT
