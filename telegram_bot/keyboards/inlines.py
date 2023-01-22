from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

stack_button = InlineKeyboardButton('Показать очередь', callback_data='stack')
clear_stack = InlineKeyboardButton('Очистить очередь', callback_data='clear_stack')
storage_button = InlineKeyboardButton('Святое хранилище', callback_data='storage')
delete_element_from_stack = InlineKeyboardButton('Удалить карточку из очереди', callback_data='delete')
clear_stack_and_storage = InlineKeyboardButton('Очистить хранилище и очередь', callback_data='clear_storage')
saved_info_button = InlineKeyboardButton('Показать все ключевые слова в хранилище', callback_data='all_information')
add_repeat_info_button = InlineKeyboardButton('Добавить карточку в хранилище и очередь', callback_data='startrepeat')
help_button = InlineKeyboardButton('Помощь', callback_data='help')
search_button = InlineKeyboardButton('Найти карточку в хранилище', callback_data='search')

# Универсальный инлайн
universal_inline_buttons = (InlineKeyboardMarkup().add(add_repeat_info_button).add(search_button).add(stack_button)
                                                  .add(storage_button).add(help_button))


