# Чтение файла
with open('hellotext.txt', 'r') as hello_text:
    text = ''.join(i for i in hello_text)

# Очередь
stack = []


# Замена спецаильных символов для работы parse_mode
def replace_symbol(arg):
    special_symbol = ('\\', '`', '*', '_', '{', '}', '[', ']', '(', ')', '#', '+', '-', '.', '!')

    for i in special_symbol:
        if i in arg:
            arg = arg.replace(i, f'\\{i}')
        else:
            continue

    return arg


# Текст для /help команды
help_message = """
*Доступные команды:*\n
/start \- запуск бота и отображение приветствия\n
/startrepeat \- начало работы с ботом\n
/all\_buttons \- отображает все возможные кнопки

_*__Помощь по кнопочкам:__*_

*Добавить карточку в хранилище и очередь* \- создает карточку, которая будет приходить к вам с определенным интервалом\.\n
*Удалить карточку из очереди* \- удаляет один элемент из очереди по ключевому слову\.\n
*Святое хранилище* \- предоставляет все возможные функции для работы с хранилищем информации\.\n
*Очистить хранилище и очередь* \- название говорит само за себя\.\n
*Показать все ключевые слова в хранилище* \- и тут тоже\.\n
*Найти карточку в хранилище* \- ищет карточку по ключевому слову\.\n
*Показать очередь* \- отображает все слова, которые сейчас в работе и ждут отправки\.\n
*Очистить очередь* \- очищает очередь, но сохраняет карточки в базе данных\.\n
*Помощь* \- и так все ясно\.
"""
