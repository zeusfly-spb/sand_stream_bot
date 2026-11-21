from decimal import Decimal
from pathlib import Path
from uuid import uuid4

from asgiref.sync import sync_to_async
from django.conf import settings as django_settings
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from accounts.models import TelegramUser
from catalog.models import City, Listing, ListingPhoto, MaterialType

UNIT_LABELS = {"m3": "м³", "ton": "тонн"}


def _slug_for(name: str) -> str:
    base = slugify(name, allow_unicode=True) or "material"
    slug = base
    index = 2
    while MaterialType.objects.exclude(name=name).filter(slug=slug).exists():
        slug = f"{base}-{index}"
        index += 1
    return slug


def _create_listing(data: dict, telegram_user_data: dict, photo_paths: list) -> str:
    """Создаёт объявление, пользователя и фотографии. Возвращает UUID строкой."""
    with transaction.atomic():
        telegram_user, _ = TelegramUser.objects.update_or_create(
            telegram_id=telegram_user_data["telegram_id"],
            defaults={
                "username": telegram_user_data.get("username") or "",
                "first_name": telegram_user_data.get("first_name") or "",
                "last_name": telegram_user_data.get("last_name") or "",
            },
        )

        unit_label = UNIT_LABELS.get(data["unit"], "м³")

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
            quantity=f"{data['quantity']} {unit_label}",
            price=Decimal(data["price"]),
            price_unit=f"за {unit_label}",
            status=Listing.Status.ACTIVE,
            contact_name=telegram_user.first_name or "",
            contact_phone=getattr(telegram_user, "phone", "") or "",
            published_at=timezone.now(),
        )

        media_root = django_settings.MEDIA_ROOT
        for position, path in enumerate(photo_paths):
            photo = ListingPhoto(listing=listing, position=position)
            photo.image.name = Path(path).relative_to(media_root).as_posix()
            photo.save()

        return str(listing.id)


async def create_listing(data: dict, telegram_user_data: dict, bot) -> str:
    """Скачивает фото из Telegram и создаёт объявление."""
    photo_paths = []

    for file_id in data.get("photos", []):
        name = f"{uuid4().hex}.jpg"
        directory = django_settings.MEDIA_ROOT / "listings"
        directory.mkdir(parents=True, exist_ok=True)
        destination = directory / name
        await bot.download(file_id, destination=destination)
        photo_paths.append(destination)

    return await sync_to_async(_create_listing, thread_sensitive=True)(
        data, telegram_user_data, photo_paths
    )
