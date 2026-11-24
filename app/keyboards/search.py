from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from asgiref.sync import sync_to_async

from catalog.models import City, MaterialType

ANY_MATERIAL = "🪨 Любой материал"
ANY_CITY = "🗺 Вся область"
BACK = "🔙 В главное меню"
SEARCH_BY_CITY = "🏙 Поиск по городу"
SEARCH_NEARBY = "📍 Рядом со мной"

GEO_RADII = {
    "5 км": 5,
    "10 км": 10,
    "25 км": 25,
    "50 км": 50,
    "100 км": 100,
}

def _build(buttons: list[str]) -> ReplyKeyboardMarkup:
    rows = [buttons[i : i + 2] for i in range(0, len(buttons), 2)]
    keyboard = [[KeyboardButton(text=b) for b in row] for row in rows]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Выберите вариант",
    )


@sync_to_async
def material_keyboard() -> ReplyKeyboardMarkup:
    names = list(
        MaterialType.objects.filter(is_active=True)
        .order_by("name")
        .values_list("name", flat=True)
    )
    return _build([ANY_MATERIAL] + names + [BACK])


@sync_to_async
def city_keyboard() -> ReplyKeyboardMarkup:
    names = list(
        City.objects.filter(is_active=True)
        .order_by("name")
        .values_list("name", flat=True)
    )
    return _build([ANY_CITY] + names + [BACK])


ALL_PRICES = "💰 Все объявления"
FREE_ONLY = "🆓 Только бесплатные"
PAID_ONLY = "💵 Только платные"


def price_type_keyboard() -> ReplyKeyboardMarkup:
    return _build([
        ALL_PRICES,
        FREE_ONLY,
        PAID_ONLY,
        BACK,
    ])

def search_mode_keyboard() -> ReplyKeyboardMarkup:
    return _build([
        SEARCH_BY_CITY,
        SEARCH_NEARBY,
        BACK,
    ])


def geo_location_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="📍 Отправить геолокацию",
                    request_location=True,
                )
            ],
            [KeyboardButton(text=BACK)],
        ],
        resize_keyboard=True,
        input_field_placeholder="Отправьте свою геолокацию",
    )


def geo_radius_keyboard() -> ReplyKeyboardMarkup:
    return _build([
        *GEO_RADII.keys(),
        BACK,
    ])

