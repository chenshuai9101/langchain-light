"""LangChain Light - 轻量级AI Agent框架"""

__version__ = "1.0.0"
__author__ = "牧云野"
__license__ = "MIT"

from .core import ModelManager, ChainEngine, AgentRuntime, ToolRegistry
from .core.model_manager import ModelConfig, Message


class LangChainLight:
    """LangChain Light 主类"""
    
    def __init__(self, config: ModelConfig = None):
        self.model = ModelManager(config)
        self.chains = ChainEngine()
        self.tools = ToolRegistry()
        self.agent = AgentRuntime(self.model)
        
        # 注册内置工具（名字唯一，避免与自定义混淆）
        self._register_builtin_tools()
        
        print(f"LangChain Light v{__version__} 初始化完成")
        print(f"  模型: {config.provider if config else 'openai'}")
        print(f"  工具: {len(self.tools.list_tools())}个内置")
    
    def _register_builtin_tools(self):
        """注册内置工具"""
        import datetime
        
        def calc(expr):
            import re
            if re.match(r'^[\d+\-*/().\s]+$', expr):
                try:
                    return f"结果: {eval(expr)}"
                except:
                    return "表达式无效"
            return "表达式无效"
        
        self.tools.register("计算器", calc, "计算数学表达式")
        self.tools.register("获取时间", lambda: f"现在时间是: {datetime.datetime.now().strftime('%H:%M:%S')}", "获取当前时间")
        
        # 同步到Agent
        for tool in self.tools.list_tools():
            self.agent.register_tool(tool["name"], self.tools.get(tool["name"]), tool["description"])
    
    def register_tool(self, name: str, func, description: str = ""):
        """注册自定义工具"""
        self.tools.register(name, func, description)
        self.agent.register_tool(name, func, description)
    
    def chat(self, messages, **kwargs):
        return self.model.chat(messages, **kwargs)
    
    def chat_stream(self, messages, on_chunk=None, **kwargs):
        """流式对话"""
        return self.model.chat_stream(messages, on_chunk=on_chunk, **kwargs)
    
    def create_chain(self, name, steps):
        return self.chains.create_chain(name, steps)
    
    def run_chain(self, name, inputs):
        return self.chains.execute(name, inputs)
    
    def run_agent(self, task):
        return self.agent.run(task)
    
    def switch_model(self, provider, model=None):
        self.model.switch_model(provider, model)
        self.agent.model = self.model
    
    def get_info(self):
        return {
            "version": __version__,
            "model": f"{self.model.config.provider}/{self.model.config.model}",
            "tools": self.tools.list_tools(),
            "chains": self.chains.list_chains(),
        }
