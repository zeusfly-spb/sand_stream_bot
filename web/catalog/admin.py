from django.contrib import admin
from django.utils.html import format_html

from .models import Material, Listing, ListingPhoto


class ListingPhotoInline(admin.TabularInline):
    model = ListingPhoto
    extra = 1
    fields = ("image", "caption", "position", "preview")
    readonly_fields = ("preview",)

    @admin.display(description="Предпросмотр")
    def preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="100" style="object-fit: contain;" />',
                obj.image.url,
            )
        return "Нет изображения"


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "material",
        "quantity",
        "unit",
        "price",
        "status",
        "city",
        "created_at",
    )
    list_filter = ("status", "material", "unit", "city")
    search_fields = ("title", "description", "address", "contact_name")
    autocomplete_fields = ("material",)
    inlines = (ListingPhotoInline,)
    readonly_fields = ("created_at", "updated_at")
    list_select_related = ("material",)


admin.site.site_header = "SandStreamBot — управление"
admin.site.site_title = "SandStreamBot"
admin.site.index_title = "Панель управления"
