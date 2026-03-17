"""
网络工具：让 Agent 访问互联网
"""

import json
from typing import Any
from .base import BaseTool

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


class WebSearchTool(BaseTool):
    """网络搜索工具（使用 DuckDuckGo，无需 API Key）"""

    name = "web_search"
    description = "Search the internet for information. Returns search results with titles and URLs."
    parameters = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query"
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of results (default: 5)",
                "default": 5
            }
        },
        "required": ["query"]
    }

    async def execute(self, query: str, max_results: int = 5) -> str:
        if not HAS_REQUESTS:
            return "Error: requests not installed. Run: pip install requests"

        try:
            # 使用 DuckDuckGo Instant Answer API
            url = "https://api.duckduckgo.com/"
            params = {
                "q": query,
                "format": "json",
                "no_html": 1,
                "skip_disambig": 1
            }

            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            results = []

            # 相关主题
            if data.get("RelatedTopics"):
                for topic in data["RelatedTopics"][:max_results]:
                    if isinstance(topic, dict) and "Text" in topic:
                        text = topic.get("Text", "")
                        url = topic.get("FirstURL", "")
                        results.append(f"• {text}\n  URL: {url}")

            # 直接答案
            if data.get("AbstractText"):
                results.insert(0, f"摘要: {data['AbstractText']}\n  来源: {data.get('AbstractURL', '')}")

            if not results:
                # 备用：使用 HTML 搜索
                return await self._search_html(query, max_results)

            return f"搜索结果:\n\n" + "\n\n".join(results)

        except Exception as e:
            return f"Search error: {e}"

    async def _search_html(self, query: str, max_results: int) -> str:
        """备用搜索方法"""
        try:
            url = f"https://html.duckduckgo.com/html/?q={query}"
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers, timeout=10)

            # 简单解析 HTML 结果
            results = []
            lines = response.text.split("\n")

            for line in lines:
                if 'class="result__a"' in line:
                    # 提取标题
                    start = line.find('">') + 2
                    end = line.find('</a>')
                    if start > 1 and end > start:
                        title = line[start:end].strip()
                        results.append(f"• {title}")
                        if len(results) >= max_results:
                            break

            if results:
                return f"搜索结果:\n\n" + "\n".join(results)
            return "No results found."

        except Exception as e:
            return f"Search error: {e}"


class WebFetchTool(BaseTool):
    """获取网页内容"""

    name = "web_fetch"
    description = "Fetch and extract text content from a web page URL."
    parameters = {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "The URL to fetch"
            },
            "max_length": {
                "type": "integer",
                "description": "Maximum content length to return (default: 5000)",
                "default": 5000
            }
        },
        "required": ["url"]
    }

    async def execute(self, url: str, max_length: int = 5000) -> str:
        if not HAS_REQUESTS:
            return "Error: requests not installed. Run: pip install requests"

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()

            # 简单提取文本内容
            content = response.text

            # 移除 script 和 style
            import re
            content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
            content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)

            # 移除 HTML 标签
            content = re.sub(r'<[^>]+>', ' ', content)

            # 清理空白
            content = re.sub(r'\s+', ' ', content)
            content = content.strip()

            # 截断
            if len(content) > max_length:
                content = content[:max_length] + "..."

            return f"URL: {url}\n\n{content}"

        except Exception as e:
            return f"Fetch error: {e}"


class WebRequestTool(BaseTool):
    """通用 HTTP 请求工具"""

    name = "web_request"
    description = "Make an HTTP request to any URL. Useful for API calls."
    parameters = {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "The URL to request"
            },
            "method": {
                "type": "string",
                "description": "HTTP method: GET, POST, PUT, DELETE (default: GET)",
                "default": "GET"
            },
            "headers": {
                "type": "object",
                "description": "HTTP headers as JSON object",
                "default": {}
            },
            "body": {
                "type": "string",
                "description": "Request body (for POST/PUT)"
            }
        },
        "required": ["url"]
    }

    async def execute(self, url: str, method: str = "GET", headers: dict = None, body: str = None) -> str:
        if not HAS_REQUESTS:
            return "Error: requests not installed. Run: pip install requests"

        try:
            method = method.upper()

            kwargs = {
                "url": url,
                "method": method,
                "headers": headers or {},
                "timeout": 30
            }

            if body and method in ["POST", "PUT", "PATCH"]:
                kwargs["data"] = body

            response = requests.request(**kwargs)

            result = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": response.text[:5000] if len(response.text) > 5000 else response.text
            }

            return json.dumps(result, indent=2, ensure_ascii=False)

        except Exception as e:
            return f"Request error: {e}"
