import sys
import os
from pathlib import Path

# Windows 终端 UTF-8 编码修复
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# 确保项目根目录在 Python 路径中
sys.path.insert(0, str(Path(__file__).parent))

from cli.commands import app

if __name__ == "__main__":
    app()
