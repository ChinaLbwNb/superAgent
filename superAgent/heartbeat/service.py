import asyncio
import logging
from pathlib import Path
from typing import Callable, Awaitable

logger = logging.getLogger(__name__)

Handler = Callable[[str], Awaitable[str]]  # task_text -> result


class HeartbeatService:
    """
    心跳服务：定期唤醒 agent，检查 workspace/HEARTBEAT.md 中的待办任务并执行。

    HEARTBEAT.md 格式（每行一个任务，- [ ] 表示待执行，- [x] 表示已完成）：
    ```
    - [ ] 检查邮件
    - [ ] 整理今日笔记
    - [x] 已完成的任务
    ```
    执行完后自动将 [ ] 标记为 [x]。
    """

    def __init__(self, workspace: str, handler: Handler, interval_seconds: int = 300):
        self.heartbeat_file = Path(workspace) / "HEARTBEAT.md"
        self.handler = handler
        self.interval = interval_seconds
        self._running = False

    def _read_pending(self) -> list[tuple[int, str]]:
        """返回 [(行号, 任务文本)] 的列表，仅包含未完成任务。"""
        if not self.heartbeat_file.exists():
            return []
        lines = self.heartbeat_file.read_text(encoding="utf-8").splitlines()
        pending = []
        for i, line in enumerate(lines):
            if line.strip().startswith("- [ ]"):
                task = line.strip()[5:].strip()
                pending.append((i, task))
        return pending

    def _mark_done(self, line_index: int) -> None:
        lines = self.heartbeat_file.read_text(encoding="utf-8").splitlines()
        lines[line_index] = lines[line_index].replace("- [ ]", "- [x]", 1)
        self.heartbeat_file.write_text("\n".join(lines), encoding="utf-8")

    async def tick(self) -> None:
        """执行一次心跳检查。"""
        pending = self._read_pending()
        if not pending:
            return
        logger.info(f"Heartbeat: found {len(pending)} pending task(s).")
        for line_idx, task in pending:
            logger.info(f"Heartbeat executing: {task}")
            try:
                await self.handler(task)
                self._mark_done(line_idx)
            except Exception as e:
                logger.error(f"Heartbeat task failed: {task!r} — {e}")

    async def start(self) -> None:
        self._running = True
        logger.info(f"HeartbeatService started (interval={self.interval}s).")
        while self._running:
            await self.tick()
            await asyncio.sleep(self.interval)

    def stop(self) -> None:
        self._running = False
