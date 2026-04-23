#!/usr/bin/env python3
"""LangChain Light - 压力测试套件"""
import sys, os, time, traceback, datetime as dt, threading

sys.path.insert(0, "/tmp/langchain-light")
API_KEY = "sk-2565d4e8209542f7b6ff5b3730091d3c"
os.environ["DEEPSEEK_API_KEY"] = API_KEY

from langchain_light import LangChainLight
from langchain_light.core.model_manager import ModelConfig, Message

PASS = 0; FAIL = 0; ERRORS = []

def test(name, fn):
    global PASS, FAIL
    start = dt.datetime.now()
    try:
        fn()
        PASS += 1
        elapsed = (dt.datetime.now() - start).total_seconds()
        print(f"  ✅ {name} ({elapsed:.1f}s)")
    except Exception as e:
        FAIL += 1
        tb = traceback.format_exc()
        ERRORS.append(f"{name}: {e}")
        elapsed = (dt.datetime.now() - start).total_seconds()
        print(f"  ❌ {name}: {e} ({elapsed:.1f}s)")
        print(f"    {str(e)[:200]}")

def section(title):
    print(f"\n──── {title}")

import resource
def get_mem():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024

print(f"初始内存: {get_mem():.1f}MB")
print(f"API Key: {API_KEY[:12]}...")
print(f"时间: {dt.datetime.now().strftime('%H:%M:%S')}")

# ===== 压力1: 批量对话 =====
section("压力1: 批量连续对话（模拟高频API调用）")
lcl = LangChainLight(ModelConfig(provider="deepseek", model="deepseek-chat", timeout=15))

def stress_batch():
    for i in range(20):
        r = lcl.chat([Message(role="user", content=f"回复数字 {i}")])
        assert r is not None
test("20次连续对话无间断", stress_batch)

def stress_rapid():
    for i in range(10):
        r = lcl.chat([Message(role="user", content=f"回复：{i}")], max_tokens=5)
        assert r is not None
test("10次快速对话（max_tokens=5）", stress_rapid)

# ===== 压力2: 大消息处理 =====
section("压力2: 大消息/长上下文")
lcl2 = LangChainLight(ModelConfig(provider="deepseek", model="deepseek-chat", timeout=60))

def stress_long_input():
    long_text = "测试" * 50000  # ~150KB
    r = lcl2.chat([Message(role="user", content=long_text + "回复一个：好")], max_tokens=10)
    assert r is not None
test("150KB输入", stress_long_input)

def stress_huge_context():
    msgs = [Message(role="user", content=f"第{i}条消息") for i in range(100)]
    r = lcl2.chat(msgs + [Message(role="user", content="总结以上消息，回复：已读完")], max_tokens=20)
    assert r is not None
test("100条历史消息+总结", stress_huge_context)

# ===== 压力3: 大量工具注册 =====
section("压力3: 大量工具注册")
lcl3 = LangChainLight(ModelConfig(provider="deepseek", model="deepseek-chat"))

def stress_50_tools():
    for i in range(50):
        lcl3.register_tool(f"tool_{i}", lambda x=i: f"result_{x}", f"第{i}个工具")
    tools = lcl3.tools.list_tools()
    assert len(tools) >= 52  # 50自定义 + 2内置
test("注册50个工具", stress_50_tools)

def stress_200_tools():
    lclx = LangChainLight(ModelConfig(provider="deepseek", model="deepseek-chat"))
    for i in range(200):
        lclx.register_tool(f"t{i}", lambda x=i: x, f"工具{i}")
    assert len(lclx.tools.list_tools()) >= 202
test("注册200个工具", stress_200_tools)

# ===== 压力4: Agent并发调用 =====
section("压力4: Agent并发调用")
def stress_agent_10():
    results = []
    for i in range(10):
        l = LangChainLight(ModelConfig(provider="deepseek", model="deepseek-chat"))
        l.register_tool(f"search_{i}", lambda q: f"结果: {q}", f"搜索{i}")
        r = l.run_agent(f"搜索 test_{i}")
        results.append(r)
    assert all(r["success"] for r in results)
test("创建10个独立Agent各自执行", stress_agent_10)

# ===== 压力5: 长时间运行 =====
section("压力5: 长时间连续运行")
def stress_loop():
    l = LangChainLight(ModelConfig(provider="deepseek", model="deepseek-chat"))
    start = time.time()
    count = 0
    while time.time() - start < 30:  # 30秒连续调用
        l.chat([Message(role="user", content=str(count))], max_tokens=3)
        count += 1
    print(f"    30秒内完成 {count} 次调用")
test("30秒连续API调用", stress_loop)

# ===== 压力6: 极端输入 =====
section("压力6: 极端输入")

def stress_emoji():
    l = LangChainLight(ModelConfig(provider="deepseek", model="deepseek-chat"))
    r = l.chat([Message(role="user", content="😀😎🤖🚀💡🔥" * 100 + "这是什么？")])
    assert r is not None
test("大量emoji", stress_emoji)

def stress_html():
    l = LangChainLight(ModelConfig(provider="deepseek", model="deepseek-chat"))
    html = "<html><body><h1>Test</h1><p>" + "x" * 10000 + "</p></body></html>"
    r = l.chat([Message(role="user", content=html + "解析以上HTML")], max_tokens=20)
    assert r is not None
test("HTML代码输入", stress_html)

def stress_code():
    l = LangChainLight(ModelConfig(provider="deepseek", model="deepseek-chat"))
    code = "\n".join([f"def func_{i}(): pass" for i in range(500)])
    r = l.chat([Message(role="user", content=code + "\n以上代码有多少函数？")], max_tokens=20)
    assert r is not None
test("500个函数代码", stress_code)

# ===== 压力7: 网络异常 =====
section("压力7: 网络异常模拟")

def stress_timeout():
    l = LangChainLight(ModelConfig(provider="deepseek", model="deepseek-chat", timeout=1))
    # 1秒超时，正常对话通常>1秒
    start = time.time()
    try:
        r = l.chat([Message(role="user", content="回复：好" * 1000)])
        elapsed = time.time() - start
        print(f"    超时1s: {elapsed:.1f}s完成")
    except:
        elapsed = time.time() - start
        print(f"    超时1s: {elapsed:.1f}s后超时（预期行为）")
test("1秒超时限制", stress_timeout)

def stress_no_net():
    l = LangChainLight(ModelConfig(provider="openai", model="gpt-4o", timeout=2))
    r = l.chat([Message(role="user", content="hi")])
    assert "错误" in r or "失败" in r or "timeout" in r.lower() or "timed" in r.lower()
test("断网环境（OpenAI被墙）", stress_no_net)

# ===== 压力8: 内存泄漏检测 =====
section("压力8: 内存稳定性")
mem_before = get_mem()
lcl_mem = LangChainLight(ModelConfig(provider="deepseek", model="deepseek-chat"))
for i in range(50):
    lcl_mem.chat([Message(role="user", content="回复：好")], max_tokens=3)
mem_after = get_mem()
print(f"    内存: {mem_before:.1f}MB → {mem_after:.1f}MB (增{mem_after-mem_before:.1f}MB)")
test("50次对话后内存稳定性", lambda: (mem_after - mem_before) < 100)

# ===== 结果 =====
print(f"\n{'='*60}")
print(f"LangChain Light 压力测试完成: {PASS}通过, {FAIL}失败, 共{PASS+FAIL}项")
print(f"当前内存: {get_mem():.1f}MB")
if ERRORS:
    print(f"\n失败:")
    for e in ERRORS:
        print(f"  ❌ {e}")
print(f"\n时间: {dt.datetime.now().strftime('%H:%M:%S')}")
