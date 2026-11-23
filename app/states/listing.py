
from aiogram.fsm.state import State, StatesGroup


class ListingForm(StatesGroup):
    material = State()
    title = State()
    description = State()
    quantity = State()
    unit = State()
    price = State()
    city = State()
    address = State()
    location = State()
    confirmation = State()
