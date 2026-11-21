from html import escape

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.config import settings
from app.keyboards.main_menu import main_menu_keyboard
from app.keyboards.search import ANY_CITY, ANY_MATERIAL, BACK, city_keyboard, material_keyboard
from app.services.search import find_city, find_material, search_listings
from app.states.search import SearchForm

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
async def process_search_city(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()

    if text == BACK or text in MENU_BUTTONS:
        await _back_to_menu(message, state)
        return

    data = await state.get_data()
    material_id = data.get("material_id")

    if text == ANY_CITY:
        city_id = None
        chosen_city = "вся область"
    else:
        city = await find_city(text)
        if city is None:
            await message.answer(
                "Такого города нет в списке.\n"
                "Выберите вариант кнопкой."
            )
            return
        city_id = city.id
        chosen_city = escape(city.name)

    results = await search_listings(material_id, city_id)

    await state.clear()

    if not results:
        await message.answer(
            "😕 <b>Ничего не нашлось</b>\n\n"
            f"Запрос: {chosen_city}.\n"
            "Попробуйте «Вся область» или зайдите позже.",
            reply_markup=main_menu_keyboard(
                (message.from_user.id if message.from_user else 0)
                in settings.admin_id_set
            ),
        )
        return

    lines = [f"🔎 <b>Найдено объявлений: {len(results)}</b>\n"]
    for index, listing in enumerate(results, start=1):
        material_name = (
            listing.material_type.name if listing.material_type else listing.material_raw or "—"
        )
        city_name = listing.city.name if listing.city else listing.city_raw or "—"
        price = (
            "Бесплатно"
            if listing.price == 0
            else f"{listing.price} руб. {listing.price_unit}".strip()
        )
        phone = listing.contact_phone or getattr(listing.seller, "phone", "") or "не указан"


        lines.append(
            f"<b>{index}. {escape(listing.title)}</b>\n"
            f"🪨 {escape(material_name)} · 📍 {escape(city_name)}\n"
            f"💰 {escape(price)}"
            + (f" · 📦 {escape(listing.quantity)}" if listing.quantity else "")
            + f"\n📞 {escape(phone)}\n"
        )

    lines.append("Для нового поиска нажмите «🔎 Найти материалы».")

    await message.answer(
        "\n".join(lines),
        reply_markup=main_menu_keyboard(
            (message.from_user.id if message.from_user else 0)
            in settings.admin_id_set
        ),
    )
