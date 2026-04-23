"""Agent使用示例"""

import sys
sys.path.insert(0, "/tmp/langchain-light")

from langchain_light import LangChainLight

# 1. 初始化
lcl = LangChainLight()
print("=" * 50)

# 2. 注册自定义工具
def search_web(query):
    return f"【搜索结果】找到{len(query)}条相关结果"

def calculate(expr):
    try:
        return f"结果: {eval(expr)}"
    except:
        return "表达式无效"

lcl.register_tool("搜索网页", search_web, "搜索互联网信息")
lcl.register_tool("计算器", calculate, "执行数学计算")

print("\n📦 已注册工具:")
for t in lcl.tools.list_tools():
    print(f"  - {t['name']}: {t['description']}")

# 3. 运行Agent
print("\n🚀 运行Agent:")
result = lcl.run_agent("搜索AI新闻并计算阅读量")
print(f"  ✓ 任务完成")
print(f"  ✓ 迭代次数: {result['iterations']}")
print(f"  ✓ 结果: {result['result'][:50]}")

# 4. 查看信息
print("\n📊 系统信息:")
info = lcl.get_info()
print(f"  版本: {info['version']}")
print(f"  模型: {info['model']}")
print(f"  工具数: {len(info['tools'])}")

print("\n" + "=" * 50)
print("✅ LangChain Light 运行成功!")
