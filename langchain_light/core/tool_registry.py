"""
工具注册中心
"""

import logging
from typing import Dict, List, Any, Callable

logger = logging.getLogger(__name__)


class ToolRegistry:
    """工具注册中心"""
    
    def __init__(self):
        self._tools: Dict[str, Dict] = {}
        logger.info("工具注册中心初始化")
    
    def register(self, name: str, func: Callable, description: str, parameters: Dict = None):
        """注册工具"""
        self._tools[name] = {
            "func": func,
            "description": description,
            "parameters": parameters or {},
        }
        logger.info(f"工具注册: {name}")
    
    def get(self, name: str) -> Callable:
        """获取工具"""
        tool = self._tools.get(name)
        if not tool:
            raise KeyError(f"工具不存在: {name}")
        return tool["func"]
    
    def execute(self, name: str, **kwargs) -> Any:
        """执行工具"""
        tool = self._tools.get(name)
        if not tool:
            return {"error": f"工具不存在: {name}"}
        try:
            result = tool["func"](**kwargs)
            logger.info(f"工具执行: {name} → 成功")
            return result
        except Exception as e:
            logger.error(f"工具执行失败: {name} → {e}")
            return {"error": str(e)}
    
    def list_tools(self) -> List[Dict]:
        return [{"name": n, "description": t["description"]} for n, t in self._tools.items()]
    
    def create_builtin_tools(self):
        """创建内置工具"""
        import datetime, json
        
        self.register("calculator", lambda expr: f"计算: {eval(expr)}" if __import__('re').match(r'^[\d+\-*/().\s]+$', expr) else "表达式无效", "执行数学计算")
        self.register("current_time", lambda: f"当前时间: {datetime.datetime.now()}", "获取当前时间")
        self.register("echo", lambda text: text, "回显输入文本")
