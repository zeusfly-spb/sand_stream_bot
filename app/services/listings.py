
from asgiref.sync import sync_to_async
from catalog.models import Listing


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
