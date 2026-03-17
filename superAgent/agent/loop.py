import json
import sys
import os
from typing import Any
from io import StringIO

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from config.schema import Config
from providers.llm import LLMProvider
from session.manager import SessionManager
from agent.context import ContextBuilder
from agent.memory import MemoryManager
from agent.subagent import SubAgentRunner
from agent.tools.registry import ToolRegistry
from agent.tools.filesystem import (
    ReadFileTool, WriteFileTool, ListDirTool, EditFileTool, ShellTool
)
from agent.tools.memory_tools import SaveMemoryTool, SaveTodayNoteTool, ReadMemoryTool
from agent.tools.subagent_tools import SpawnAgentTool, GetAgentResultTool
from agent.tools.screenshot import ScreenshotTool
from agent.tools.web import WebSearchTool, WebFetchTool, WebRequestTool

# Windows 编码修复
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# 检测是否在 CLI 模式（有真实终端）
IS_CLI_MODE = sys.stdout.isatty()

# CLI 模式：显示思考过程；GUI 模式：静默
if IS_CLI_MODE:
    console = Console()
else:
    console = Console(file=StringIO(), legacy_windows=False)


class AgentLoop:
    """
    Agent 主循环：
    1. 接收用户消息
    2. 构建上下文（system prompt + memory + skills + history）
    3. 调用 LLM
    4. 执行工具调用（循环直到无 tool_call 或达上限）
    5. 持久化历史，返回最终回复
    """

    def __init__(self, config: Config):
        self.config = config
        self.provider = LLMProvider(config)
        self.memory = MemoryManager(config.workspace)
        self.session = SessionManager(
            sessions_dir=f"{config.workspace}/.superagent/sessions"
        )
        self.context_builder = ContextBuilder(config)
        self.subagent_runner = SubAgentRunner(agent_process_fn=self._process_internal)
        self.registry = ToolRegistry()
        self._register_tools()

    def _register_tools(self):
        ws = self.config.workspace
        restrict = self.config.restrict_to_workspace

        # 文件系统工具
        self.registry.register(ReadFileTool(ws, restrict))
        self.registry.register(WriteFileTool(ws, restrict))
        self.registry.register(ListDirTool(ws, restrict))
        self.registry.register(EditFileTool(ws, restrict))
        self.registry.register(ShellTool(ws))

        # 记忆工具
        self.registry.register(SaveMemoryTool(self.memory))
        self.registry.register(SaveTodayNoteTool(self.memory))
        self.registry.register(ReadMemoryTool(self.memory))

        # 子代理工具
        self.registry.register(SpawnAgentTool(self.subagent_runner))
        self.registry.register(GetAgentResultTool(self.subagent_runner))

        # 截图工具
        self.registry.register(ScreenshotTool(ws))

        # 网络工具
        self.registry.register(WebSearchTool())
        self.registry.register(WebFetchTool())
        self.registry.register(WebRequestTool())

    async def _process_internal(self, user_input: str, session_id: str) -> str:
        """内部处理逻辑（供 SubAgentRunner 调用）。"""
        history = self.session.load(session_id)
        messages = self.context_builder.build(history, user_input)
        tools = self.registry.get_definitions()

        iterations = 0
        assistant_content = ""

        while iterations < self.config.max_tool_iterations:
            iterations += 1

            # 显示思考过程
            console.print(Panel(
                f"[dim]Iteration {iterations}[/dim]",
                title="[bold cyan]🧠 Thinking[/bold cyan]",
                expand=False
            ))

            response = await self.provider.chat(messages, tools=tools)
            assistant_content = response.content

            # 显示模型原始响应
            console.print(Panel(
                f"[dim]content:[/dim] {assistant_content[:300]}{'...' if len(assistant_content) > 300 else ''}\n"
                f"[dim]tool_calls:[/dim] {response.tool_calls if response.tool_calls else '[red]None[/red]'}",
                title="[bold]📤 LLM Response[/bold]",
                expand=False
            ))

            if not response.tool_calls:
                # LLM 决定不调用工具
                console.print(Panel(
                    "[green]直接回答，无需调用工具[/green]",
                    title="[bold]Decision[/bold]",
                    expand=False
                ))
                break

            # LLM 决定调用工具
            console.print(Panel(
                f"[yellow]调用 {len(response.tool_calls)} 个工具[/yellow]",
                title="[bold]Decision[/bold]",
                expand=False
            ))

            # 显示工具调用详情
            table = Table(title="🔧 Tool Calls", show_header=True, header_style="bold magenta")
            table.add_column("Tool", style="cyan")
            table.add_column("Arguments", style="green")

            for tc in response.tool_calls:
                args_str = json.dumps(tc["arguments"], ensure_ascii=False)
                table.add_row(tc["name"], args_str)

            console.print(table)

            # 追加 assistant 消息（含 tool_calls）
            messages.append({
                "role": "assistant",
                "content": assistant_content,
                "tool_calls": [
                    {
                        "id": tc["id"],
                        "type": "function",
                        "function": {
                            "name": tc["name"],
                            "arguments": json.dumps(tc["arguments"], ensure_ascii=False),
                        },
                    }
                    for tc in response.tool_calls
                ],
            })

            # 执行所有工具调用
            for tc in response.tool_calls:
                result = await self.registry.execute(tc["name"], tc["arguments"])

                # 显示工具执行结果
                result_preview = result[:500] + "..." if len(result) > 500 else result
                console.print(Panel(
                    result_preview,
                    title=f"[bold green]✓ {tc['name']}[/bold green]",
                    expand=False
                ))

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": result,
                })

        # 持久化这轮对话
        self.session.append(session_id, {"role": "user", "content": user_input})
        self.session.append(session_id, {"role": "assistant", "content": assistant_content})

        return assistant_content

    async def process(self, user_input: str, session_id: str = "default") -> str:
        return await self._process_internal(user_input, session_id)
