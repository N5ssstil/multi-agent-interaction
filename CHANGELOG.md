# 变更日志

所有重要的变更都会记录在这个文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### 计划中
- Web UI 界面
- 更多 LLM 提供商支持
- Agent 可视化监控

## [0.1.0] - 2026-02-27

### 新增
- ✨ 核心 Agent 基类，支持消息收发和任务执行
- ✨ MessageBus 消息总线，支持点对点和广播通信
- ✨ Orchestrator 编排器，支持顺序/并行任务编排
- ✨ Tools 工具系统，支持自定义工具注册和调用
- ✨ Memory 记忆系统，支持短期/长期记忆和共享状态
- ✨ LLMAgent 类，支持 OpenAI/Anthropic API 集成
- ✨ ToolEnabledAgent，支持 LLM 工具调用
- ✨ OpenClawAgent 适配器，支持将 OpenClaw 接入框架
- 📝 完整的 README 文档
- 📝 CONTRIBUTING 贡献指南
- 🧪 基础测试用例
- 📦 示例代码

### 架构
```
multi_agent/
├── agent.py          # Agent 基类
├── message.py        # 消息系统
├── orchestrator.py   # 任务编排
├── tools.py          # 工具系统
├── memory.py         # 记忆系统
└── llm_agent.py      # LLM Agent
```

---

## 版本说明

- **[Major]**: 不兼容的 API 变更
- **[Minor]**: 向后兼容的功能新增
- **[Patch]**: 向后兼容的问题修复