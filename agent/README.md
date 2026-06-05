# Tick-AI Agent 中台

> 承担数据处理分析 + 大模型调用 + 智能化能力的核心服务

## 定位

**Agent 中台**是整个系统的智能化核心，与 Java 后端职责分明：
- **Java 后端**：负责数据库表的操作和复杂业务逻辑（CRUD、事务、权限）
- **Agent 中台**：负责数据处理分析、大模型调用、AI 智能体编排

## 技术栈

- Python 3.9+
- FastAPI（HTTP 服务）
- OpenAI Python SDK（兼容通义、智谱、DeepSeek 等）
- httpx（异步 HTTP 客户端，与 Java 后端通信）
- PyYAML（配置管理）

## 核心能力

### 1. 六大智能体（Agent）
- **AI 漫剧导演**（comic_creator）- 漫剧剧本创作和分镜设计
- **AI 图像大师**（image_generator）- 图片生成提示词优化
- **AI 写作助手**（text_writer）- 各类文本内容创作、副业技巧
- **AI 语音导演**（voice_director）- 语音合成参数优化
- **AI 音乐家**（music_composer）- 音乐创作和编曲
- **社区审核员**（community_moderator）- 内容审核和质量评估

### 2. 数据分析
- 用户行为分析
- 社区趋势分析
- 用户报告生成

### 3. 大模型调用
- 支持 OpenAI / 通义千问 / 智谱 GLM / DeepSeek
- 统一接口，动态切换
- 流式输出支持

## 项目结构

```
agent/
├── core/                      # 核心模块
│   ├── config_loader.py      # 配置加载器
│   ├── llm_client.py         # LLM 统一客户端
│   ├── base_agent.py         # Agent 基类
│   └── agent_registry.py     # Agent 注册中心
├── services/                  # 业务服务
│   ├── backend_client.py     # Java 后端 API 客户端
│   ├── data_analyzer.py      # 数据分析器
│   └── agents.py             # 具体 Agent 实现
├── cli/                       # CLI 命令行
│   ├── main.py               # CLI 入口
│   └── server.py             # HTTP 服务
├── prompts/                   # 提示词模板
│   ├── comic_creator.txt
│   ├── image_generator.txt
│   ├── text_writer.txt
│   ├── voice_director.txt
│   ├── music_composer.txt
│   └── community_moderator.txt
├── configs/
│   └── config.yaml           # 配置文件
├── logs/                      # 日志
├── data/                      # 缓存数据
├── requirements.txt          # 依赖
├── start.sh                  # Linux/Mac 启动
└── start.bat                 # Windows 启动
```

## 快速开始

### 1. 安装依赖
```bash
# Linux/Mac
./agent/start.sh

# Windows
agent\start.bat
```

### 2. CLI 模式

#### 查看帮助
```bash
python -m agent --help
```

#### 查看可用 Agent
```bash
python -m agent list
```

#### 与 Agent 对话
```bash
python -m agent chat --agent text_writer --input "写一篇关于 AI 绘画的文章"
```

#### 用户登录
```bash
python -m agent login --email user@example.com --password 123456
```

#### 分析用户行为
```bash
python -m agent analyze-user --user-id 1
```

#### 分析社区趋势
```bash
python -m agent analyze-community
```

#### 内容生成
```bash
python -m agent generate --type text --input "AI 创作的未来"
```

#### 生成每日副业技巧
```bash
python -m agent tips
```

#### 内容审核
```bash
python -m agent moderate --title "测试" --content "测试内容"
```

### 3. HTTP 服务模式

#### 启动服务
```bash
python -m agent serve
# 或
python -m agent.cli.server
```

服务地址：http://localhost:8000

#### API 文档
http://localhost:8000/docs

#### 主要 API

| 路径 | 方法 | 说明 |
|------|------|------|
| `/agents` | GET | 列出所有 Agent |
| `/chat` | POST | 与 Agent 对话 |
| `/chat/stream` | POST | 流式对话（SSE） |
| `/generate` | POST | 内容生成 |
| `/tips` | POST | 每日副业技巧 |
| `/moderate` | POST | 内容审核 |
| `/analyze/user` | POST | 用户行为分析 |
| `/analyze/community` | POST | 社区趋势分析 |

#### API 调用示例

```bash
# 与 Agent 对话
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"agent": "text_writer", "input": "写一首诗"}'

# 内容生成
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"type": "text", "input": "AI 创作的未来"}'

# 每日副业技巧
curl -X POST http://localhost:8000/tips \
  -H "Content-Type: application/json" \
  -d '{"count": 5}'
```

## 架构关系

```
┌──────────────┐     HTTP      ┌──────────────┐    HTTP     ┌──────────────┐
│   Web 前端   │ ───────────>  │  Agent 中台  │ ──────────> │  Java 后端   │
│  (React)     │  <─────────── │  (Python)    │  <──────────│  (Spring)    │
│  Port: 5173  │               │  Port: 8000  │             │  Port: 8080  │
└──────────────┘               └──────────────┘             └──────────────┘
                                      │                              │
                                      │ 调用 LLM                     │ 操作 MySQL
                                      ▼                              ▼
                              ┌──────────────┐             ┌──────────────┐
                              │  大模型 API  │             │    MySQL     │
                              │ OpenAI/Qwen  │             │  Port: 3306  │
                              └──────────────┘             └──────────────┘
```

**职责划分**：
- **Web 前端**：UI 展示、用户交互
- **Agent 中台**：AI 智能化、数据分析、大模型调用
- **Java 后端**：数据库 CRUD、复杂业务逻辑、权限管理
- **MySQL**：数据持久化

## 配置

修改 `configs/config.yaml`：

```yaml
# LLM 提供方
llm:
  default_provider: "openai"
  providers:
    openai:
      api_key: "${OPENAI_API_KEY}"
      model: "gpt-4o-mini"

# 后端地址
backend:
  base_url: "http://localhost:8080/api"
```

通过环境变量注入敏感信息：
```bash
export OPENAI_API_KEY="sk-xxx"
export DASHSCOPE_API_KEY="sk-xxx"
```

## 开发

### 添加新 Agent

1. 在 `services/agents.py` 中实现 Agent 类（继承 BaseAgent）
2. 在 `services/__init__.py` 中注册
3. 在 `prompts/` 中添加系统提示词
4. 在 `configs/config.yaml` 中添加配置

```python
class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_id="my_agent", name="我的智能体")
        self.load_system_prompt()
    
    async def my_method(self, input: str) -> str:
        return await self.run(input)
```

### 添加新 CLI 命令

在 `cli/main.py` 中添加：
```python
async def cmd_my_command(self, args):
    # 实现逻辑
    pass
```

## 监控

日志文件：`logs/agent.log`

支持的日志级别：DEBUG / INFO / WARNING / ERROR
