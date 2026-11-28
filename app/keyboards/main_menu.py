from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

FIND_MATERIALS = "🔎 Найти материалы"
ADD_LISTING = "➕ Добавить объявление"

MENU_BUTTONS = (
    FIND_MATERIALS,
    ADD_LISTING,
)


def main_menu_keyboard(is_admin: bool) -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(text=FIND_MATERIALS)],
    ]

    if is_admin:
        rows.append([KeyboardButton(text=ADD_LISTING)])

    return ReplyKeyboardMarkup(
        keyboard=rows,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие",
    )
