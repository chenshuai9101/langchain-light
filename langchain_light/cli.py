#!/usr/bin/env python3
"""LangChain Light CLI - 命令行快速体验"""

import sys, os


def main():
    """CLI入口"""
    args = sys.argv[1:]

    if "--help" in args or "-h" in args or not args:
        print("LangChain Light CLI v2.0.0")
        print()
        print("用法:")
        print("  lcl chat <消息>           单次对话")
        print("  lcl agent <任务>          Agent执行任务")
        print("  lcl info                 查看系统信息")
        print()
        print("环境变量:")
        print("  DEEPSEEK_API_KEY          DeepSeek API Key")
        print("  OPENAI_API_KEY            OpenAI API Key")
        print()
        return

    cmd = args[0]

    if cmd == "chat":
        message = " ".join(args[1:]) or "你好"
        _chat(message)
    elif cmd == "agent":
        task = " ".join(args[1:]) or "搜索最新AI新闻"
        _agent(task)
    elif cmd == "info":
        _info()
    else:
        print(f"未知命令: {cmd}")


def _ensure_key():
    key = os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not key:
        print("错误: 未设置API Key")
        print("请设置环境变量: export DEEPSEEK_API_KEY=your_key_here")
        sys.exit(1)
    return key


def _chat(message):
    from langchain_light.core.model_manager import ModelManager, ModelConfig, Message
    key = _ensure_key()
    provider = "deepseek" if os.environ.get("DEEPSEEK_API_KEY") else "openai"
    mm = ModelManager(ModelConfig(provider=provider, api_key=key))

    print(f">>> {message}")
    print("---")
    result = mm.chat([Message(role="user", content=message)])
    print(result)


def _agent(task):
    from langchain_light import LangChainLight
    from langchain_light.core.model_manager import ModelConfig
    _ensure_key()
    lcl = LangChainLight(ModelConfig(provider="deepseek"))

    # 注册实用工具
    lcl.register_tool("search_web", lambda q: f"【搜索结果】关于'{q}'找到25条相关信息", "搜索互联网信息")
    lcl.register_tool("calculator", lambda x: str(eval(x)), "数学计算")

    print(f">>> Agent任务: {task}")
    print("---")
    result = lcl.run_agent(task)
    print(f"完成: {result['success']}")
    if result.get("tool_calls"):
        for tc in result["tool_calls"]:
            print(f"  调用工具: {tc['name']} → {tc['result'][:80]}")
    elif result.get("result"):
        print(f"  回复: {result['result'][:100]}")


def _info():
    from langchain_light import LangChainLight
    from langchain_light.core.model_manager import ModelConfig
    lcl = LangChainLight(ModelConfig(provider="deepseek"))
    info = lcl.get_info()
    print(f"LangChain Light v{info['version']}")
    print(f"模型: {info['model']}")
    print(f"工具数: {len(info['tools'])}")
    for t in info["tools"]:
        print(f"  - {t['name']}: {t['description']}")
    print(f"链数: {len(info['chains'])}")


if __name__ == "__main__":
    main()
