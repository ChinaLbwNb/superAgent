import asyncio
import logging
from typing import TYPE_CHECKING

from channels.base import BaseChannel
from bus.queue import MessageBus, Message

logger = logging.getLogger(__name__)

try:
    from telegram import Update
    from telegram.ext import Application, MessageHandler, filters, ContextTypes
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False


class TelegramChannel(BaseChannel):
    """
    Telegram channel。
    依赖：pip install python-telegram-bot>=21.0
    配置：在 config.json 中添加 telegram_token 字段。
    """

    def __init__(self, bus: MessageBus, token: str, allowed_users: list[int] | None = None):
        super().__init__(bus)
        if not TELEGRAM_AVAILABLE:
            raise ImportError("python-telegram-bot is not installed. Run: pip install python-telegram-bot")
        self.token = token
        self.allowed_users = set(allowed_users) if allowed_users else None
        self._app = None

    async def start(self) -> None:
        self._app = Application.builder().token(self.token).build()

        async def handle_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
            user_id = update.effective_user.id
            if self.allowed_users and user_id not in self.allowed_users:
                await update.message.reply_text("Access denied.")
                return

            session_id = f"telegram_{user_id}"
            text = update.message.text or ""

            # 发到 agent inbound
            await self.bus.send(Message(session_id=session_id, content=text))

            # 等待 agent 回复
            reply = await self.bus.get_reply()
            await update.message.reply_text(reply.content)

        self._app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        await self._app.initialize()
        await self._app.start()
        await self._app.updater.start_polling()
        logger.info("Telegram channel started.")

    async def stop(self) -> None:
        if self._app:
            await self._app.updater.stop()
            await self._app.stop()
            await self._app.shutdown()
            logger.info("Telegram channel stopped.")
