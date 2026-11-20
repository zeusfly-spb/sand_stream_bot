from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def main_menu_keyboard(is_admin: bool) -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(text="🔎 Найти материалы")],
        [KeyboardButton(text="🔔 Мои подписки")],
    ]

    if is_admin:
        rows.append([KeyboardButton(text="➕ Добавить объявление")])
        rows.append([KeyboardButton(text="⚙️ Управление объявлениями")])

    return ReplyKeyboardMarkup(
        keyboard=rows,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие",
    )
