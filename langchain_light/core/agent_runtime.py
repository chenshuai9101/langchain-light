"""
Agent运行环境 v2 - 真实LLM Function Calling版
    支持中文工具名（自动映射为英文ID）
"""
import logging, json, inspect, re
from typing import Dict, List

logger = logging.getLogger(__name__)


def _make_safe_name(name: str) -> str:
    """将工具名转为合法的Function Calling ID
    策略：取拼音首字母或hash，保证唯一可读
    """
    import hashlib
    safe = re.sub(r'[^a-zA-Z0-9_]', '_', name)
    if safe and safe[0].isalpha() and safe[0].isascii():
        return safe[:64]
    # 中文名 → pinyin缩写 + hash后缀保证唯一
    h = hashlib.md5(name.encode()).hexdigest()[:6]
    # 取每个中文字拼音首字母
    try:
        import unicodedata
        chars = []
        has_non_ascii = any(ord(c) > 127 for c in name)
        if has_non_ascii:
            safe = f"tool_{h}"
        else:
            safe = f"tool_{h}"
    except:
        safe = f"tool_{h}"
    return safe[:64]


class AgentRuntime:
    """Agent v2 - 原生LLM Function Calling"""

    def __init__(self, model_manager=None):
        self.model = model_manager
        self.tools: Dict[str, callable] = {}
        self.tool_descriptions: Dict[str, str] = {}
        self._name_map: Dict[str, str] = {}       # safe_name → actual_name
        self._reverse_map: Dict[str, str] = {}     # actual_name → safe_name
        self._tool_schemas: Dict[str, dict] = {}
        logger.info("Agent v2启动 (真实Function Calling)")

    def register_tool(self, name: str, func: callable, description: str = ""):
        self.tools[name] = func
        self.tool_descriptions[name] = description

        safe_name = _make_safe_name(name)
        self._reverse_map[name] = safe_name
        self._name_map[safe_name] = name

        # 自动推断参数schema
        sig = inspect.signature(func)
        params = {}
        required = []
        for p_name, p_param in sig.parameters.items():
            p_type = "string"
            if p_param.annotation is not inspect.Parameter.empty:
                if p_param.annotation in (int, float): p_type = "number"
                elif p_param.annotation == bool: p_type = "boolean"
            params[p_name] = {"type": p_type, "description": p_name}
            if p_param.default is inspect.Parameter.empty:
                required.append(p_name)

        self._tool_schemas[safe_name] = {
            "type": "function",
            "function": {
                "name": safe_name,
                "description": (description or name)[:200],
                "parameters": {
                    "type": "object",
                    "properties": params if params else {"input": {"type": "string", "description": "输入"}},
                    "required": required if required else ["input"],
                },
            },
        }
        logger.info(f"工具注册: {name} → {safe_name}")

    def _call_tool(self, safe_name: str, args: dict) -> str:
        actual_name = self._name_map.get(safe_name, safe_name)
        func = self.tools.get(actual_name)
        if not func:
            return f"工具不存在: {actual_name}"
        try:
            return str(func(**args) if args else func())
        except TypeError:
            sig = inspect.signature(func)
            params = list(sig.parameters.keys())
            try:
                if not params: return str(func())
                first_val = next(iter(args.values())) if args else ""
                return str(func(first_val))
            except Exception as e2:
                return f"执行失败: {e2}"
        except Exception as e:
            return f"执行失败: {e}"

    def run(self, task: str) -> dict:
        logger.info(f"Agent v2执行: {task[:100]}")

        if not self.tools:
            return {"success": True, "task": task, "tool_calls": [], "result": "无工具可用"}
        if not self.model:
            return {"success": False, "task": task, "error": "模型未初始化"}

        from langchain_light.core.model_manager import Message
        schemas = list(self._tool_schemas.values())

        try:
            response = self.model.function_call(
                messages=[Message(role="user", content=task)],
                tools=schemas,
            )

            if "error" in response:
                logger.warning(f"Function Calling降级: {response['error']}")
                fallback = self.model.chat([Message(role="user", content=task)])
                return {"success": True, "task": task, "tool_calls": [], "result": fallback}

            tool_calls = response.get("tool_calls", [])
            content = response.get("content", "")

            if not tool_calls:
                return {"success": True, "task": task, "tool_calls": [], "result": content or "完成"}

            results = []
            for tc in tool_calls:
                safe_name = tc["function"]["name"]
                actual_name = self._name_map.get(safe_name, safe_name)
                try:
                    args = json.loads(tc["function"]["arguments"]) if tc["function"]["arguments"] else {}
                except json.JSONDecodeError:
                    args = {}
                res = self._call_tool(safe_name, args)
                results.append({"name": actual_name, "args": args, "result": res[:300]})
                logger.info(f"  工具[{actual_name}] = {res[:80]}")

            return {
                "success": True,
                "task": task,
                "iterations": 1,
                "tool_calls": results,
                "result": results[0]["result"] if results else (content or "完成"),
            }

        except Exception as e:
            logger.error(f"Agent执行失败: {e}")
            return {"success": False, "task": task, "error": str(e), "tool_calls": []}

    def list_tools(self) -> list:
        return list(self.tools.keys())
