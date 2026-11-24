from aiogram.fsm.state import State, StatesGroup


class SearchForm(StatesGroup):
    mode = State()
    material = State()
    city = State()
    price_type = State()
    results = State()
    geo_location = State()
    geo_radius = State()
    


