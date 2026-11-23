from html import escape

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.config import settings
from app.keyboards.main_menu import main_menu_keyboard
from app.keyboards.search import ANY_CITY, ANY_MATERIAL, BACK, city_keyboard, material_keyboard
from app.services.search import find_city, find_material
from app.states.search import SearchForm
from app.handlers.catalog import show_catalog_page

MENU_BUTTONS = ("🔎 Найти материалы", "➕ Добавить объявление", "ℹ️ Помощь")

router = Router()


async def _back_to_menu(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id if message.from_user else 0
    is_admin = user_id in settings.admin_id_set
    await state.clear()
    await message.answer(
        "Возвращаемся в главное меню.",
        reply_markup=main_menu_keyboard(is_admin),
    )


@router.message(F.text == "🔎 Найти материалы")
async def start_search(message: Message, state: FSMContext) -> None:
    await state.set_state(SearchForm.material)
    await message.answer(
        "🔎 <b>Поиск материалов</b>\n\n"
        "Шаг 1 из 2.\n"
        "Выберите тип материала:",
        reply_markup=await material_keyboard(),
    )


@router.message(SearchForm.material, F.text)
async def process_search_material(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()

    if text == BACK or text in MENU_BUTTONS:
        await _back_to_menu(message, state)
        return

    if text == ANY_MATERIAL:
        material_id = None
        chosen = "любой"
    else:
        material = await find_material(text)
        if material is None:
            await message.answer(
                "Такого материала нет в списке.\n"
                "Выберите вариант кнопкой."
            )
            return
        material_id = material.id
        chosen = escape(material.name)

    await state.update_data(material_id=material_id)
    await state.set_state(SearchForm.city)

    await message.answer(
        f"Материал: <b>{chosen}</b>.\n\n"
        "Шаг 2 из 2.\n"
        "Выберите город:",
        reply_markup=await city_keyboard(),
    )


@router.message(SearchForm.city, F.text)
async def process_search_city(
    message: Message,
    state: FSMContext,
) -> None:
    text = (message.text or "").strip()

    if text == BACK or text in MENU_BUTTONS:
        await _back_to_menu(message, state)
        return

    if text == ANY_CITY:
        city_id = None
    else:
        city = await find_city(text)

        if city is None:
            await message.answer(
                "Такого города нет в списке.\n"
                "Выберите вариант кнопкой."
            )
            return

        city_id = city.id

    await state.update_data(city_id=city_id)

    await show_catalog_page(
        message=message,
        state=state,
        page=0,
    )

    user_id = message.from_user.id if message.from_user else 0

    await message.answer(
        "Поиск завершён. Для нового поиска нажмите "
        "«🔎 Найти материалы».",
        reply_markup=main_menu_keyboard(
            user_id in settings.admin_id_set
        ),
    )
