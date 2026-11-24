from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

FIND_MATERIALS = "🔎 Найти материалы"
MY_SUBSCRIPTIONS = "🔔 Мои подписки"
ADD_LISTING = "➕ Добавить объявление"
MANAGE_LISTINGS = "⚙️ Управление объявлениями"

MENU_BUTTONS = (
    FIND_MATERIALS,
    MY_SUBSCRIPTIONS,
    ADD_LISTING,
    MANAGE_LISTINGS,
)


def main_menu_keyboard(is_admin: bool) -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(text=FIND_MATERIALS)],
        [KeyboardButton(text=MY_SUBSCRIPTIONS)],
    ]

    if is_admin:
        rows.append([KeyboardButton(text=ADD_LISTING)])
        rows.append([KeyboardButton(text=MANAGE_LISTINGS)])

    return ReplyKeyboardMarkup(
        keyboard=rows,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие",
    )
