import os
import subprocess
from pathlib import Path
from typing import Any
from .base import BaseTool


def _safe_path(workspace: str, path: str, restrict: bool) -> Path:
    workspace_path = Path(workspace).resolve()
    target = (workspace_path / path).resolve()
    if restrict and not str(target).startswith(str(workspace_path)):
        raise PermissionError(f"Access denied: '{path}' is outside the workspace.")
    return target


class ReadFileTool(BaseTool):
    name = "read_file"
    description = "Read the content of a file."
    parameters = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "File path (relative to workspace)"},
        },
        "required": ["path"],
    }

    def __init__(self, workspace: str, restrict: bool = True):
        self.workspace = workspace
        self.restrict = restrict

    async def execute(self, path: str) -> str:
        try:
            target = _safe_path(self.workspace, path, self.restrict)
            return target.read_text(encoding="utf-8")
        except Exception as e:
            return f"Error: {e}"


class WriteFileTool(BaseTool):
    name = "write_file"
    description = "Write content to a file (creates or overwrites)."
    parameters = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "File path (relative to workspace)"},
            "content": {"type": "string", "description": "Content to write"},
        },
        "required": ["path", "content"],
    }

    def __init__(self, workspace: str, restrict: bool = True):
        self.workspace = workspace
        self.restrict = restrict

    async def execute(self, path: str, content: str) -> str:
        try:
            target = _safe_path(self.workspace, path, self.restrict)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            return f"Written to {path} ({len(content)} chars)."
        except Exception as e:
            return f"Error: {e}"


class ListDirTool(BaseTool):
    name = "list_dir"
    description = "List files and directories in a given path."
    parameters = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Directory path (relative to workspace)", "default": "."},
        },
        "required": [],
    }

    def __init__(self, workspace: str, restrict: bool = True):
        self.workspace = workspace
        self.restrict = restrict

    async def execute(self, path: str = ".") -> str:
        try:
            target = _safe_path(self.workspace, path, self.restrict)
            entries = sorted(target.iterdir(), key=lambda p: (p.is_file(), p.name))
            lines = []
            for e in entries:
                prefix = "📁" if e.is_dir() else "📄"
                lines.append(f"{prefix} {e.name}")
            return "\n".join(lines) if lines else "(empty)"
        except Exception as e:
            return f"Error: {e}"


class EditFileTool(BaseTool):
    name = "edit_file"
    description = "Replace a specific string in a file with a new string."
    parameters = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "File path (relative to workspace)"},
            "old_string": {"type": "string", "description": "The exact string to replace"},
            "new_string": {"type": "string", "description": "The new string to replace it with"},
        },
        "required": ["path", "old_string", "new_string"],
    }

    def __init__(self, workspace: str, restrict: bool = True):
        self.workspace = workspace
        self.restrict = restrict

    async def execute(self, path: str, old_string: str, new_string: str) -> str:
        try:
            target = _safe_path(self.workspace, path, self.restrict)
            content = target.read_text(encoding="utf-8")
            if old_string not in content:
                return f"Error: String not found in {path}."
            new_content = content.replace(old_string, new_string, 1)
            target.write_text(new_content, encoding="utf-8")
            return f"Edited {path} successfully."
        except Exception as e:
            return f"Error: {e}"


class ShellTool(BaseTool):
    name = "shell"
    description = "Execute a shell command in the workspace directory."
    parameters = {
        "type": "object",
        "properties": {
            "command": {"type": "string", "description": "Shell command to execute"},
        },
        "required": ["command"],
    }

    def __init__(self, workspace: str):
        self.workspace = workspace

    async def execute(self, command: str) -> str:
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=30,
            )
            output = result.stdout
            if result.stderr:
                output += f"\nSTDERR:\n{result.stderr}"
            return output.strip() or "(no output)"
        except subprocess.TimeoutExpired:
            return "Error: Command timed out (30s)."
        except Exception as e:
            return f"Error: {e}"
