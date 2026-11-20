
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.config import settings
from app.states.listing import ListingForm

from decimal import Decimal, InvalidOperation
from aiogram.types import CallbackQuery
from app.keyboards.listings import listing_confirmation_keyboard

from html import escape
from aiogram.filters import Command


router = Router()


@router.message(F.text == "➕ Добавить объявление")
async def start_listing(
    message: Message,
    state: FSMContext,
) -> None:
    user_id = message.from_user.id if message.from_user else 0

    if user_id not in settings.admin_id_set:
        await message.answer("У вас нет прав для создания объявлений.")
        return

    await state.set_state(ListingForm.material)

    await message.answer(
        "➕ <b>Новое объявление</b>\n\n"
        "Шаг 1 из 9.\n"
        "Введите название материала:\n\n"
        "Например: песок карьерный, щебень гранитный."
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
        "Шаг 2 из 9.\n"
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
        "Выберите единицу измерения:\n\n"
        "Введите «м3» для кубических метров "
        "или «тонн» для тонн."
    )


@router.message(ListingForm.unit)
async def process_unit(
    message: Message,
    state: FSMContext,
) -> None:
    if not message.text:
        await message.answer("Введите единицу измерения: м3 или тонн.")
        return

    unit = message.text.strip().lower().replace("³", "3")

    if unit in ("м3", "м³", "m3"):
        unit_value = "m3"
        unit_label = "м³"
    elif unit in ("тонна", "тонны", "тонн", "т", "t"):
        unit_value = "ton"
        unit_label = "тонн"
    else:
        await message.answer(
            "Не понял единицу измерения.\n"
            "Введите «м3» или «тонн»."
        )
        return

    await state.update_data(unit=unit_value)
    await state.set_state(ListingForm.price)

    await message.answer(
        f"Единица измерения: {unit_label}.\n\n"
        "Шаг 6 из 10.\n"
        "Укажите цену за всё количество материала в рублях.\n\n"
        "Введите 0, если материал отдаётся бесплатно."
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

    price_text = "Бесплатно" if price == 0 else f"{price} руб."

    await message.answer(
        f"Цена: {price_text}.\n\n"
        "Шаг 7 из 10.\n"
        "Укажите город или населённый пункт:\n\n"
        "Например: Санкт-Петербург или Всеволожск."
    )


@router.message(ListingForm.city)
async def process_city(
    message: Message,
    state: FSMContext,
) -> None:
    if not message.text or not message.text.strip():
        await message.answer("Пожалуйста, укажите город или населённый пункт.")
        return

    city = message.text.strip()

    if len(city) > 100:
        await message.answer("Название города слишком длинное.")
        return

    await state.update_data(city=city)
    await state.set_state(ListingForm.address)

    await message.answer(
        "Шаг 8 из 10.\n"
        "Укажите адрес или местоположение материала.\n\n"
        "Например: улица Промышленная, участок 15.\n\n"
        "Если адрес неизвестен, отправьте дефис (-)."
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
    await state.set_state(ListingForm.photos)

    await message.answer(
        "Шаг 9 из 10.\n"
        "Теперь отправьте фотографии материала.\n\n"
        "Можно отправить несколько фотографий по одной.\n"
        "Когда закончите, отправьте команду /done.\n\n"
        "Если фотографий нет, сразу отправьте /done."
    )



@router.message(ListingForm.photos, F.photo)
async def process_photo(
    message: Message,
    state: FSMContext,
) -> None:
    photo = message.photo[-1]

    data = await state.get_data()
    photos = data.get("photos", [])

    if len(photos) >= 10:
        await message.answer(
            "Можно добавить не более 10 фотографий."
        )
        return

    photos.append(photo.file_id)

    await state.update_data(photos=photos)

    await message.answer(
        f"Фотография добавлена ({len(photos)}/10).\n"
        "Можете отправить следующую или завершить загрузку командой /done."
    )


@router.message(ListingForm.photos, F.text == "/done")
async def finish_photos(
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

    unit = "м³" if data.get("unit") == "m3" else "тонн"

    price_value = data.get("price", "0")
    price = (
        "Бесплатно"
        if Decimal(price_value) == 0
        else f"{escape(price_value)} руб."
    )

    photos = data.get("photos", [])

    preview = (
        "📋 <b>Проверьте объявление</b>\n\n"
        f"🪨 <b>Материал:</b> {material}\n"
        f"📝 <b>Заголовок:</b> {title}\n"
        f"📄 <b>Описание:</b> {description}\n"
        f"📦 <b>Количество:</b> {quantity} {unit}\n"
        f"💰 <b>Цена:</b> {price}\n"
        f"📍 <b>Город:</b> {city}\n"
        f"🏠 <b>Адрес:</b> {address}\n"
        f"📸 <b>Фотографий:</b> {len(photos)}\n\n"
        "Всё верно? Подтвердите объявление."
    )

    await state.set_state(ListingForm.confirmation)

    await message.answer(
        preview,
        reply_markup=listing_confirmation_keyboard(),
    )


@router.callback_query(
    ListingForm.confirmation,
    F.data == "listing:confirm",
)
async def confirm_listing(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    user_id = callback.from_user.id

    if user_id not in settings.admin_id_set:
        await callback.answer("У вас нет прав.", show_alert=True)
        return

    await callback.answer("Данные подтверждены!")

    if isinstance(callback.message, Message):
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(
            "✅ <b>Объявление подтверждено!</b>\n\n"
            "Данные сохранены в форме.\n"
            "Следующий этап — подключение сохранения в базу данных."
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

    if isinstance(callback.message, Message):
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(
            "❌ Создание объявления отменено."
        )


@router.message(Command("cancel"))
async def cancel_listing_creation(
    message: Message,
    state: FSMContext,
) -> None:
    current_state = await state.get_state()

    if current_state is None:
        await message.answer(
            "Сейчас у вас нет активного создания объявления."
        )
        return

    await state.clear()

    await message.answer(
        "❌ Создание объявления отменено.\n\n"
        "Все введённые данные очищены."
    )



