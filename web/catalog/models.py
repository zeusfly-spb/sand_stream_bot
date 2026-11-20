from django.db import models


from django.db import models
from django.core.validators import MinValueValidator


class Material(models.Model):
    """Справочник сыпучих строительных материалов."""

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Название",
    )

    description = models.TextField(
        blank=True,
        verbose_name="Описание",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Активен",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
    )

    class Meta:
        verbose_name = "Материал"
        verbose_name_plural = "Материалы"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Listing(models.Model):
    """Объявление о продаже или бесплатной передаче материала."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Черновик"
        ACTIVE = "active", "Активно"
        RESERVED = "reserved", "Забронировано"
        SOLD = "sold", "Продано"
        ARCHIVED = "archived", "Архив"

    class Unit(models.TextChoices):
        M3 = "m3", "м³"
        TON = "ton", "тонн"

    material = models.ForeignKey(
        Material,
        on_delete=models.PROTECT,
        related_name="listings",
        verbose_name="Материал",
    )

    created_by = models.ForeignKey(
        "accounts.TelegramUser",
        on_delete=models.PROTECT,
        related_name="listings",
        null=True,
        blank=True,
        verbose_name="Автор объявления",
    )

    title = models.CharField(
        max_length=200,
        verbose_name="Заголовок",
    )

    description = models.TextField(
        blank=True,
        verbose_name="Описание",
    )

    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        validators=[MinValueValidator(0.001)],
        verbose_name="Количество",
    )

    unit = models.CharField(
        max_length=10,
        choices=Unit.choices,
        default=Unit.M3,
        verbose_name="Единица измерения",
    )

    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Цена (руб.)",
        help_text="Ноль означает бесплатное предложение.",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
        verbose_name="Статус",
    )

    city = models.CharField(
        max_length=100,
        default="Санкт-Петербург",
        verbose_name="Город",
    )

    address = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Адрес",
    )

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name="Широта",
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name="Долгота",
    )

    contact_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Контактное лицо",
    )

    contact_phone = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Телефон",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления",
    )

    class Meta:
        verbose_name = "Объявление"
        verbose_name_plural = "Объявления"
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["status", "created_at"],
                name="listing_status_created_idx",
            ),
        ]

    def __str__(self):
        return self.title

    
class ListingPhoto(models.Model):
    """Фотографии объявления."""

    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name="photos",
        verbose_name="Объявление",
    )

    image = models.ImageField(
        upload_to="listings/%Y/%m/",
        verbose_name="Фотография",
    )

    caption = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Подпись",
    )

    position = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Порядок отображения",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата загрузки",
    )

    class Meta:
        verbose_name = "Фотография"
        verbose_name_plural = "Фотографии"
        ordering = ["position", "id"]

    def __str__(self):
        return f"Фото: {self.listing.title}"


