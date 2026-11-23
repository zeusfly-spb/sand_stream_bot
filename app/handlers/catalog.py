from html import escape
from uuid import UUID

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from app.keyboards.catalog import (
    catalog_keyboard,
    catalog_sort_keyboard,
    listing_detail_keyboard,
)

from app.services.search import (
    get_listing_by_id,
    get_listings_page,
)
from app.states.search import SearchForm

router = Router()


@router.callback_query(F.data.startswith("catalog:detail:"))
async def show_listing_detail(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    listing_id_raw = callback.data.split(":", maxsplit=2)[2]
    try:
        listing_id = UUID(listing_id_raw)
    except ValueError:
        await callback.answer("Некорректный номер объявления.", show_alert=True)
        return

    listing = await get_listing_by_id(listing_id)

    if listing is None:
        await callback.answer(
            "Объявление больше не доступно.",
            show_alert=True,
        )
        return

    material = (
        listing.material_type.name
        if listing.material_type
        else listing.material_raw or "Не указан"
    )

    city = (
        listing.city.name
        if listing.city
        else listing.city_raw or "Не указан"
    )

    if listing.price == 0:
        price = "Бесплатно"
    elif listing.price is not None:
        price_value = f"{listing.price:,.2f}".replace(",", " ")
        price_unit = listing.price_unit.strip()

        if price_unit.lower().startswith("за "):
            price_unit = price_unit[3:]

        price = f"{price_value} ₽"
        if price_unit:
            price += f" / {price_unit}"
    else:
        price = "Цена не указана"
    
    if listing.contact_phone:
        phone = (
            f'<a href="tel:{escape(listing.contact_phone, quote=True)}">'
            f'{escape(listing.contact_phone)}</a>'
        )
    else:
        phone = "Не указан"
    
    quantity = listing.quantity or "Не указано"
    if listing.quantity_unit:
        quantity += f" {listing.quantity_unit}"

    text = (
        f"<b>{escape(listing.title)}</b>\n\n"
        f"🪨 Материал: {escape(material)}\n"
        f"📍 Город: {escape(city)}\n"
        f"📦 Количество: {escape(quantity)}\n"
        f"💰 Цена: {escape(price)}\n\n"
        f"<b>Описание:</b>\n"
        f"{escape(listing.description or 'Описание отсутствует')}\n\n"
        f"📌 Адрес: {escape(listing.address or 'Не указан')}\n"
        f"👤 Продавец: {escape(listing.contact_name or 'Не указан')}\n"
        f"👤 Продавец: {escape(listing.contact_name or 'Не указан')}\n"
        f"📞 Телефон: {phone}"
    )

    data = await state.get_data()
    current_page = data.get("catalog_page", 0)

    await callback.message.edit_text(
        text,
        reply_markup=listing_detail_keyboard(page=current_page),
    )
    await callback.answer()


async def show_catalog_page(
    message: Message,
    state: FSMContext,
    page: int = 0,
    edit: bool = False,
) -> None:
    data = await state.get_data()

    material_id = data.get("material_id")
    city_id = data.get("city_id")
    sort_by = data.get("sort_by", "newest")
    price_type = data.get("price_type")

    listings, has_next = await get_listings_page(
        material_id=material_id,
        city_id=city_id,
        page=page,
        sort_by=sort_by,
        price_type=price_type,
    )

    if not listings:
        await message.answer("Объявления не найдены.")
        return

    await state.update_data(catalog_page=page)
    await state.set_state(SearchForm.results)

    lines = [
        f"<b>🔎 Результаты поиска — страница {page + 1}</b>",
        "",
    ]

    for listing in listings:
        material = (
            listing.material_type.name
            if listing.material_type
            else listing.material_raw or "Материал не указан"
        )
        city = (
            listing.city.name
            if listing.city
            else listing.city_raw or "Город не указан"
        )
        price = (
            "Бесплатно"
            if listing.price == 0
            else f"{listing.price} ₽ {listing.price_unit}"
            if listing.price is not None
            else "Цена не указана"
        )

        lines.append(
            f"🪨 <b>{escape(listing.title)}</b>\n"
            f"Материал: {escape(material)}\n"
            f"Город: {escape(city)}\n"
            f"Количество: {escape(listing.quantity or 'Не указано')}\n"
            f"Цена: {escape(price)}"
        )
        lines.append("")

    text = "\n".join(lines)
    listing_keyboard = catalog_keyboard(listings, page, has_next)
    sort_keyboard = catalog_sort_keyboard(sort_by)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            *listing_keyboard.inline_keyboard,
            *sort_keyboard.inline_keyboard,
        ]
    )

    if edit:
        await message.edit_text(
            text,
            reply_markup=keyboard,
        )
    else:
        await message.answer(
            text,
            reply_markup=keyboard,
        )


@router.callback_query(F.data.startswith("catalog:page:"))
async def change_catalog_page(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    try:
        page = int(callback.data.split(":")[-1])
    except (ValueError, AttributeError):
        await callback.answer("Некорректный номер страницы.", show_alert=True)
        return

    if page < 0:
        await callback.answer("Это первая страница.")
        return

    data = await state.get_data()

    if "material_id" not in data or "city_id" not in data:
        await callback.answer(
            "Поиск устарел. Начните новый поиск.",
            show_alert=True,
        )
        return

    await show_catalog_page(
        callback.message,
        state,
        page,
        edit=True,
    )
    await callback.answer()


@router.callback_query(F.data.startswith("catalog:sort:"))
async def change_catalog_sort(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    sort_by = callback.data.split(":")[-1]

    allowed_sorts = {
        "newest",
        "price_asc",
        "price_desc",
    }

    if sort_by not in allowed_sorts:
        await callback.answer(
            "Неизвестный способ сортировки.",
            show_alert=True,
        )
        return

    data = await state.get_data()

    if "material_id" not in data or "city_id" not in data:
        await callback.answer(
            "Поиск устарел. Начните новый поиск.",
            show_alert=True,
        )
        return

    await state.update_data(
        sort_by=sort_by,
        catalog_page=0,
    )

    await show_catalog_page(
        callback.message,
        state,
        page=0,
        edit=True,
    )

    await callback.answer("Сортировка изменена.")



