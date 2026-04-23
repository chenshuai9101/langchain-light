# LangChain Light 🎯

> 轻量级AI Agent编排框架 | 1个文件=1个概念 | 10行代码启动自己的AI助手

[//]: # (v2.0.0)

**核心定位**: 不是LangChain的全功能替代品，而是**99%的场景够用且学得快的精简版**。

## 5秒判断适不适合你

```
你用AI是为了快速完成任务 ✅ → 适合
你想研究AI框架的完整生态 ❌ → 不适合
```

## 安装

```bash
pip install langchain-light
# 或用源码（这个仓库）
git clone https://github.com/chenshuai9101/langchain-light
cd langchain-light
pip install -e .
```

## 配置

```bash
# 支持DeepSeek（推荐，国内可用）
export DEEPSEEK_API_KEY=sk-your-key-here

# 或OpenAI
export OPENAI_API_KEY=sk-your-key-here
```

> 💡 没有Key？去 [platform.deepseek.com](https://platform.deepseek.com) 注册，新用户送500万tokens。

## 改Key就能跑的示例

### 🚀 示例1：10秒测试是否通

```python
from langchain_light import LangChainLight

lcl = LangChainLight()
print(lcl.chat([{"role": "user", "content": "你好"}]))
```

### 🔧 示例2：让Agent使用工具

```python
from langchain_light import LangChainLight

lcl = LangChainLight()

# 注册工具（AI会自动选择使用哪个）
lcl.register_tool("搜索新闻", lambda q: f"关于'{q}'的最新报道", "搜索互联网新闻")
lcl.register_tool("数学计算", lambda x: str(eval(x)), "计算数学表达式")

# Agent: 帮你搜索
result = lcl.run_agent("搜索昨天的AI新闻")
print(result["result"])

# Agent: 帮你计算
result = lcl.run_agent("计算 2的10次方等于多少")
print(result["result"])
```

### 💬 示例3：流式对话（打字机效果）

```python
from langchain_light import LangChainLight

lcl = LangChainLight()
lcl.chat_stream(
    [{"role": "user", "content": "用三句话介绍自己"}],
    on_chunk=lambda text: print(text, end="", flush=True)
)
```

### 🔗 示例4：链式编排（多步骤任务）

```python
from langchain_light import LangChainLight
from langchain_light.core.chain_engine import ChainStep

lcl = LangChainLight()

lcl.create_chain("报告生成", [
    ChainStep(name="研究", prompt_template="研究{topic}", output_key="研究结果"),
    ChainStep(name="总结", prompt_template="总结: {研究结果}", output_key="总结结果"),
])

result = lcl.run_chain("报告生成", {"topic": "AI行业趋势"})
print(result)
```

## 错误处理指南

```
报错信息                      原因                     解决方案
────────────────────────────  ──────────────────      ────────────────────────
"未设置API Key"               API Key没配              设置DEEPSEEK_API_KEY
"网络错误: ..."               API不可达                 检查网络/代理配置
"HTTP 401/403"               API Key无效              检查Key是否正确
"HTTP 429"                   调用频率超限              等待后重试
"工具不存在: xxxx"           调用的工具未注册          先register_tool()再调用
```

## 命令行动手

```bash
# 对话
lcl chat "你好"

# Agent执行任务
lcl agent "搜索最近的AI新闻"

# 查看系统信息
lcl info
```

## 架构一览

```
langchain_light/
├── __init__.py          主类 LangChainLight
├── core/
│   ├── model_manager.py 模型管理 (DeepSeek/OpenAI/Ollama)
│   ├── agent_runtime.py Agent运行时 (Function Calling)
│   ├── chain_engine.py  链式编排
│   └── tool_registry.py 工具注册
├── cli.py               CLI入口
```

## 与LangChain的对比

如果你之前用过LangChain，这里是核心差异：

| 你的任务 | LangChain | LangChain Light |
|---------|----------|----------------|
| 学习时间 | 3-7天 | 5分钟 |
| 代码量 | 几十到几百行 | 5-20行 |
| 概念数 | 40+ | 5 |
| 对话 | ConversationBuffer | 直接调用chat() |
| 工具调用 | Function Calling | Function Calling ✅ |
| Agent | AgentExecutor | AgentRuntime.run() |
| 链 | LCEL | ChainEngine |
| 记忆 | 需要配置 | 无状态设计 |

## API速查

```python
LangChainLight(config?)           # 初始化
    .chat(messages)                # 对话 → str
    .chat_stream(messages, on_chunk) # 流式对话 → str
    .register_tool(name, func, desc) # 注册工具
    .run_agent(task)                # Agent执行 → dict
    .create_chain(name, steps)      # 创建链
    .run_chain(name, inputs)        # 执行链
    .switch_model(provider, model?) # 切换模型
    .get_info()                     # 系统信息
```

## License

MIT

---

## 💖 赞助支持

如果这个项目帮到了你，欢迎赞助支持——每一份心意都是前行的动力 🙏

<div align="center">
  <table>
    <tr>
      <td align="center">
        <img src="./assets/wechat.jpg" width="200" alt="微信支付">
        <br>
        <b>微信</b>
      </td>
      <td align="center">
        <img src="./assets/alipay.jpg" width="200" alt="支付宝">
        <br>
        <b>支付宝</b>
      </td>
    </tr>
  </table>
</div>
