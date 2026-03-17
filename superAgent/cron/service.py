import asyncio
import logging
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable, Awaitable

logger = logging.getLogger(__name__)


def _parse_cron_field(field: str, min_val: int, max_val: int) -> set[int]:
    """解析单个 cron 字段（支持 * / - ,）。"""
    values = set()
    for part in field.split(","):
        if part == "*":
            values.update(range(min_val, max_val + 1))
        elif "/" in part:
            base, step = part.split("/", 1)
            step = int(step)
            start = min_val if base == "*" else int(base)
            values.update(range(start, max_val + 1, step))
        elif "-" in part:
            start, end = part.split("-", 1)
            values.update(range(int(start), int(end) + 1))
        else:
            values.add(int(part))
    return values


class CronJob:
    def __init__(self, name: str, expression: str, task: str):
        self.name = name
        self.expression = expression  # "分 时 日 月 周"
        self.task = task
        fields = expression.split()
        assert len(fields) == 5, f"Invalid cron expression: {expression}"
        self.minutes = _parse_cron_field(fields[0], 0, 59)
        self.hours = _parse_cron_field(fields[1], 0, 23)
        self.days = _parse_cron_field(fields[2], 1, 31)
        self.months = _parse_cron_field(fields[3], 1, 12)
        self.weekdays = _parse_cron_field(fields[4], 0, 6)

    def matches(self, dt: datetime) -> bool:
        return (
            dt.minute in self.minutes
            and dt.hour in self.hours
            and dt.day in self.days
            and dt.month in self.months
            and dt.weekday() in self.weekdays
        )


Handler = Callable[[str, str], Awaitable[str]]  # (task, job_name) -> result


class CronService:
    """
    定时任务服务。
    从 workspace/CRON.md 读取任务配置，按 cron 表达式定时执行。

    CRON.md 格式：
    ```
    # job-name
    expression: 0 9 * * 1-5
    task: 发送早报
    ```
    """

    def __init__(self, workspace: str, handler: Handler):
        self.cron_file = Path(workspace) / "CRON.md"
        self.handler = handler
        self._jobs: list[CronJob] = []
        self._running = False

    def _load_jobs(self) -> list[CronJob]:
        if not self.cron_file.exists():
            return []
        content = self.cron_file.read_text(encoding="utf-8")
        jobs = []
        # 解析格式：## job-name \n expression: xxx \n task: xxx
        blocks = re.split(r"^##\s+", content, flags=re.MULTILINE)
        for block in blocks:
            if not block.strip():
                continue
            lines = block.strip().splitlines()
            name = lines[0].strip()
            params = {}
            for line in lines[1:]:
                if ":" in line:
                    k, v = line.split(":", 1)
                    params[k.strip()] = v.strip()
            expr = params.get("expression", "")
            task = params.get("task", "")
            if expr and task:
                try:
                    jobs.append(CronJob(name, expr, task))
                except Exception as e:
                    logger.warning(f"Invalid cron job '{name}': {e}")
        return jobs

    async def start(self) -> None:
        self._running = True
        logger.info("CronService started.")
        while self._running:
            now = datetime.now().replace(second=0, microsecond=0)
            self._jobs = self._load_jobs()
            for job in self._jobs:
                if job.matches(now):
                    logger.info(f"Running cron job: {job.name}")
                    try:
                        await self.handler(job.task, job.name)
                    except Exception as e:
                        logger.error(f"Cron job '{job.name}' failed: {e}")
            # 等到下一分钟
            next_min = (now + timedelta(minutes=1)).replace(second=0, microsecond=0)
            await asyncio.sleep((next_min - datetime.now()).total_seconds())

    def stop(self) -> None:
        self._running = False
