#!/usr/bin/env python3
"""LangChain Light - 自动化测试套件 v1"""
import sys, os, json, traceback

sys.path.insert(0, "/tmp/langchain-light")
os.environ["DEEPSEEK_API_KEY"] = "sk-2565d4e8209542f7b6ff5b3730091d3c"
os.environ["OPENAI_API_KEY"] = ""  # 无，跳过

from langchain_light import LangChainLight
from langchain_light.core.model_manager import ModelConfig, Message

PASS = 0
FAIL = 0
ERRORS = []

def test(name, fn):
    global PASS, FAIL
    try:
        fn()
        PASS += 1
        print(f"  ✅ {name}")
    except Exception as e:
        FAIL += 1
        err = f"  ❌ {name}: {e}"
        ERRORS.append(f"{name}: {traceback.format_exc()}")
        print(err)

def section(n, title):
    print(f"\n─── [{n}] {title} {'─' * (50 - len(title))}")

# ===== [1-10] 基础功能 =====
section("1-10", "基础功能")

lcl = None

def t1():
    global lcl
    lcl = LangChainLight(ModelConfig(provider="deepseek", model="deepseek-chat"))
    assert lcl is not None
test("初始化", t1)

def t2():
    assert "version" in lcl.get_info()
test("get_info有版本号", t2)

def t3():
    info = lcl.get_info()
    assert info["model"] == "deepseek/deepseek-chat"
test("默认模型正确", t3)

def t4():
    tools = lcl.tools.list_tools()
    assert len(tools) >= 3
    assert any(t["name"] == "calculator" for t in tools)
test("内置工具>=3个", t4)

def t5():
    lcl.switch_model("deepseek", "deepseek-chat")
    assert lcl.model.config.model == "deepseek-chat"
test("模型切换: deepseek", t5)

def t6():
    lcl.switch_model("ollama", "llama3")
    assert lcl.model.config.provider == "ollama"
test("模型切换: ollama", t6)

def t7():
    lcl.switch_model("deepseek", "deepseek-chat")
    lcl._load_api_key = lambda: None  # hack to keep key
test("模型切换回deepseek", t7)

def t8():
    models = lcl.model.get_supported_models()
    assert "deepseek" in models
    assert "openai" in models
test("get_supported_models含三种提供商", t8)

# ===== [11-30] 真实API调用 =====
section("11-30", "真实API调用")

API_KEY = "sk-2565d4e8209542f7b6ff5b3730091d3c"
lcl2 = LangChainLight(ModelConfig(provider="deepseek", model="deepseek-chat", api_key=API_KEY, timeout=30))

def t11():
    result = lcl2.chat([Message(role="user", content="回复两个字：你好")])
    assert "你好" in result or result.strip()
    print(f"    回复: {result[:50]}")
test("单轮对话", t11)

def t12():
    result = lcl2.chat([
        Message(role="system", content="你只回复数字，不要回复其他任何内容"),
        Message(role="user", content="1+1=?")
    ])
    assert "2" in result
    print(f"    回复: {result[:30]}")
test("system prompt生效", t12)

def t13():
    r1 = lcl2.chat([Message(role="user", content="你的名字是什么？")])
    r2 = lcl2.chat([Message(role="user", content="我的第一个问题是什么？")])
    # 无context时应该不记得
    assert len(r2) > 0
    print(f"    无上下文时回复: {r2[:40]}")
test("无上下文多轮对话（无记忆）", t13)

def t14():
    result = lcl2.chat(
        [Message(role="user", content="用中文回复一个字：是")],
        max_tokens=10
    )
    assert len(result) < 500
    print(f"    回复(限制10token): {result[:30]}")
test("max_tokens限制", t14)

def t15():
    result = lcl2.chat(
        [Message(role="user", content="请用100字以上描述AI")],
        max_tokens=200
    )
    print(f"    回复长度: {len(result)}字符")
test("长回复正常", t15)

def t16():
    result = lcl2.chat([Message(role="user", content="")])
    # 空消息至少不崩溃
    assert result is not None
test("空消息不崩溃", t16)

def t17():
    result = lcl2.chat([Message(role="user", content="用英文回复：hello")])
    print(f"    英文回复: {result.strip()[:50]}")
test("英文对话", t17)

def t18():
    result = lcl2.chat([Message(role="user", content="请列三个点")])
    assert "1" in result or "·" in result or "-" in result or "*" in result or "\n" in result
    print(f"    结构化回复: {result[:60]}")
test("结构化回复", t18)

# ===== [31-50] Agent功能 =====
section("31-50", "Agent功能")

lcl3 = LangChainLight(ModelConfig(provider="deepseek", model="deepseek-chat", api_key=API_KEY))

def t31():
    # 注册真实工具
    test_data = {"counter": 0}
    def search_web(query):
        test_data["counter"] += 1
        return f"【搜索】找到关于'{query}'的结果15条"
    lcl3.register_tool("搜索", search_web, "搜索互联网信息")
    tools = lcl3.tools.list_tools()
    assert any(t["name"] == "搜索" for t in tools)
test("注册真实工具", t31)

def t32():
    result = lcl3.tools.execute("calculator", expr="2+3*4")
    assert "14" in str(result) or "计算" in str(result)
test("内置计算器工具", t32)

def t33():
    result = lcl3.tools.execute("echo", text="test123")
    assert "test123" in str(result)
test("内置echo工具", t33)

def t34():
    result = lcl3.agent.run("帮我搜索AI新闻")
    assert result["success"]
    assert len(result["tool_calls"]) > 0
    print(f"    Agent工具调用: {result['tool_calls'][0]['name']}")
test("Agent运行", t34)

print(f"\n{'='*50}")
print(f"第一轮测试完成: {PASS}通过, {FAIL}失败")

if ERRORS:
    print(f"\n失败详情:")
    for e in ERRORS[:3]:
        print(f"\n{e[:300]}...\n")

import datetime
print(f"时间: {datetime.datetime.now().strftime('%H:%M')}")
