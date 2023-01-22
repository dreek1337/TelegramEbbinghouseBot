from sqlalchemy import select, delete

from aiogram import Dispatcher, Bot
from aiogram import types

from telegram_bot.handlers import other
from telegram_bot.database.models import RepeatInformation
from telegram_bot.handlers.other import replace_symbol, help_message
from telegram_bot.handlers.state import DeleteState, ContentState, SearchInformationState
from telegram_bot.keyboards.inlines import *
from telegram_bot.database.connection import *


async def __show_storage(callback_query: types.CallbackQuery):
    """
    Отправляет инлайн кнопки для работы с хранилищем
    """
    bot: Bot = callback_query.bot
    inline_buttons = (InlineKeyboardMarkup().add(add_repeat_info_button).add(saved_info_button)
                                            .add(clear_stack_and_storage).add(help_button))

    await bot.send_message(callback_query.from_user.id,
                           "📚 Переченнь доступных функций для работы с хранилищем.",
                           reply_markup=inline_buttons)


async def __show_stack(callback_query: types.CallbackQuery):
    """
    Показывает очередь на отправку информации
    """
    bot: Bot = callback_query.bot

    user_stack = [i for i in other.stack if i[1] == callback_query.from_user.id]
    if not user_stack:
        await bot.send_message(callback_query.from_user.id, '❎ Очередь, как и ваша душа, чиста.',
                               reply_markup=universal_inline_buttons)
    else:
        send_stack = '\n'.join(f'*{str(j)}*' + '\. ' + f'_{replace_symbol(i[0])}_'
                               for j, i in zip(range(1, len(user_stack) + 1), user_stack))

        inline_buttons = (InlineKeyboardMarkup().add(add_repeat_info_button).add(delete_element_from_stack)
                                                .add(clear_stack).add(help_button))

        await bot.send_message(callback_query.from_user.id,
                               send_stack,
                               reply_markup=inline_buttons,
                               parse_mode='MarkdownV2')


async def __clear_stack(callback_query: types.CallbackQuery):
    """
    Удаляет из очереди все карточки
    """
    bot: Bot = callback_query.bot

    other.stack = [i for i in other.stack if i[1] != callback_query.from_user.id]  # Очень странный вариант, но лучше копирования списка

    await bot.send_message(callback_query.from_user.id,
                           '✅ Очередь была очищена. Теперь можем продолжить с чистой душой.',
                           reply_markup=universal_inline_buttons)


# Удаление из очереди одного элемента
async def __delete_info_from_stack(callback_query: types.CallbackQuery):
    """
    Запрашивает ключевое слово для удаления карточки из очереди
    """
    bot: Bot = callback_query.bot
    user_stack = [i for i in other.stack if i[1] == callback_query.from_user.id]

    if not user_stack:
        await bot.send_message(callback_query.from_user.id,
                               '❎ Нечего удалять, очередь кристально чиста',
                               reply_markup=universal_inline_buttons)
    else:
        await bot.send_message(callback_query.from_user.id, "📗 Введите ключевое слово, чтобы удалить его из очереди.")

        await DeleteState.header.set()


# Запрашивает у пользователя ключевое слово
async def __callback_start_repeat(callback_query: types.CallbackQuery):
    """
    Запрос ключевого слова
    """
    bot: Bot = callback_query.bot
    await bot.send_message(callback_query.from_user.id, "📚 Введите ключевое слово.")

    await ContentState.header.set()


# Работа с хранилищем
async def __send_all_info(callback_query: types.CallbackQuery):
    """
    Отображение ключевых слов находящихся в хранилище и проверка на их наличие
    """
    bot: Bot = callback_query.bot

    stmt = (select(RepeatInformation.header)
            .where(RepeatInformation.user_id == callback_query.from_user.id))

    await bot.answer_callback_query(callback_query.id)

    try:
        await bot.send_message(callback_query.from_user.id, '\n'.join(str(j) + '. ' + str(i[0])
                                                                      for j, i in
                                                                      zip(range(
                                                                          1, len(conn.execute(stmt).fetchall()) + 1),
                                                                          conn.execute(stmt).fetchall())),
                               reply_markup=universal_inline_buttons)
    except:
        inline_buttons = InlineKeyboardMarkup().add(add_repeat_info_button).add(help_button)
        await bot.send_message(callback_query.from_user.id,
                               '❎ Ваша душа чиста, в хранилище отсутствует информация.',
                               reply_markup=inline_buttons)


# Очистка хранилища
async def __clear_storage(callback_query: types.CallbackQuery):
    """
    Удаляет все элементы в хранилище
    """
    bot: Bot = callback_query.bot

    select_database = select(RepeatInformation).where(RepeatInformation.user_id == callback_query.from_user.id)

    if conn.execute(select_database).fetchall():
        stmt = delete(RepeatInformation).where(RepeatInformation.user_id == callback_query.from_user.id)
        conn.execute(stmt)

        other.stack = [i for i in other.stack if i[1] != callback_query.from_user.id]

        await bot.send_message(callback_query.from_user.id,
                               '✅ Хранилище было очищено.',
                               reply_markup=universal_inline_buttons)
    else:
        inline_buttons = InlineKeyboardMarkup().add(add_repeat_info_button).add(help_button)
        await bot.send_message(callback_query.from_user.id,
                               '❎ В хранилище и так уже пусто( Пора добавить новую карточку!',
                               reply_markup=inline_buttons)


# Отправка сообщения с командами
async def __send_help(callback_query: types.CallbackQuery):
    """
    Отображение текста с помощью
    """
    bot: Bot = callback_query.bot
    inline_buttons = InlineKeyboardMarkup().add(add_repeat_info_button).add(search_button)

    await bot.send_message(callback_query.from_user.id,
                           help_message,
                           reply_markup=inline_buttons,
                           parse_mode='MarkdownV2')


# Поиск информации в хранилище
async def __search_info(callback_query: types.CallbackQuery):
    """
    Запрос на ввод ключевого слова, для поиска в хранилище
    """
    bot: Bot = callback_query.bot

    await bot.send_message(callback_query.from_user.id,
                           "📗 Введите ключевое слово, чтобы я смог найти информацию по нему.")

    await SearchInformationState.header.set()


def register_callback_handlers(dp: Dispatcher):

    dp.register_callback_query_handler(__show_storage, lambda c: c.data == 'storage')
    dp.register_callback_query_handler(__show_stack, lambda c: c.data == 'stack')
    dp.register_callback_query_handler(__clear_stack, lambda c: c.data == 'clear_stack')
    dp.register_callback_query_handler(__delete_info_from_stack, lambda c: c.data == 'delete')
    dp.register_callback_query_handler(__callback_start_repeat, lambda c: c.data == 'startrepeat')
    dp.register_callback_query_handler(__send_all_info, lambda c: c.data == 'all_information')
    dp.register_callback_query_handler(__clear_storage, lambda c: c.data == 'clear_storage')
    dp.register_callback_query_handler(__send_help, lambda c: c.data == 'help')
    dp.register_callback_query_handler(__search_info, lambda c: c.data == 'search')