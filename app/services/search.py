from asgiref.sync import sync_to_async

from catalog.models import City, Listing, MaterialType
from uuid import UUID



@sync_to_async
def find_material(name: str) -> MaterialType | None:
    return MaterialType.objects.filter(is_active=True, name=name).first()


@sync_to_async
def find_city(name: str) -> City | None:
    return City.objects.filter(is_active=True, name=name).first()


@sync_to_async
def search_listings(material_id: int | None, city_id: int | None) -> list:
    qs = Listing.objects.filter(status=Listing.Status.ACTIVE)

    if material_id is not None:
        qs = qs.filter(material_type_id=material_id)
    if city_id is not None:
        qs = qs.filter(city_id=city_id)

    return list(
        qs.select_related("material_type", "city", "seller")
        .order_by("-published_at", "-created_at")[:10]
    )


@sync_to_async
def get_listings_page(
    material_id: int | None,
    city_id: int | None,
    page: int = 0,
    page_size: int = 5,
) -> tuple[list, bool]:
    """Возвращает страницу объявлений и признак следующей страницы."""

    page = max(page, 0)
    page_size = max(1, min(page_size, 10))

    qs = Listing.objects.filter(status=Listing.Status.ACTIVE)

    if material_id is not None:
        qs = qs.filter(material_type_id=material_id)

    if city_id is not None:
        qs = qs.filter(city_id=city_id)

    start = page * page_size

    listings = list(
        qs.select_related("material_type", "city", "seller")
        .order_by("-published_at", "-created_at", "-id")[
            start : start + page_size + 1
        ]
    )

    has_next = len(listings) > page_size

    return listings[:page_size], has_next

@sync_to_async
def get_listing_by_id(listing_id: UUID):
    """Получает активное объявление по UUID."""

    return (
        Listing.objects
        .filter(
            id=listing_id,
            status=Listing.Status.ACTIVE,
        )
        .select_related("material_type", "city", "seller")
        .first()
    )
