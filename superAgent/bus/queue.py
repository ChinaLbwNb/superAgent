import asyncio
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Message:
    session_id: str
    content: str
    role: str = "user"
    metadata: dict[str, Any] = field(default_factory=dict)


class MessageBus:
    """
    异步消息总线，解耦输入渠道（channel）与 agent 核心。
    - inbound：channel → agent
    - outbound：agent → channel
    """

    def __init__(self):
        self.inbound: asyncio.Queue[Message] = asyncio.Queue()
        self.outbound: asyncio.Queue[Message] = asyncio.Queue()

    async def send(self, message: Message) -> None:
        """Channel 向 agent 发送消息。"""
        await self.inbound.put(message)

    async def receive(self) -> Message:
        """Agent 从 inbound 队列取消息。"""
        return await self.inbound.get()

    async def reply(self, message: Message) -> None:
        """Agent 将回复放入 outbound 队列。"""
        await self.outbound.put(message)

    async def get_reply(self) -> Message:
        """Channel 从 outbound 队列取回复。"""
        return await self.outbound.get()
