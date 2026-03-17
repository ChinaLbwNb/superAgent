import urllib.request
import urllib.error
import json
from typing import Any, Optional
from .base import BaseTool


class HttpGetTool(BaseTool):
    """HTTP GET 请求工具"""
    name = "http_get"
    description = "发送 HTTP GET 请求获取网页内容"
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "要访问的 URL"},
            "timeout": {"type": "integer", "description": "超时时间（秒），默认 10", "default": 10},
        },
        "required": ["url"],
    }

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    async def execute(self, url: str, timeout: int = 10) -> str:
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
            )
            with urllib.request.urlopen(req, timeout=timeout) as response:
                content = response.read().decode('utf-8', errors='ignore')
                return f"状态码: {response.status}\n\n{content[:5000]}"
        except urllib.error.HTTPError as e:
            return f"HTTP 错误: {e.code} {e.reason}"
        except urllib.error.URLError as e:
            return f"URL 错误: {e.reason}"
        except Exception as e:
            return f"错误: {e}"


class HttpPostTool(BaseTool):
    """HTTP POST 请求工具"""
    name = "http_post"
    description = "发送 HTTP POST 请求"
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "要访问的 URL"},
            "data": {"type": "string", "description": "POST 数据（JSON 格式）"},
            "timeout": {"type": "integer", "description": "超时时间（秒），默认 10", "default": 10},
        },
        "required": ["url", "data"],
    }

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    async def execute(self, url: str, data: str, timeout: int = 10) -> str:
        try:
            req = urllib.request.Request(
                url,
                data=data.encode('utf-8'),
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Content-Type": "application/json",
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=timeout) as response:
                content = response.read().decode('utf-8', errors='ignore')
                return f"状态码: {response.status}\n\n{content[:5000]}"
        except urllib.error.HTTPError as e:
            return f"HTTP 错误: {e.code} {e.reason}"
        except urllib.error.URLError as e:
            return f"URL 错误: {e.reason}"
        except Exception as e:
            return f"错误: {e}"