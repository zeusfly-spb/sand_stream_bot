from django.db import models


class TelegramUser(models.Model):
    """Пользователь Telegram."""

    class Role(models.TextChoices):
        USER = "user", "Пользователь"
        MANAGER = "manager", "Менеджер"
        OWNER = "owner", "Владелец"

    telegram_id = models.BigIntegerField(
        unique=True,
        verbose_name="Telegram ID",
    )

    username = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Username",
    )

    first_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Имя",
    )

    last_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Фамилия",
    )

    phone = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Телефон",
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.USER,
        db_index=True,
        verbose_name="Роль",
    )

    is_blocked = models.BooleanField(
        default=False,
        verbose_name="Заблокирован",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата регистрации",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Последнее обновление",
    )

    class Meta:
        verbose_name = "Пользователь Telegram"
        verbose_name_plural = "Пользователи Telegram"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.first_name} ({self.telegram_id})"
