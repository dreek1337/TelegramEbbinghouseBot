from aiogram.dispatcher.filters.state import State, StatesGroup


# Создаем переменную состояния
class ContentState(StatesGroup):
    header = State()
    information = State()


class SearchInformationState(StatesGroup):
    header = State()


class DeleteState(StatesGroup):
    header = State()
