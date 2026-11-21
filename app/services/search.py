from asgiref.sync import sync_to_async

from catalog.models import City, Listing, MaterialType


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
