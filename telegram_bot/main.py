import logging

from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from telegram_bot.handlers.main import register_all_handlers
from telegram_bot.utils.env import TgKeys


# Подключение к боту
async def __on_start_up(dp: Dispatcher):
    logging.basicConfig(level=logging.INFO)

    register_all_handlers(dp)


# Запуск бота
def __start_bot():

    bot = Bot(token=TgKeys.TOKEN)

    dp = Dispatcher(bot, storage=MemoryStorage())

    executor.start_polling(dp, skip_updates=True, on_startup=__on_start_up)
