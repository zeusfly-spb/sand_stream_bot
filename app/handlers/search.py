from html import escape

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.keyboards.main_menu import MENU_BUTTONS, main_menu_keyboard
from app.services.access import is_admin
from app.keyboards.search import (
    ALL_PRICES,
    ANY_CITY,
    ANY_MATERIAL,
    BACK,
    FREE_ONLY,
    PAID_ONLY,
    city_keyboard,
    material_keyboard,
    price_type_keyboard,
)
from app.services.search import find_city, find_material
from app.states.search import SearchForm
from app.handlers.catalog import show_catalog_page

router = Router()




async def _back_to_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "Возвращаемся в главное меню.",
        reply_markup=main_menu_keyboard(is_admin(message.from_user.id if message.from_user else None)),
    )


@router.message(F.text == "🔎 Найти материалы")
async def start_search(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(SearchForm.material)
    await state.update_data(
        search_mode="city",
        sort_by="newest",
        catalog_page=0,
    )

    await message.answer(
        "🔎 <b>Поиск строительных материалов</b>\n\n"
        "Шаг 1 из 3.\n"
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
        "Шаг 2 из 3.\n"
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
    await state.set_state(SearchForm.price_type)

    await message.answer(
        "Город выбран.\n\n"
        "Шаг 3 из 3.\n"
        "Выберите тип стоимости:",
        reply_markup=price_type_keyboard(),
    )


@router.message(SearchForm.price_type, F.text)
async def process_search_price(
    message: Message,
    state: FSMContext,
) -> None:
    text = (message.text or "").strip()

    if text == BACK or text in MENU_BUTTONS:
        await _back_to_menu(message, state)
        return

    price_filters = {
        ALL_PRICES: None,
        FREE_ONLY: "free",
        PAID_ONLY: "paid",
    }

    if text not in price_filters:
        await message.answer(
            "Выберите тип стоимости кнопкой.",
            reply_markup=price_type_keyboard(),
        )
        return

    await state.update_data(price_type=price_filters[text])

    found = await show_catalog_page(
        message=message,
        state=state,
        page=0,
    )

    # Сбрасываем имя состояния, но оставляем фильтры для пагинации/сортировки.
    await state.set_state(None)

    if found:
        await message.answer(
            "Поиск завершён. Для нового поиска нажмите "
            "«🔎 Найти материалы».",
            reply_markup=main_menu_keyboard(is_admin(message.from_user.id if message.from_user else None)),
        )
    else:
        await message.answer(
            "Объявления не найдены.\n"
            "Измените фильтры или начните новый поиск.",
            reply_markup=main_menu_keyboard(is_admin(message.from_user.id if message.from_user else None)),
        )
