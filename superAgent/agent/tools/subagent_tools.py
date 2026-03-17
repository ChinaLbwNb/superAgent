from .base import BaseTool
from agent.subagent import SubAgentRunner


class SpawnAgentTool(BaseTool):
    name = "spawn_agent"
    description = "Spawn a background sub-agent to handle a long-running task asynchronously. Returns a task_id."
    parameters = {
        "type": "object",
        "properties": {
            "prompt": {"type": "string", "description": "The task to give to the sub-agent"},
            "session_id": {"type": "string", "description": "Optional session ID for the sub-agent"},
        },
        "required": ["prompt"],
    }

    def __init__(self, runner: SubAgentRunner):
        self.runner = runner

    async def execute(self, prompt: str, session_id: str | None = None) -> str:
        task_id = self.runner.submit(prompt, session_id)
        return f"Sub-agent task submitted. task_id={task_id}"


class GetAgentResultTool(BaseTool):
    name = "get_agent_result"
    description = "Get the result of a background sub-agent task by task_id."
    parameters = {
        "type": "object",
        "properties": {
            "task_id": {"type": "string", "description": "The task_id returned by spawn_agent"},
        },
        "required": ["task_id"],
    }

    def __init__(self, runner: SubAgentRunner):
        self.runner = runner

    async def execute(self, task_id: str) -> str:
        task = self.runner.get_status(task_id)
        if not task:
            return f"Error: task_id '{task_id}' not found."
        return (
            f"status: {task.status.value}\n"
            f"result: {task.result or '(not yet)'}\n"
            f"error: {task.error or 'none'}"
        )
