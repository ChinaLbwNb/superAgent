from datetime import datetime
from pathlib import Path
from typing import Any
from .base import BaseTool

try:
    from PIL import ImageGrab
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


class ScreenshotTool(BaseTool):
    """截取电脑当前屏幕画面。"""

    name = "screenshot"
    description = "Take a screenshot of the current screen and save it to a file."
    parameters = {
        "type": "object",
        "properties": {
            "filename": {
                "type": "string",
                "description": "Filename for the screenshot (optional, default: screenshot_YYYYMMDD_HHMMSS.png)"
            },
        },
        "required": [],
    }

    def __init__(self, workspace: str):
        self.workspace = Path(workspace)
        self.screenshots_dir = self.workspace / ".superagent" / "screenshots"
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)

    async def execute(self, filename: str | None = None) -> str:
        if not HAS_PIL:
            return "Error: Pillow not installed. Run: pip install Pillow"

        try:
            # 生成默认文件名
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"

            # 确保是 .png 后缀
            if not filename.endswith(".png"):
                filename += ".png"

            # 截图保存路径
            save_path = self.screenshots_dir / filename

            # 执行截图
            screenshot = ImageGrab.grab()
            screenshot.save(save_path)

            return f"Screenshot saved: {save_path}"
        except Exception as e:
            return f"Error taking screenshot: {e}"
