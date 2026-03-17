from pathlib import Path
from datetime import date


class MemoryManager:
    """
    长期记忆管理器。
    - 长期记忆：workspace/MEMORY.md（手动或 agent 写入）
    - 每日笔记：workspace/.superagent/daily/YYYY-MM-DD.md
    支持读取、追加、注入到上下文。
    """

    def __init__(self, workspace: str):
        self.workspace = Path(workspace)
        self.daily_dir = self.workspace / ".superagent" / "daily"
        self.daily_dir.mkdir(parents=True, exist_ok=True)
        self.memory_file = self.workspace / "MEMORY.md"

    # ── 长期记忆 ──────────────────────────────────────────

    def read_long_term(self) -> str:
        if self.memory_file.exists():
            return self.memory_file.read_text(encoding="utf-8").strip()
        return ""

    def write_long_term(self, content: str) -> None:
        self.memory_file.write_text(content, encoding="utf-8")

    def append_long_term(self, note: str) -> None:
        with open(self.memory_file, "a", encoding="utf-8") as f:
            f.write(f"\n{note}")

    # ── 每日笔记 ──────────────────────────────────────────

    def _today_file(self) -> Path:
        return self.daily_dir / f"{date.today().isoformat()}.md"

    def read_today(self) -> str:
        f = self._today_file()
        if f.exists():
            return f.read_text(encoding="utf-8").strip()
        return ""

    def append_today(self, note: str) -> None:
        with open(self._today_file(), "a", encoding="utf-8") as f:
            f.write(f"\n{note}")

    # ── 上下文注入 ────────────────────────────────────────

    def get_context(self) -> str:
        parts = []
        long_term = self.read_long_term()
        if long_term:
            parts.append(f"# Long-term Memory\n{long_term}")
        today = self.read_today()
        if today:
            parts.append(f"# Today's Notes ({date.today().isoformat()})\n{today}")
        return "\n\n".join(parts)
