
from decimal import Decimal

from asgiref.sync import sync_to_async
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from accounts.models import TelegramUser
from catalog.models import City, Listing, MaterialType

UNIT_LABELS = {
    "m3": "м³",
    "ton": "т",
    "kg": "кг",
    "bag": "меш.",
    "pcs": "шт.",
}

def _slug_for(name: str) -> str:
    base = slugify(name, allow_unicode=True) or "material"
    slug = base
    index = 2

    while MaterialType.objects.exclude(name=name).filter(slug=slug).exists():
        slug = f"{base}-{index}"
        index += 1

    return slug


def _create_listing(data: dict, telegram_user_data: dict) -> str:
    """Создаёт пользователя и объявление. Возвращает UUID строкой."""
    with transaction.atomic():
        telegram_user, _ = TelegramUser.objects.update_or_create(
            telegram_id=telegram_user_data["telegram_id"],
            defaults={
                "username": telegram_user_data.get("username") or "",
                "first_name": telegram_user_data.get("first_name") or "",
                "last_name": telegram_user_data.get("last_name") or "",
            },
        )

        unit_label = UNIT_LABELS[data["unit"]]

        material, _ = MaterialType.objects.get_or_create(
            name=data["material_name"],
            defaults={"slug": _slug_for(data["material_name"])},
        )

        city = City.objects.filter(name__iexact=data["city"]).first()

        listing = Listing.objects.create(
            seller=telegram_user,
            material_type=material,
            material_raw=data["material_name"],
            city=city,
            city_raw="" if city else data["city"],
            title=data["title"],
            description=data.get("description", ""),
            address=data.get("address", ""),
            quantity=data["quantity"],
            price=Decimal(data["price"]),
            price_unit=f"за {unit_label}",
            quantity_unit=unit_label,
            status=Listing.Status.ACTIVE,
            contact_name=telegram_user.first_name or "",
            contact_phone=telegram_user.phone or "",
            published_at=timezone.now(),
        )

        return str(listing.id)


async def create_listing(data: dict, telegram_user_data: dict) -> str:
    """Создаёт объявление через Django ORM."""
    return await sync_to_async(_create_listing, thread_sensitive=True)(
        data, telegram_user_data
    )
