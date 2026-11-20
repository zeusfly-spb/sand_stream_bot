
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


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
