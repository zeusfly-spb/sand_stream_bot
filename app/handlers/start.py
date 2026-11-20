from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.config import settings
from app.keyboards.main_menu import main_menu_keyboard

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    user_id = message.from_user.id if message.from_user else 0
    is_admin = user_id in settings.admin_id_set

    greeting = (
        "Добро пожаловать в <b>SandStreamBot</b>!\n\n"
        "Здесь можно будет находить предложения песка, гравия, щебня "
        "и других сыпучих строительных материалов."
    )

    if is_admin:
        greeting += "\n\n<i>У вас есть права администратора.</i>"

    await message.answer(greeting, reply_markup=main_menu_keyboard(is_admin))
