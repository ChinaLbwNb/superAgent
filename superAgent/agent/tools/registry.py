from typing import Any
from .base import BaseTool


class ToolRegistry:
    """工具注册表：注册、查找、执行工具。"""

    def __init__(self):
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        self._tools[tool.name] = tool

    def get_definitions(self) -> list[dict[str, Any]]:
        return [tool.to_schema() for tool in self._tools.values()]

    async def execute(self, name: str, params: dict[str, Any]) -> str:
        if name not in self._tools:
            return f"Error: Tool '{name}' not found."
        tool = self._tools[name]
        errors = tool.validate_params(params)
        if errors:
            return "Error: " + "; ".join(errors)
        try:
            return await tool.execute(**params)
        except Exception as e:
            return f"Error executing tool '{name}': {e}"
