from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.services.access import is_admin
from app.keyboards.main_menu import (
    main_menu_keyboard,
)

router = Router()



@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    admin_access = is_admin(message.from_user.id if message.from_user else None)

    greeting = (
        "Добро пожаловать в <b>SandStreamBot</b>!\n\n"
        "Здесь можно будет находить предложения песка, гравия, щебня "
        "и других сыпучих строительных материалов."
    )

    if admin_access:
        greeting += "\n\n<i>У вас есть права администратора.</i>"

    await message.answer(greeting, reply_markup=main_menu_keyboard(admin_access))


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id if message.from_user else None
    current_state = await state.get_state()

    if current_state is None:
        await message.answer(
            "Сейчас нет активного сценария.",
            reply_markup=main_menu_keyboard(is_admin(user_id)),
        )
        return

    await state.clear()
    await message.answer(
        "❌ Действие отменено.\n\n"
        "Все введённые данные очищены.",
        reply_markup=main_menu_keyboard(is_admin(user_id)),
    )


