from aiogram import Dispatcher

from telegram_bot.handlers.callbacks import register_callback_handlers
from telegram_bot.handlers.messages import register_message_handlers


def register_all_handlers(dp: Dispatcher) -> None:
    handlers = (
        register_callback_handlers,
        register_message_handlers
    )
    for handler in handlers:
        handler(dp)
