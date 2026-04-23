"""快速开始示例"""

from langchain_light import LangChainLight

# 初始化
lcl = LangChainLight()

# 对话
result = lcl.chat([
    {"role": "system", "content": "你是一个助手"},
    {"role": "user", "content": "你好"},
])
print("对话:", result)

# 运行Agent
agent_result = lcl.run_agent("帮我处理数据")
print("Agent运行完成")
