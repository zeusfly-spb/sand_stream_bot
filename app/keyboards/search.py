from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from asgiref.sync import sync_to_async

from catalog.models import City, MaterialType

ANY_MATERIAL = "🪨 Любой материал"
ANY_CITY = "🗺 Вся область"
BACK = "🔙 В главное меню"
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


def _active_material_names() -> tuple[str, ...]:
    return tuple(
        MaterialType.objects.filter(is_active=True)
        .order_by("name")
        .values_list("name", flat=True)
    )


def _active_city_names() -> tuple[str, ...]:
    return tuple(
        City.objects.filter(is_active=True)
        .order_by("name")
        .values_list("name", flat=True)
    )


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


