import json
from pathlib import Path
from datetime import datetime


class SessionManager:
    """
    会话历史管理：以 JSONL 格式持久化每个 session。
    每行是一条消息 {"role": ..., "content": ...}。
    """

    def __init__(self, sessions_dir: str = ".superagent/sessions"):
        self.sessions_dir = Path(sessions_dir)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self._cache: dict[str, list[dict]] = {}

    def _path(self, session_id: str) -> Path:
        return self.sessions_dir / f"{session_id}.jsonl"

    def load(self, session_id: str) -> list[dict]:
        if session_id in self._cache:
            return self._cache[session_id]
        path = self._path(session_id)
        messages = []
        if path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line:
                    messages.append(json.loads(line))
        self._cache[session_id] = messages
        return messages

    def append(self, session_id: str, message: dict) -> None:
        messages = self.load(session_id)
        messages.append(message)
        with open(self._path(session_id), "a", encoding="utf-8") as f:
            f.write(json.dumps(message, ensure_ascii=False) + "\n")

    def clear(self, session_id: str) -> None:
        self._cache.pop(session_id, None)
        path = self._path(session_id)
        if path.exists():
            path.unlink()

    def list_sessions(self) -> list[str]:
        return [p.stem for p in self.sessions_dir.glob("*.jsonl")]
