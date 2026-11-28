import uuid

from django.db import models


class MaterialType(models.Model):
    """Справочник типов сыпучих материалов: песок, щебень, гравий..."""

    name = models.CharField("название", max_length=100, unique=True)
    slug = models.SlugField("слаг", max_length=100, unique=True)
    is_active = models.BooleanField("активен", default=True)

    class Meta:
        verbose_name = "материал"
        verbose_name_plural = "Материалы"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class City(models.Model):
    """Справочник населённых пунктов СПб и Ленинградской области."""

    name = models.CharField("название", max_length=150)
    region = models.CharField("регион", max_length=150, default="Ленинградская область")
    latitude = models.DecimalField(
        "широта", max_digits=9, decimal_places=6, null=True, blank=True
    )
    longitude = models.DecimalField(
        "долгота", max_digits=9, decimal_places=6, null=True, blank=True
    )
    is_active = models.BooleanField("активен", default=True)

    class Meta:
        verbose_name = "населённый пункт"
        verbose_name_plural = "Города и районы"
        ordering = ("name",)
        unique_together = ("name", "region")

    def __str__(self) -> str:
        return f"{self.name} ({self.region})"


class Listing(models.Model):
    """Объявление о продаже сыпучих материалов."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Черновик"
        ACTIVE = "active", "Активно"
        SOLD = "sold", "Продано"
        ARCHIVED = "archived", "В архиве"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    seller = models.ForeignKey(
        "accounts.TelegramUser",
        on_delete=models.CASCADE,
        related_name="listings",
        verbose_name="поставщик",
    )

    # Новые связанные поля (заполняем постепенно, старые записи живут на *_raw)
    material_type = models.ForeignKey(
        MaterialType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="listings",
        verbose_name="тип материала",
    )
    city = models.ForeignKey(
        City,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="listings",
        verbose_name="населённый пункт",
    )

    # Прежние текстовые поля — сохраняем для совместимости
    material_raw = models.CharField("материал (текст)", max_length=200, blank=True)
    city_raw = models.CharField("город (текст)", max_length=200, blank=True)

    title = models.CharField("заголовок", max_length=200)
    description = models.TextField("описание", blank=True)

    price = models.DecimalField(
        "цена", max_digits=12, decimal_places=2, null=True, blank=True
    )
    price_unit = models.CharField(
        "единица цены", max_length=20, blank=True, default=""
    )  # "за м3", "за тонну"
    quantity = models.CharField("объём/количество", max_length=100, blank=True)
    quantity_unit = models.CharField(
        "единица измерения",
        max_length=20,
        blank=True,
        default="",
    )

    status = models.CharField(
        "статус", max_length=20, choices=Status.choices, default=Status.DRAFT
    )

    contact_name = models.CharField("имя контактного лица", max_length=100, blank=True)
    address = models.CharField("адрес", max_length=255, blank=True)
    latitude = models.DecimalField(
        "широта",
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )

    longitude = models.DecimalField(
        "долгота",
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )

    contact_phone = models.CharField("телефон", max_length=32, blank=True)

    created_at = models.DateTimeField("создано", auto_now_add=True)
    updated_at = models.DateTimeField("обновлено", auto_now=True)
    published_at = models.DateTimeField("опубликовано", null=True, blank=True)

    class Meta:
        verbose_name = "объявление"
        verbose_name_plural = "Объявления"
        ordering = ("-created_at",)
        indexes = [
            models.Index(
                fields=["status", "material_type", "city", "-published_at"],
                name="listing_catalog_newest_idx",
            ),
            models.Index(
                fields=["status", "material_type", "city", "price"],
                name="listing_catalog_price_idx",
            ),
            models.Index(
                fields=["status", "latitude", "longitude"],
                name="listing_geo_idx",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.title} — {self.city_raw or 'без города'}"


class ListingPhoto(models.Model):
    """Фотографии объявления (порядок задаётся полем position)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name="photos",
        verbose_name="объявление",
    )
    image = models.ImageField("фото", upload_to="listings/%y/%m/")
    position = models.PositiveSmallIntegerField("позиция", default=0)
    created_at = models.DateTimeField("добавлено", auto_now_add=True)

    class Meta:
        verbose_name = "фотография"
        verbose_name_plural = "Фотографии"
        ordering = ("position",)

    def __str__(self) -> str:
        return f"Фото #{self.position} для {self.listing_id}"


class Subscription(models.Model):
    """Подписка пользователя: следить за материалом X в городе Y."""

    subscriber = models.ForeignKey(
        "accounts.TelegramUser",
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="подписчик",
    )
    material_type = models.ForeignKey(
        MaterialType,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="тип материала",
    )
    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="город",
    )
    is_active = models.BooleanField("активна", default=True)
    created_at = models.DateTimeField("создана", auto_now_add=True)

    class Meta:
        verbose_name = "подписка"
        verbose_name_plural = "Подписки"
        ordering = ("-created_at",)
        unique_together = ("subscriber", "material_type", "city")

    def __str__(self) -> str:
        return f"{self.subscriber_id}: {self.material_type} в {self.city}"


class Notification(models.Model):
    """Журнал уведомлений: что, кому и когда отправили."""

    class Kind(models.TextChoices):
        NEW_LISTING = "new_listing", "Новое объявление"
        STATUS_CHANGE = "status_change", "Изменение статуса"
        REMINDER = "reminder", "Напоминание"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        "accounts.TelegramUser",
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name="получатель",
    )
    listing = models.ForeignKey(
        Listing,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications",
        verbose_name="объявление",
    )
    kind = models.CharField("тип", max_length=30, choices=Kind.choices)
    text = models.TextField("текст", blank=True)
    sent_at = models.DateTimeField("отправлено", null=True, blank=True)
    is_sent = models.BooleanField("отправлено", default=False)
    created_at = models.DateTimeField("создано", auto_now_add=True)

    class Meta:
        verbose_name = "уведомление"
        verbose_name_plural = "Уведомления"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.kind} → {self.user_id}"
