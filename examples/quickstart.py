#!/usr/bin/env python3
"""
LangChain Light 快速上手
=======================
使用方法:
  1. 设置API Key: export DEEPSEEK_API_KEY=your_key_here
  2. 运行: python3 quickstart.py

不需要理解框架概念，改Key就能跑。
"""

import os, time

# ===== 第一步：设置 =====
API_KEY = os.environ.get("DEEPSEEK_API_KEY", "替换为你的Key")
if API_KEY == "替换为你的Key":
    print("⚠️  请先设置API Key")
    print("    export DEEPSEEK_API_KEY=sk-xxx")
    print("    或打开本文件编辑最后一行")
    exit(1)

# ===== 第二步：导入（唯一需要import的一行）=====
import sys
sys.path.insert(0, ".")  # 非pip安装时需要
from langchain_light import LangChainLight
from langchain_light.core.model_manager import ModelConfig

print("=" * 50)
print("  LangChain Light v2.0 - 快速上手")
print("=" * 50)
print()

# ===== 示例1：基础对话 =====
print("📝 示例1: 基础对话")
lcl = LangChainLight(ModelConfig(provider="deepseek"))
resp = lcl.chat([{"role": "user", "content": "用5个字形容LangChain Light"}])
print(f"  AI说: {resp}")
print()

# ===== 示例2：Agent + 工具 =====
print("🔧 示例2: Agent使用工具")
lcl2 = LangChainLight(ModelConfig(provider="deepseek"))
lcl2.register_tool("搜索新闻", lambda q: f"【新闻】关于'{q}'的最新报道", "搜索互联网新闻")
lcl2.register_tool("数学计算", lambda x: str(eval(x)), "执行数学计算")

# Agent会自动判断该用什么工具
for task in ["搜索最近的AI新闻", "计算 2的10次方是多少", "你好啊"]:
    result = lcl2.run_agent(task)
    if result["success"] and result["tool_calls"]:
        tool_name = result["tool_calls"][0]["name"]
        tool_res = result["tool_calls"][0]["result"]
        print(f"  任务: {task}")
        print(f"    选择了: {tool_name} → {tool_res}")
    elif result["success"]:
        print(f"  任务: {task}")
        print(f"    回复: {result['result'][:50]}")
    else:
        print(f"  任务: {task}")
        print(f"    失败: {result.get('error', '未知错误')}")
print()

# ===== 示例3：流式输出（打字机效果）=====
print("⌨️  示例3: 流式输出（打字机效果）")
lcl3 = LangChainLight(ModelConfig(provider="deepseek"))
print("  AI说: ", end="", flush=True)
full_text = ""
def on_chunk(text):
    global full_text
    full_text += text
    print(text, end="", flush=True)
    time.sleep(0.02)
lcl3.chat_stream(
    [{"role": "user", "content": "用一句话总结什么是AI Agent"}],
    on_chunk=on_chunk,
)
print()
print()

# ===== 示例4：链式编排 =====
print("🔗 示例4: 链式编排（多步骤）")
from langchain_light.core.chain_engine import ChainStep
lcl4 = LangChainLight(ModelConfig(provider="deepseek"))
lcl4.create_chain("研究流程", [
    ChainStep(name="资料收集", prompt_template="收集{topic}的资料", output_key="资料"),
    ChainStep(name="整理输出", prompt_template="整理: {资料}", output_key="结果"),
])
result = lcl4.run_chain("研究流程", {"topic": "AI Agent"})
print(f"  步骤结果: {result.get('资料', 'N/A')[:50]}...")
print(f"  汇总: {result.get('结果', 'N/A')[:50]}...")
print()

# ===== 信息 =====
info = lcl.get_info()
print("=" * 50)
print(f"  LangChain Light v{info['version']}")
print(f"  模型: {info['model']}")
print(f"  工具数: {len(info['tools'])} (含内置)")
print(f"  内置工具: {', '.join(t['name'] for t in info['tools'])}")
print("=" * 50)
print("✅ 全部通过！欢迎使用 LangChain Light")
print()
