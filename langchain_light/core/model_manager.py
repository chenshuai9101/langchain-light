"""
模型管理器 v2 - 新增原生function_call支持
"""
import logging, json, urllib.request, urllib.error
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class Message:
    role: str
    content: str

@dataclass
class ModelConfig:
    provider: str = "deepseek"
    model: str = "deepseek-chat"
    api_key: str = ""
    base_url: str = ""
    temperature: float = 0.7
    max_tokens: int = 2048
    timeout: int = 30

PROVIDER_CONFIGS = {
    "deepseek": {"base_url": "https://api.deepseek.com/v1", "models": ["deepseek-chat", "deepseek-reasoner"]},
    "openai": {"base_url": "https://api.openai.com/v1", "models": ["gpt-4o", "gpt-4o-mini"]},
    "ollama": {"base_url": "http://localhost:11434/v1", "models": ["llama3", "mistral"]},
}


class ModelManager:
    def __init__(self, config: ModelConfig = None):
        self.config = config or ModelConfig()
        self._load_api_key()
        logger.info(f"模型管理器 v2: {self.config.provider}/{self.config.model}")

    def _load_api_key(self):
        if not self.config.api_key:
            env_map = {"deepseek": "DEEPSEEK_API_KEY", "openai": "OPENAI_API_KEY"}
            env_name = env_map.get(self.config.provider)
            if env_name:
                import os; self.config.api_key = os.environ.get(env_name, "")
        if not self.config.base_url:
            info = PROVIDER_CONFIGS.get(self.config.provider, {})
            self.config.base_url = info.get("base_url", "")

    def _build_headers(self) -> dict:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.api_key}",
        }

    def chat(self, messages: list, **kwargs) -> str:
        try:
            messages = self._normalize_messages(messages)
            return self._call_api(messages, **kwargs)
        except Exception as e:
            return f"[错误: {e}]"

    def _normalize_messages(self, messages: list) -> list:
        msgs = []
        for m in messages:
            if isinstance(m, dict):
                msgs.append(Message(role=m.get("role", "user"), content=m.get("content", "")))
            else:
                msgs.append(m)
        return msgs

    def _call_api(self, messages: list, **kwargs) -> str:
        api_key = kwargs.get("api_key", self.config.api_key)
        base_url = kwargs.get("base_url", self.config.base_url)
        if not api_key: return "错误: 未设置API Key"
        if not base_url: return "错误: base_url未配置"

        url = f"{base_url.rstrip('/')}/chat/completions"
        req_body = {
            "model": kwargs.get("model", self.config.model),
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
        }

        req = urllib.request.Request(
            url, data=json.dumps(req_body).encode("utf-8"),
            headers=self._build_headers(), method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.config.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            if "choices" in data and data["choices"]:
                return data["choices"][0]["message"]["content"]
            return f"API错误: {data.get('error', {}).get('message', str(data)[:200])}"
        except urllib.error.HTTPError as e:
            return f"HTTP {e.code}: {e.read().decode('utf-8')[:200]}"
        except urllib.error.URLError as e:
            return f"网络错误: {e.reason}"
        except Exception as e:
            return f"请求失败: {e}"

    def chat_stream(self, messages: list, on_chunk: callable = None, **kwargs) -> str:
        """流式输出 - 逐块回调"""
        # 兼容dict格式
        msgs = []
        for m in messages:
            if isinstance(m, dict):
                msgs.append(Message(role=m.get("role", "user"), content=m.get("content", "")))
            else:
                msgs.append(m)
        messages = msgs
        api_key = kwargs.get("api_key", self.config.api_key)
        base_url = kwargs.get("base_url", self.config.base_url)
        if not api_key: return "错误: 未设置API Key"
        if not base_url: return "错误: base_url未配置"

        url = f"{base_url.rstrip('/')}/chat/completions"
        req_body = {
            "model": kwargs.get("model", self.config.model),
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "stream": True,
        }

        req = urllib.request.Request(
            url, data=json.dumps(req_body).encode("utf-8"),
            headers=self._build_headers(), method="POST",
        )
        full_content = ""
        try:
            with urllib.request.urlopen(req, timeout=self.config.timeout) as resp:
                buffer = b""
                for chunk_bytes in iter(lambda: resp.read(1), b""):
                    buffer += chunk_bytes
                    if b"\n" in buffer:
                        lines = buffer.split(b"\n")
                        buffer = lines.pop()
                        for line in lines:
                            line_str = line.decode("utf-8", errors="replace").strip()
                            if line_str.startswith("data: "):
                                data_str = line_str[6:].strip()
                                if data_str == "[DONE]":
                                    break
                                try:
                                    chunk = json.loads(data_str)
                                    delta = chunk.get("choices", [{}])[0].get("delta", {})
                                    content = delta.get("content", "")
                                    if content:
                                        full_content += content
                                        if on_chunk:
                                            on_chunk(content)
                                except json.JSONDecodeError:
                                    pass
        except urllib.error.HTTPError as e:
            return f"HTTP {e.code}: {e.read().decode('utf-8')[:200]}"
        except urllib.error.URLError as e:
            return f"网络错误: {e.reason}"
        except Exception as e:
            return f"流式请求失败: {e}"
        return full_content

    def function_call(self, messages: List[Message], tools: List[Dict], **kwargs) -> Dict:
        """
        原生Function Calling调用
        返回: {"tool_calls": [...], "content": "..."}
        """
        api_key = kwargs.get("api_key", self.config.api_key)
        base_url = kwargs.get("base_url", self.config.base_url)
        if not api_key or not base_url:
            return {"error": "API Key或base_url未配置"}

        url = f"{base_url.rstrip('/')}/chat/completions"
        req_body = {
            "model": kwargs.get("model", self.config.model),
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "tools": tools,
            "tool_choice": "auto",
            "temperature": kwargs.get("temperature", self.config.temperature),
        }

        req = urllib.request.Request(
            url, data=json.dumps(req_body).encode("utf-8"),
            headers=self._build_headers(), method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.config.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            msg = data["choices"][0]["message"]
            return {"tool_calls": msg.get("tool_calls", []), "content": msg.get("content", "")}
        except Exception as e:
            return {"error": str(e)}

    def switch_model(self, provider: str, model: str = None):
        self.config.provider = provider
        if model: self.config.model = model
        self._load_api_key()

    def get_supported_models(self) -> dict:
        return {k: v["models"] for k, v in PROVIDER_CONFIGS.items()}
