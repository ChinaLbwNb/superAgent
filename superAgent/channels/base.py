from abc import ABC, abstractmethod
from bus.queue import MessageBus


class BaseChannel(ABC):
    """
    Channel 抽象基类。
    每种接入方式（Telegram、Discord、Web 等）继承此类，
    实现 start() 方法，通过 bus 与 agent 通信。
    """

    def __init__(self, bus: MessageBus):
        self.bus = bus

    @abstractmethod
    async def start(self) -> None:
        """启动 channel，开始监听输入并转发到 bus。"""
        ...

    @abstractmethod
    async def stop(self) -> None:
        """停止 channel。"""
        ...
