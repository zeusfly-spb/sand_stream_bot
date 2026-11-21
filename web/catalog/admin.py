from django.contrib import admin

from .models import City, Listing, ListingPhoto, MaterialType


@admin.register(MaterialType)
class MaterialTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("name", "region", "is_active")
    list_filter = ("region", "is_active")
    search_fields = ("name",)


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "seller",
        "material_type",
        "city",
        "price",
        "price_unit",
        "status",
        "created_at",
    )
    list_filter = ("status", "material_type", "city")
    search_fields = ("title", "description", "material_raw", "city_raw")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)

    # Чтобы autocomplete_fields заработал, у MaterialTypeAdmin и CityAdmin
    # должен быть search_fields — он уже задан выше.
    autocomplete_fields = ("material_type", "city", "seller")


@admin.register(ListingPhoto)
class ListingPhotoAdmin(admin.ModelAdmin):
    list_display = ("listing", "position", "created_at")
    list_filter = ("listing",)
    ordering = ("listing", "position")
