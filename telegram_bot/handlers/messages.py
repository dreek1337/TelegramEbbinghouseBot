import asyncio

from aiogram import types
from aiogram import Dispatcher, Bot
from aiogram.dispatcher import FSMContext

from sqlalchemy import select
from telegram_bot.database.models import RepeatInformation

from telegram_bot.handlers.other import replace_symbol, stack, text
from telegram_bot.handlers.state import ContentState, DeleteState, SearchInformationState
from telegram_bot.keyboards.inlines import *
from telegram_bot.database.connection import *


async def __send_welcome(message: types.Message):
    """
    Команда вызывает приветственный текст
    """
    bot: Bot = message.bot
    inline_buttons = InlineKeyboardMarkup().add(add_repeat_info_button).add(help_button)

    await bot.send_message(message.from_user.id,
                           text,
                           parse_mode='MarkdownV2',
                           reply_markup=inline_buttons)


async def __send_all_buttons(message: types.Message):
    """
    Отображает все кнопки доступные в боте
    """
    bot: Bot = message.bot
    all_buttons = (InlineKeyboardMarkup().add(add_repeat_info_button).add(delete_element_from_stack)
                   .add(storage_button).add(clear_stack_and_storage).add(saved_info_button).add(search_button).add(stack_button)
                   .add(clear_stack).add(help_button))

    await bot.send_message(message.from_user.id,
                           '📚 Прошу, пользуйся на здоровье',
                           reply_markup=all_buttons)


async def __send_start_repeat_buttons(message: types.Message):
    """
    Через команду, отправляет инлайн кнопки для работы с ботом
    """
    await message.reply('🤓 Чем могу быть полезен?',
                        reply_markup=universal_inline_buttons)


async def __delete_info_from_stack_condition(message: types.Message, state: FSMContext):
    """
    Удаляет карточку из очереди и отправляет сообщение об успешном удалении, либо об отсутствии карточки в очереди
    """
    bot: Bot = message.bot

    await state.update_data(header=message.text)

    data = await state.get_data()

    keyword_and_id = data['header'], message.from_user.id

    if keyword_and_id in stack:
        stack.remove(keyword_and_id)

        await bot.send_message(message.from_user.id, f"✅ Ключевое слово «{data['header']}» было удалено из очереди.",
                               reply_markup=universal_inline_buttons)
    else:
        await message.answer("❌ Ключевое слово отсутствует в очереди!",
                             reply_markup=universal_inline_buttons)

    await state.finish()


# Добавление карточки
async def __processing_header_and_request_info(message: types.Message, state: FSMContext):
    """
    Обработка ключевого слова и запрос краткого описания
    """
    bot: Bot = message.bot

    await state.update_data(header=message.text)

    await bot.send_message(message.chat.id, "♻ Отлично! Теперь введите краткое описание.")

    await ContentState.next()  # либо же UserState.information.set()


async def __processing_info(message: types.Message, state: FSMContext):
    """
    Обработка краткого описания, сохранение всей информации в бд и запуск повторения информации
    """
    bot: Bot = message.bot

    await state.update_data(information=message.text)

    data = await state.get_data()

    user_id = message.from_user.id
    header = data['header']
    information = data['information']

    session.add(RepeatInformation(
        user_id=user_id,
        header=header,
        information=information
    ))
    session.commit()

    await state.finish()

    stack.append((header, message.from_user.id))

    inline_buttons = InlineKeyboardMarkup().add(help_button)

    await bot.send_message(message.from_user.id,
                           '✅ Поздравляю\! *Карточка* успешно сохранена\.',
                           reply_markup=inline_buttons,
                           parse_mode='MarkdownV2')

    repeat_counts = 0
    repeat_after_times = 1200

    for i in range(5):
        if (header, message.from_user.id) in stack:
            await bot.send_message(message.chat.id,
                                   f"📚 *Ключевое слово:* __{replace_symbol(header)}__\n\n"
                                   f"♻ *Описание:* ||_{replace_symbol(information)}_||",
                                   reply_markup=universal_inline_buttons,
                                   parse_mode='MarkdownV2')
            if repeat_counts < 1:
                await asyncio.sleep(repeat_after_times)
                repeat_counts += 1
                repeat_after_times *= 30
            else:
                await asyncio.sleep(repeat_after_times)
                repeat_after_times *= 3

    try:
        stack.remove((header, message.from_user.id))
    except ValueError:
        pass


# Работа с состоянием поиска
async def __processing_state_search(message: types.Message, state: FSMContext):
    """
    Поиск информации в бд
    """
    bot: Bot = message.bot

    await state.update_data(header=message.text)

    data = await state.get_data()
    header_and_id = data['header'], message.from_user.id

    stmt = (select(RepeatInformation.header, RepeatInformation.information)
            .where(RepeatInformation.header == header_and_id[0],
                   RepeatInformation.user_id == header_and_id[1]))
    database = set(conn.execute(stmt).fetchall())  # фильтрация повторяющихся эдементов

    if database:
        answer_text = '\n'.join(f"{j}\. 📚 *Ключевое слово:* __{replace_symbol(i[0])}__\n\n"
                                f"♻ *Описание:* ||_{replace_symbol(i[1])}_||\n"
                                for j, i in zip(range(1, len(database) + 1), database))

        await bot.send_message(message.chat.id,
                               answer_text,
                               reply_markup=universal_inline_buttons,
                               parse_mode='MarkdownV2')
    else:
        inline_buttons = InlineKeyboardMarkup().add(add_repeat_info_button).add(help_button)
        await bot.send_message(message.chat.id,
                               '❎ Дитя, в хранилище отсутствует это ключевое слово, мне нечего тебе предложить!',
                               reply_markup=inline_buttons)

    await state.finish()


async def __echo(message: types.Message):
    """
    Ответ на неверный формат сообщения
    """
    bot: Bot = message.bot
    await bot.send_message(message.from_user.id,
                           '🚫 Ой, что\-то на непонятном\(\(\( Попробуй перейти в раздел *Помощь*\.',
                           reply_markup=universal_inline_buttons,
                           parse_mode='MarkdownV2')


def register_message_handlers(dp: Dispatcher):

    dp.register_message_handler(__send_welcome, commands=['start'])
    dp.register_message_handler(__send_all_buttons, commands=['all_buttons'])
    dp.register_message_handler(__send_start_repeat_buttons, commands = ['startrepeat'])
    dp.register_message_handler(__delete_info_from_stack_condition, state=DeleteState.header)
    dp.register_message_handler(__processing_header_and_request_info, state=ContentState.header)
    dp.register_message_handler(__processing_info, state=ContentState.information)
    dp.register_message_handler(__processing_state_search, state=SearchInformationState.header)
    dp.register_message_handler(__echo)
