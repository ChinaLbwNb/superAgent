from pydantic import BaseModel
from typing import Optional


class TelegramConfig(BaseModel):
    token: str = ""
    allowed_users: list[int] = []


class CronConfig(BaseModel):
    enabled: bool = False


class HeartbeatConfig(BaseModel):
    enabled: bool = False
    interval_seconds: int = 300


class Config(BaseModel):
    model: str = "gpt-4o"
    api_key: str = ""
    api_base: str = ""
    provider: str = "openai"  # "openai" or "anthropic"
    max_tokens: int = 4096
    temperature: float = 0.7
    max_tool_iterations: int = 20
    workspace: str = "."
    restrict_to_workspace: bool = True
    system_prompt: str = "You are superAgent, a powerful AI assistant. You can use tools to help users with their tasks."
    telegram: TelegramConfig = TelegramConfig()
    cron: CronConfig = CronConfig()
    heartbeat: HeartbeatConfig = HeartbeatConfig()
