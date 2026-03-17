import asyncio
import uuid
import logging
from dataclasses import dataclass, field
from typing import Any
from enum import Enum

logger = logging.getLogger(__name__)


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


@dataclass
class SubTask:
    id: str
    prompt: str
    session_id: str
    status: TaskStatus = TaskStatus.PENDING
    result: str = ""
    error: str = ""


class SubAgentRunner:
    """
    子代理运行器：后台异步执行长任务。
    任务通过 queue 提交，由独立 worker 并发执行。
    """

    def __init__(self, agent_process_fn, max_workers: int = 3):
        """
        agent_process_fn: async (prompt, session_id) -> str
        """
        self._fn = agent_process_fn
        self._max_workers = max_workers
        self._queue: asyncio.Queue[SubTask] = asyncio.Queue()
        self._tasks: dict[str, SubTask] = {}
        self._running = False

    def submit(self, prompt: str, session_id: str | None = None) -> str:
        """提交一个后台任务，返回 task_id。"""
        task_id = str(uuid.uuid4())[:8]
        session_id = session_id or f"subagent_{task_id}"
        task = SubTask(id=task_id, prompt=prompt, session_id=session_id)
        self._tasks[task_id] = task
        self._queue.put_nowait(task)
        logger.info(f"SubAgent task submitted: {task_id}")
        return task_id

    def get_status(self, task_id: str) -> SubTask | None:
        return self._tasks.get(task_id)

    async def _worker(self):
        while self._running:
            try:
                task = await asyncio.wait_for(self._queue.get(), timeout=1.0)
            except asyncio.TimeoutError:
                continue
            task.status = TaskStatus.RUNNING
            logger.info(f"SubAgent running task: {task.id}")
            try:
                result = await self._fn(task.prompt, task.session_id)
                task.result = result
                task.status = TaskStatus.DONE
                logger.info(f"SubAgent task done: {task.id}")
            except Exception as e:
                task.error = str(e)
                task.status = TaskStatus.FAILED
                logger.error(f"SubAgent task failed: {task.id} — {e}")

    async def start(self):
        self._running = True
        workers = [asyncio.create_task(self._worker()) for _ in range(self._max_workers)]
        await asyncio.gather(*workers)

    def stop(self):
        self._running = False
