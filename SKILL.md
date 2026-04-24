---
name: langchain-light
description: 轻量级AI Agent编排框架 - 1个文件=1个概念，10行代码启动自己的AI助手。非LangChain替代品，而是99%场景够用的精简版。
metadata:
  openclaw:
    emoji: 🎯
    aiFriendly: true
    plugAndPlay: true
    requires:
      minimal: true
      packages: ['python>=3.8']
    category: agent-framework
    tags: ['langchain', 'agent', 'framework', 'lightweight', 'ai-orchestration']
version: '2.0.0'
---

# LangChain Light 🎯

## 一、概述

LangChain Light 不是LangChain的全功能替代品，而是**99%的AI Agent场景够用且学得快的精简版**。核心设计原则是"1个文件=1个概念"。

### 适用场景
- ✅ 快速构建AI Agent / 工具链调用
- ✅ 聊天机器人 / RAG应用
- ✅ 批量文本处理管线
- ✅ 教学/学习AI Agent概念

### 不适用场景
- ❌ 需要LangChain完整生态插件
- ❌ 分布式高可用AI服务
- ❌ 复杂多模态流水线

## 二、安装

```bash
pip install langchain-light
# 或使用源码
git clone https://github.com/chenshuai9101/langchain-light
cd langchain-light
pip install -e .
```

## 三、快速开始

```python
from langchain_light import LangChainLight

lcl = LangChainLight()
# 10秒测试连接
print(lcl.chat([{"role": "user", "content": "你好"}]))

# 带工具的Agent
lcl.register_tool("搜索新闻", lambda q: f"关于'{q}'的最新报道")
result = lcl.chat_with_tools("今天有什么AI新闻？")
print(result)
```

## 四、结构化输出

本skill支持结构化输入输出：

```json
{
  "operation": "chat|chat_with_tools|batch_process",
  "messages": [{"role": "user", "content": "..."}],
  "options": {
    "model": "deepseek-chat",
    "temperature": 0.7,
    "retry_on_fail": true
  }
}
```

## 五、边界声明

### NOT FOR
- 需要LangChain完整生态插件的复杂场景
- 分布式高可用Agent集群
- 不具备API Key时的本地运行模式

### 触发词
- 用户需要快速构建AI Agent时
- 用户提及"简化版""精简""轻量"时

## 安装与兼容性

### 支持的平台
- ✅ **Claude Code** (v0.7.0+) - 作为Python库调用
- ✅ **OpenClaw** (v1.0.0+) - 通过skill机制加载
- ✅ **Codex CLI** (latest)
- ✅ **Cursor** (latest)
- 🟡 **纯命令行** - pip install 直接使用

### 安装方式

```bash
# Python包方式
pip install langchain-light

# Claude Code方式
claude mcp add chenshuai9101/langchain-light

# OpenClaw方式
clawhub install chenshuai9101/langchain-light
```
