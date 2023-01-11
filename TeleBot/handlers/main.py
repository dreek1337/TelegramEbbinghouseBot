from aiogram import Dispatcher

from TeleBot.handlers.callbacks import register_callback_handlers
from TeleBot.handlers.messages import register_message_handlers


def register_all_handlers(dp: Dispatcher) -> None:
    handlers = (
        register_callback_handlers,
        register_message_handlers
    )
    for handler in handlers:
        handler(dp)
