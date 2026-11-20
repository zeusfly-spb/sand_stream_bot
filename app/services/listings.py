
from asgiref.sync import sync_to_async
from decimal import Decimal
from django.db import transaction
from accounts.models import TelegramUser
from catalog.models import Listing, Material



def _get_active_listings(limit: int = 10) -> list[dict]:
    """Получает список активных объявлений из базы данных."""

    listings = (
        Listing.objects
        .filter(status=Listing.Status.ACTIVE)
        .select_related("material")
        .order_by("-created_at")[:limit]
    )

    return [
        {
            "id": listing.id,
            "title": listing.title,
            "material": listing.material.name,
            "quantity": listing.quantity,
            "unit": listing.unit,
            "price": listing.price,
            "city": listing.city,
        }
        for listing in listings
    ]


async def get_active_listings(limit: int = 10) -> list[dict]:
    """Асинхронно получает активные объявления."""

    return await sync_to_async(
        _get_active_listings,
        thread_sensitive=True,
    )(limit)



def _create_listing(
    data: dict,
    telegram_user_data: dict,
) -> int:
    """Создаёт объявление и связывает его с Telegram-пользователем."""

    with transaction.atomic():
        # Находим или регистрируем Telegram-пользователя.
        telegram_user, _ = TelegramUser.objects.update_or_create(
            telegram_id=telegram_user_data["telegram_id"],
            defaults={
                "username": telegram_user_data.get("username") or "",
                "first_name": telegram_user_data.get("first_name") or "",
                "last_name": telegram_user_data.get("last_name") or "",
            },
        )

        # Находим материал или добавляем его в справочник.
        material, _ = Material.objects.get_or_create(
            name=data["material_name"],
        )

        # Создаём объявление.
        listing = Listing.objects.create(
            material=material,
            created_by=telegram_user,
            title=data["title"],
            description=data.get("description", ""),
            quantity=Decimal(data["quantity"]),
            unit=data["unit"],
            price=Decimal(data["price"]),
            status=Listing.Status.ACTIVE,
            city=data["city"],
            address=data.get("address", ""),
            contact_name=telegram_user.first_name,
        )

        return listing.id


async def create_listing(
    data: dict,
    telegram_user_data: dict,
) -> int:
    """Асинхронная обёртка для создания объявления."""

    return await sync_to_async(
        _create_listing,
        thread_sensitive=True,
    )(data, telegram_user_data)

