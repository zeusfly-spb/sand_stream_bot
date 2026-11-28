from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html

from .models import (
    City,
    Listing,
    ListingPhoto,
    MaterialType,
    Notification,
    Subscription,
)


class ListingPhotoInline(admin.TabularInline):
    model = ListingPhoto
    extra = 0
    fields = ("position", "image", "preview")
    readonly_fields = ("preview",)
    ordering = ("position",)

    @admin.display(description="Превью")
    def preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height:120px; border-radius:4px;">',
                obj.image.url,
            )
        return "—"


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "material_display",
        "city_display",
        "price_display",
        "quantity",
        "status",
        "published_at",
    )
    list_filter = ("status", "city", "material_type", "created_at")
    search_fields = ("title", "description", "material_raw", "city_raw", "contact_phone")
    list_editable = ("status",)
    date_hierarchy = "created_at"
    inlines = [ListingPhotoInline]
    readonly_fields = ("created_at", "updated_at")
    list_per_page = 25

    fieldsets = (
        ("Объявление", {
            "fields": ("title", "description", "status"),
        }),
        ("Справочники", {
            "fields": ("material_type", "material_raw", "city", "city_raw"),
        }),
        ("Условия", {
            "fields": (
                "quantity",
                "quantity_unit",
                "price",
                "price_unit",
                "address",
                "latitude",
                "longitude",
            ),
        }),
        ("Продавец", {
            "fields": ("seller", "contact_name", "contact_phone"),
        }),
        ("Служебное", {
            "fields": ("published_at", "created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    @admin.display(description="Материал")
    def material_display(self, obj):
        return obj.material_type.name if obj.material_type else obj.material_raw or "—"

    @admin.display(description="Город")
    def city_display(self, obj):
        return obj.city.name if obj.city else obj.city_raw or "—"

    @admin.display(description="Цена")
    def price_display(self, obj):
        if obj.price is None:
            return "—"
        if obj.price == 0:
            return "Бесплатно"
        return f"{obj.price} руб. {obj.price_unit}".strip()


@admin.register(MaterialType)
class MaterialTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "listings_count")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .annotate(_listings=Count("listings"))
        )

    @admin.display(description="Объявлений")
    def listings_count(self, obj):
        return obj._listings


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("name", "region", "listings_count")
    search_fields = ("name",)
    list_filter = ("region",)

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .annotate(_listings=Count("listings"))
        )

    @admin.display(description="Объявлений")
    def listings_count(self, obj):
        return obj._listings


admin.site.unregister(ListingPhoto) if ListingPhoto in admin.site._registry else None
admin.site.register(ListingPhoto)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("subscriber", "material_type", "city", "is_active", "created_at")
    list_filter = ("is_active", "material_type", "city")
    search_fields = ("subscriber__username", "subscriber__telegram_id")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("kind", "user", "listing", "is_sent", "sent_at", "created_at")
    list_filter = ("kind", "is_sent")
    search_fields = ("text", "user__username", "user__telegram_id")
    readonly_fields = ("created_at",)
