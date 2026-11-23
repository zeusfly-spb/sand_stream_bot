
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton


QUANTITY_UNITS = {
    "м³": "m3",
    "Тонны": "ton",
    "Килограммы": "kg",
    "Мешки": "bag",
    "Штуки": "pcs",
}


def quantity_unit_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=label)]
            for label in QUANTITY_UNITS
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def listing_confirmation_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Подтвердить",
                    callback_data="listing:confirm",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="❌ Отменить",
                    callback_data="listing:cancel",
                ),
            ],
        ]
    )

def location_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="📍 Отправить геопозицию",
                    request_location=True,
                )
            ],
            [KeyboardButton(text="Пропустить")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
