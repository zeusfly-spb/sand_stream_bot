
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def catalog_keyboard(
    listings: list,
    page: int,
    has_next: bool,
) -> InlineKeyboardMarkup:
    """Клавиатура списка объявлений."""

    keyboard = []

    # Кнопка просмотра каждого объявления
    for index, listing in enumerate(listings, start=1):
        title = listing.title.strip()

        if len(title) > 35:
            title = title[:32] + "..."

        keyboard.append(
            [
                InlineKeyboardButton(
                    text=f"📋 {index}. {title}",
                    callback_data=f"catalog:detail:{listing.id}",
                )
            ]
        )

    # Навигация между страницами
    navigation = []

    if page > 0:
        navigation.append(
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=f"catalog:page:{page - 1}",
            )
        )

    if has_next:
        navigation.append(
            InlineKeyboardButton(
                text="Вперёд ➡️",
                callback_data=f"catalog:page:{page + 1}",
            )
        )

    if navigation:
        keyboard.append(navigation)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def listing_detail_keyboard(page: int) -> InlineKeyboardMarkup:
    """Клавиатура подробной карточки объявления."""

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⬅️ К результатам поиска",
                    callback_data=f"catalog:page:{page}",
                )
            ]
        ]
    )
