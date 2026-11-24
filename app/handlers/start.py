from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.config import settings
from app.keyboards.main_menu import (
    MANAGE_LISTINGS,
    MY_SUBSCRIPTIONS,
    main_menu_keyboard,
)

router = Router()


def _is_admin(message: Message) -> bool:
    user_id = message.from_user.id if message.from_user else 0
    return user_id in settings.admin_id_set


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    is_admin = _is_admin(message)

    greeting = (
        "Добро пожаловать в <b>SandStreamBot</b>!\n\n"
        "Здесь можно будет находить предложения песка, гравия, щебня "
        "и других сыпучих строительных материалов."
    )

    if is_admin:
        greeting += "\n\n<i>У вас есть права администратора.</i>"

    await message.answer(greeting, reply_markup=main_menu_keyboard(is_admin))


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()

    if current_state is None:
        await message.answer(
            "Сейчас нет активного сценария.",
            reply_markup=main_menu_keyboard(_is_admin(message)),
        )
        return

    await state.clear()
    await message.answer(
        "❌ Действие отменено.\n\n"
        "Все введённые данные очищены.",
        reply_markup=main_menu_keyboard(_is_admin(message)),
    )


@router.message(F.text == MY_SUBSCRIPTIONS)
async def stub_subscriptions(message: Message) -> None:
    await message.answer(
        "🔔 Подписки скоро появятся.\n\n"
        "Здесь можно будет следить за новыми объявлениями "
        "по выбранному материалу и городу."
    )


@router.message(F.text == MANAGE_LISTINGS)
async def stub_manage_listings(message: Message) -> None:
    if not _is_admin(message):
        await message.answer("У вас нет прав для управления объявлениями.")
        return

    await message.answer(
        "⚙️ Управление объявлениями скоро появится.\n\n"
        "Пока можно создавать новые через «➕ Добавить объявление»."
    )
