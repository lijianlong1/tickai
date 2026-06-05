# GitHub Spec Kit 使用指南

## 🎉 已完成初始化！

你的项目已成功配置 GitHub Spec Kit，可以开始使用规格驱动开发了！

## 📁 项目结构

```
aitest/
├── .github/
│   ├── agents/           # AI 代理配置文件
│   └── prompts/          # 提示词模板
├── .specify/
│   ├── extensions/       # 扩展（如 Git 集成）
│   ├── integrations/     # 集成配置（Copilot）
│   ├── memory/
│   │   └── constitution.md  # 项目原则（已配置）
│   ├── scripts/          # PowerShell 脚本
│   ├── templates/        # 文档模板
│   └── workflows/        # 工作流配置
└── SPEC_KIT_GUIDE.md     # 本文档
```

## 🚀 快速开始

### 核心命令

在你的 AI 编码助手（如 GitHub Copilot）中使用以下斜杠命令：

| 命令 | 功能 | 使用时机 |
|------|------|---------|
| `/speckit.constitution` | 查看/更新项目原则 | 开始新项目或修改原则时 |
| `/speckit.specify` | 创建功能规格文档 | 有新功能需求时 |
| `/speckit.plan` | 生成技术实现方案 | 规格确定后 |
| `/speckit.tasks` | 拆分成可执行任务 | 方案确定后 |
| `/speckit.implement` | 执行代码实现 | 任务清单就绪后 |

### 增强命令（可选）

| 命令 | 功能 |
|------|------|
| `/speckit.clarify` | 澄清需求中的模糊点 |
| `/speckit.analyze` | 检查文档一致性 |
| `/speckit.checklist` | 生成质量检查清单 |

### Git 相关命令

| 命令 | 功能 |
|------|------|
| `/speckit.git.initialize` | 初始化 Git 仓库 |
| `/speckit.git.feature` | 创建功能分支 |
| `/speckit.git.commit` | 提交更改 |
| `/speckit.git.validate` | 验证提交 |

## 💡 工作流示例

### 开发新功能的完整流程

**1. 制定规格**
```
输入: /speckit.specify
描述: 添加用户收藏作品功能
输出: specs/spec.md
```

**2. 澄清需求（可选）**
```
输入: /speckit.clarify
输出: 补充 spec.md 中的模糊点
```

**3. 制定技术方案**
```
输入: /speckit.plan
输出: plan.md + 相关技术文档
```

**4. 生成检查清单（可选）**
```
输入: /speckit.checklist
输出: 质量验证清单
```

**5. 拆分任务**
```
输入: /