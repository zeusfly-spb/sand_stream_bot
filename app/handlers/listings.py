
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

from app.states.listing import ListingForm

from decimal import Decimal, InvalidOperation
from app.keyboards.listings import (
    listing_confirmation_keyboard,
    quantity_unit_keyboard,
    location_keyboard,
    QUANTITY_UNITS,
)
from app.keyboards.main_menu import ADD_LISTING, main_menu_keyboard
from app.keyboards.search import BACK, listing_city_keyboard
from app.services.search import find_city
from app.services.access import is_admin

from html import escape
from app.services.listings import create_listing, UNIT_LABELS
import logging
logger = logging.getLogger(__name__)



router = Router()



async def show_listing_preview(
    message: Message,
    state: FSMContext,
) -> None:
    data = await state.get_data()

    material = escape(data.get("material_name", "—"))
    title = escape(data.get("title", "—"))
    description = escape(data.get("description") or "Не указано")
    quantity = escape(data.get("quantity", "—"))
    city = escape(data.get("city", "—"))
    address = escape(data.get("address") or "Не указан")

    unit = UNIT_LABELS[data["unit"]]

    price_value = data.get("price", "0")
    price = (
        "Бесплатно"
        if Decimal(price_value) == 0
        else f"{escape(price_value)} руб. за {unit}"
    )

    latitude = data.get("latitude")
    longitude = data.get("longitude")

    location_text = (
        "Получена"
        if latitude is not None and longitude is not None
        else "Не указана"
    )

    preview = (
        "📋 <b>Шаг 10 из 10. Проверьте объявление</b>\n\n"
        f"🪨 <b>Материал:</b> {material}\n"
        f"📝 <b>Заголовок:</b> {title}\n"
        f"📄 <b>Описание:</b> {description}\n"
        f"📦 <b>Количество:</b> {quantity} {unit}\n"
        f"💰 <b>Цена:</b> {price}\n"
        f"📍 <b>Город:</b> {city}\n"
        f"🏠 <b>Адрес:</b> {address}\n"
        f"🌍 <b>Геопозиция:</b> {location_text}\n\n"
        "Всё верно? Подтвердите объявление."
    )

    await state.set_state(ListingForm.confirmation)

    await message.answer(
        preview,
        reply_markup=listing_confirmation_keyboard(),
    )


@router.message(F.text == ADD_LISTING)
async def start_listing(
    message: Message,
    state: FSMContext,
) -> None:
    user_id = message.from_user.id if message.from_user else 0

    if not is_admin(user_id):
        await message.answer(
            "У вас нет прав для создания объявлений."
        )
        return

    current_state = await state.get_state()

    if current_state is not None and current_state.startswith("ListingForm:"):
        await message.answer(
            "⚠️ У вас уже есть незавершённое объявление.\n\n"
            "Продолжите заполнение или отправьте /cancel, "
            "чтобы начать заново."
        )
        return

    await state.clear()
    await state.set_state(ListingForm.material)

    await message.answer(
        "➕ <b>Новое объявление</b>\n\n"
        "Шаг 1 из 10.\n"
        "Введите название материала:\n\n"
        "Например: песок карьерный, щебень гранитный.",
        reply_markup=ReplyKeyboardRemove(),
    )



@router.message(ListingForm.material)
async def process_material(
    message: Message,
    state: FSMContext,
) -> None:
    if not message.text or not message.text.strip():
        await message.answer("Пожалуйста, введите название материала.")
        return

    await state.update_data(material_name=message.text.strip())

    await state.set_state(ListingForm.title)

    await message.answer(
        "Шаг 2 из 10.\n"
        "Введите заголовок объявления:\n\n"
        "Например: Продам 20 м³ карьерного песка."
    )


@router.message(ListingForm.title)
async def process_title(
    message: Message,
    state: FSMContext,
) -> None:
    if not message.text or not message.text.strip():
        await message.answer("Пожалуйста, введите заголовок объявления.")
        return

    await state.update_data(title=message.text.strip())
    await state.set_state(ListingForm.description)

    await message.answer(
        "Шаг 3 из 10.\n"
        "Введите описание объявления:\n\n"
        "Например: Чистый карьерный песок, без примесей. "
        "Самовывоз или доставка."
    )


@router.message(ListingForm.description)
async def process_description(
    message: Message,
    state: FSMContext,
) -> None:
    if not message.text:
        await message.answer("Введите описание или отправьте текст.")
        return

    description = message.text.strip()

    await state.update_data(
        description="" if description == "-" else description
    )

    await state.set_state(ListingForm.quantity)

    await message.answer(
        "Шаг 4 из 10.\n"
        "Укажите количество материала:\n\n"
        "Например: 20 или 15.5"
    )


@router.message(ListingForm.quantity)
async def process_quantity(
    message: Message,
    state: FSMContext,
) -> None:
    if not message.text:
        await message.answer("Введите количество числом.")
        return

    try:
        quantity = Decimal(message.text.strip().replace(",", "."))
    except InvalidOperation:
        await message.answer(
            "Некорректное число. Например: 20 или 15.5"
        )
        return

    if not quantity.is_finite() or quantity <= 0:
        await message.answer("Количество должно быть больше нуля.")
        return

    if quantity > Decimal("999999999.999"):
        await message.answer("Указано слишком большое количество.")
        return

    normalized = quantity.normalize()

    if normalized.as_tuple().exponent < -3:
        await message.answer(
            "Допускается не более трёх знаков после запятой."
        )
        return

    await state.update_data(quantity=str(quantity))
    await state.set_state(ListingForm.unit)

    await message.answer(
        "Шаг 5 из 10.\n"
        "Выберите единицу измерения материала:",
        reply_markup=quantity_unit_keyboard(),
    )


@router.message(ListingForm.unit)
async def process_unit(message: Message, state: FSMContext) -> None:
    if not message.text:
        await message.answer(
            "Выберите единицу измерения:",
            reply_markup=quantity_unit_keyboard(),
        )
        return

    unit_value = QUANTITY_UNITS.get(message.text.strip())

    if not unit_value:
        await message.answer(
            "Пожалуйста, выберите единицу измерения кнопкой ниже.",
            reply_markup=quantity_unit_keyboard(),
        )
        return

    await state.update_data(unit=unit_value)
    await state.set_state(ListingForm.price)

    await message.answer(
        f"Единица измерения: {message.text.strip()}.\n\n"
        "Шаг 6 из 10.\n"
        f"Укажите цену за 1 {message.text.strip().lower()} в рублях.\n\n"
        "Например: 850.\n"
        "Введите 0, если материал отдаётся бесплатно.",
        reply_markup=ReplyKeyboardRemove(),
    )

@router.message(ListingForm.price)
async def process_price(
    message: Message,
    state: FSMContext,
) -> None:
    if not message.text:
        await message.answer("Введите цену числом.")
        return

    try:
        price = Decimal(message.text.strip().replace(",", "."))
    except InvalidOperation:
        await message.answer(
            "Некорректная цена. Например: 15000 или 15000.50"
        )
        return

    if not price.is_finite() or price < 0:
        await message.answer(
            "Цена не может быть отрицательной."
        )
        return

    if price > Decimal("9999999999.99"):
        await message.answer("Указана слишком большая цена.")
        return

    if price.as_tuple().exponent < -2:
        await message.answer(
            "Цена может содержать не более двух знаков после запятой."
        )
        return

    await state.update_data(price=str(price))
    await state.set_state(ListingForm.city)

    data = await state.get_data()
    unit_label = UNIT_LABELS[data["unit"]]

    price_text = (
        "Бесплатно"
        if price == 0
        else f"{price} руб. за {unit_label}"
    )

    await message.answer(
        f"Цена: {price_text}.\n\n"
        "Шаг 7 из 10.\n"
        "Выберите город из списка:",
        reply_markup=await listing_city_keyboard(),
    )


@router.message(ListingForm.city)
async def process_city(
    message: Message,
    state: FSMContext,
) -> None:
    text = (message.text or "").strip()

    if not text:
        await message.answer(
            "Выберите город кнопкой.",
            reply_markup=await listing_city_keyboard(),
        )
        return

    if text == BACK:
        await state.clear()
        user_id = message.from_user.id if message.from_user else 0
        await message.answer(
            "Создание объявления отменено.",
            reply_markup=main_menu_keyboard(is_admin(user_id)),
        )
        return

    city = await find_city(text)
    if city is None:
        await message.answer(
            "Такого города нет в списке.\n"
            "Выберите вариант кнопкой.",
            reply_markup=await listing_city_keyboard(),
        )
        return

    await state.update_data(city=city.name, city_id=city.id)
    await state.set_state(ListingForm.address)

    await message.answer(
        f"Город: <b>{escape(city.name)}</b>.\n\n"
        "Шаг 8 из 10.\n"
        "Укажите адрес или местоположение материала.\n\n"
        "Например: улица Промышленная, участок 15.\n\n"
        "Если адрес неизвестен, отправьте дефис (-).",
        reply_markup=ReplyKeyboardRemove(),
    )



@router.message(ListingForm.address)
async def process_address(
    message: Message,
    state: FSMContext,
) -> None:
    if not message.text:
        await message.answer(
            "Введите адрес или отправьте дефис (-), если адрес неизвестен."
        )
        return

    address = message.text.strip()

    if address == "-":
        address = ""

    if len(address) > 255:
        await message.answer("Адрес слишком длинный. Максимум 255 символов.")
        return

    await state.update_data(address=address)

    await state.set_state(ListingForm.location)
    await message.answer(
        "Шаг 9 из 10.\n"
        "Отправьте геопозицию места, где находится материал.\n\n"
        "Нажмите кнопку «📍 Отправить геопозицию» "
        "или выберите «Пропустить», если координаты неизвестны.",
        reply_markup=location_keyboard(),
    )
    return

@router.message(ListingForm.location, F.text == "Пропустить")
async def skip_listing_location(
    message: Message,
    state: FSMContext,
) -> None:
    await state.update_data(
        latitude=None,
        longitude=None,
    )

    await message.answer(
        "Геопозиция пропущена.",
        reply_markup=ReplyKeyboardRemove(),
    )

    await show_listing_preview(message, state)
    
@router.message(ListingForm.location, F.location)
async def process_listing_location(
    message: Message,
    state: FSMContext,
) -> None:
    if not message.location:
        return

    await state.update_data(
        latitude=message.location.latitude,
        longitude=message.location.longitude,
    )

    await message.answer(
        "✅ Геопозиция получена!",
        reply_markup=ReplyKeyboardRemove(),
    )

    await show_listing_preview(message, state)

@router.callback_query(
    ListingForm.confirmation,
    F.data == "listing:confirm",
)
async def confirm_listing(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    user = callback.from_user

    if not is_admin(user.id):
        await callback.answer(
            "У вас нет прав.",
            show_alert=True,
        )
        return

    data = await state.get_data()

    telegram_user_data = {
        "telegram_id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
    }

    try:
        listing_id = await create_listing(
            data,
            telegram_user_data,
        )

    except Exception:
        logger.exception("Ошибка создания объявления")
        await callback.answer(
            "Не удалось сохранить объявление.",
            show_alert=True,
        )
        return

    await state.clear()
    await callback.answer("Объявление сохранено!")

    if isinstance(callback.message, Message):
        await callback.message.edit_reply_markup(
            reply_markup=None
        )
        await callback.message.answer(
            "✅ <b>Объявление создано!</b>\n\n"
            f"Номер объявления: <b>#{listing_id}</b>\n"
            "Статус: Активно.",
            reply_markup=main_menu_keyboard(is_admin(user.id)),
        )


@router.callback_query(
    ListingForm.confirmation,
    F.data == "listing:cancel",
)
async def cancel_listing(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    await state.clear()
    await callback.answer("Создание объявления отменено.")

    user_id = callback.from_user.id if callback.from_user else 0

    if isinstance(callback.message, Message):
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(
            "❌ Создание объявления отменено.",
            reply_markup=main_menu_keyboard(is_admin(user_id)),
        )





