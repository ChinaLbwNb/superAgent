from .base import BaseTool
from agent.memory import MemoryManager


class SaveMemoryTool(BaseTool):
    name = "save_memory"
    description = "Save a note to long-term memory (MEMORY.md)."
    parameters = {
        "type": "object",
        "properties": {
            "note": {"type": "string", "description": "The note to save to long-term memory"},
        },
        "required": ["note"],
    }

    def __init__(self, memory: MemoryManager):
        self.memory = memory

    async def execute(self, note: str) -> str:
        self.memory.append_long_term(f"\n- {note}")
        return f"Saved to memory: {note}"


class SaveTodayNoteTool(BaseTool):
    name = "save_today_note"
    description = "Save a note to today's daily log."
    parameters = {
        "type": "object",
        "properties": {
            "note": {"type": "string", "description": "The note to save to today's log"},
        },
        "required": ["note"],
    }

    def __init__(self, memory: MemoryManager):
        self.memory = memory

    async def execute(self, note: str) -> str:
        self.memory.append_today(f"\n- {note}")
        return f"Saved to today's notes: {note}"


class ReadMemoryTool(BaseTool):
    name = "read_memory"
    description = "Read the full long-term memory."
    parameters = {
        "type": "object",
        "properties": {},
        "required": [],
    }

    def __init__(self, memory: MemoryManager):
        self.memory = memory

    async def execute(self) -> str:
        content = self.memory.read_long_term()
        return content if content else "(memory is empty)"
