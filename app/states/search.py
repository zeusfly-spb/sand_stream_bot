from aiogram.fsm.state import State, StatesGroup


class SearchForm(StatesGroup):
    material = State()
    city = State()
    results = State()