from functools import lru_cache

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

ALL_PRICES = "💰 Все объявления"
FREE_ONLY = "🆓 Только бесплатные"
PAID_ONLY = "💵 Только платные"


def _build(buttons: list[str]) -> ReplyKeyboardMarkup:
    rows = [buttons[i : i + 2] for i in range(0, len(buttons), 2)]
    keyboard = [[KeyboardButton(text=b) for b in row] for row in rows]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Выберите вариант",
    )


@lru_cache(maxsize=1)
def _active_material_names() -> tuple[str, ...]:
    return tuple(
        MaterialType.objects.filter(is_active=True)
        .order_by("name")
        .values_list("name", flat=True)
    )


@lru_cache(maxsize=1)
def _active_city_names() -> tuple[str, ...]:
    return tuple(
        City.objects.filter(is_active=True)
        .order_by("name")
        .values_list("name", flat=True)
    )


def clear_directory_cache() -> None:
    _active_material_names.cache_clear()
    _active_city_names.cache_clear()


@sync_to_async
def material_keyboard() -> ReplyKeyboardMarkup:
    return _build([ANY_MATERIAL, *_active_material_names(), BACK])


@sync_to_async
def city_keyboard() -> ReplyKeyboardMarkup:
    return _build([ANY_CITY, *_active_city_names(), BACK])


@sync_to_async
def listing_city_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура городов для создания объявления (без «Вся область»)."""
    return _build([*_active_city_names(), BACK])


def price_type_keyboard() -> ReplyKeyboardMarkup:
    return _build([
        ALL_PRICES,
        FREE_ONLY,
        PAID_ONLY,
        BACK,
    ])


def search_mode_keyboard() -> ReplyKeyboardMarkup:
    # «Рядом со мной» временно скрыто до готового geo-сервиса.
    return _build([
        SEARCH_BY_CITY,
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
