
from django.contrib import admin

from .models import TelegramUser


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = (
        "telegram_id",
        "username",
        "first_name",
        "last_name",
        "role",
        "is_blocked",
        "created_at",
    )

    list_filter = ("role", "is_blocked")
    search_fields = (
        "telegram_id",
        "username",
        "first_name",
        "last_name",
        "phone",
    )

    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)
