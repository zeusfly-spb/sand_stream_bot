"""Тестовые объявления для разработки и демонстрации.

Запуск: python manage.py seed_listings [--flush]
Идемпотентный: повторный запуск не создаёт дубликатов.
"""
import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import TelegramUser
from catalog.models import City, Listing, MaterialType

# (название, базовая цена за м3)
MATERIALS = [
    ("Песок карьерный", 550),
    ("Песок речной", 750),
    ("Песок мытый сеяный", 900),
    ("Щебень гранитный", 2200),
    ("Щебень гравийный", 1600),
    ("Щебень известняковый", 1400),
    ("Гравий", 1350),
    ("ПГС", 650),
    ("ОПГС", 800),
    ("Гранитный отсев", 950),
    ("Керамзит", 3000),
    ("Песчаный грунт", 350),
    ("Плодородный грунт", 850),
    ("Чернозём", 1100),
    ("Торф", 780),
    ("Бой кирпича", 450),
    ("Асфальтовая крошка", 520),
]

# (название, регион)
CITIES = [
    ("Санкт-Петербург", "Санкт-Петербург"),
    ("Колпино", "Санкт-Петербург"),
    ("Пушкин", "Санкт-Петербург"),
    ("Гатчина", "Ленинградская область"),
    ("Всеволожск", "Ленинградская область"),
    ("Тосно", "Ленинградская область"),
    ("Кировск", "Ленинградская область"),
    ("Выборг", "Ленинградская область"),
    ("Луга", "Ленинградская область"),
    ("Сосновый Бор", "Ленинградская область"),
    ("Кингисепп", "Ленинградская область"),
    ("Тихвин", "Ленинградская область"),
]

# (telegram_id, username, название компании)
SELLERS = [
    (100000001, "sand_demo_1", "ООО «Гатчинский карьер»"),
    (100000002, "sand_demo_2", "ИП Петров С.В."),
    (100000003, "sand_demo_3", "«Северный путь»"),
]

# (материал, город, поправка к цене, объём) — расписание объявлений
SCHEDULE = [
    ("Песок карьерный", "Санкт-Петербург", 0, "от 20 м3"),
    ("Песок карьерный", "Гатчина", -30, "от 30 м3"),
    ("Песок речной", "Колпино", 0, "от 10 м3"),
    ("Песок мытый сеяный", "Санкт-Петербург", 0, "от 5 м3"),
    ("Щебень гранитный", "Гатчина", 0, "от 10 м3"),
    ("Щебень гранитный", "Выборг", -100, "от 20 м3"),
    ("Щебень гравийный", "Всеволожск", 0, "от 15 м3"),
    ("Щебень известняковый", "Кингисепп", 0, "от 10 м3"),
    ("Гравий", "Тосно", 0, "от 5 м3"),
    ("ПГС", "Кировск", 0, "от 30 м3"),
    ("ОПГС", "Тосно", -20, "от 15 м3"),
    ("Гранитный отсев", "Выборг", 0, "от 10 м3"),
    ("Керамзит", "Пушкин", 0, "от 3 м3"),
    ("Песчаный грунт", "Всеволожск", 0, "от 50 м3"),
    ("Плодородный грунт", "Луга", 0, "от 10 м3"),
    ("Чернозём", "Сосновый Бор", 0, "любые объёмы"),
    ("Торф", "Луга", 0, "договорная"),
    ("Бой кирпича", "Тихвин", 0, "от 10 т"),
    ("Асфальтовая крошка", "Сосновый Бор", -20, "от 20 т"),
]

QTY_NOTE = {
    "Бой кирпича": "за тонну",
    "Асфальтовая крошка": "за тонну",
    "Песок мытый сеяный": "за тонну",
}


class Command(BaseCommand):
    help = "Наполняет базу тестовыми объявлениями и поставщиками"

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush", action="store_true",
            help="Удалить ранее созданные сидером объявления и продавцов",
        )

    def handle(self, *args, **options):
        if options["flush"]:
            removed, _ = Listing.objects.filter(seller__telegram_id__lt=100001000).delete()
            TelegramUser.objects.filter(telegram_id__lt=100001000).delete()
            self.stdout.write(self.style.WARNING(f"Удалено тестовых записей: {removed}"))

        materials = {}
        for name, base_price in MATERIALS:
            obj, _ = MaterialType.objects.get_or_create(
                name=name, defaults={"slug": name.lower().replace(" ", "-")}
            )
            materials[name] = (obj, base_price)

        cities = {}
        for name, region in CITIES:
            cities[name] = City.objects.get_or_create(name=name, region=region)[0]

        sellers = []
        for tg_id, username, company in SELLERS:
            sellers.append(TelegramUser.objects.get_or_create(
                telegram_id=tg_id,
                defaults={
                    "username": username,
                    "first_name": company,
                    "role": "owner",
                },
            )[0])

        created = 0
        now = timezone.now()
        for i, (mat_name, city_name, delta, qty) in enumerate(SCHEDULE):
            material, base_price = materials[mat_name]
            city = cities[city_name]
            seller = sellers[i % len(sellers)]
            unit = QTY_NOTE.get(mat_name, "за м3")
            title = f"{mat_name}: {city_name}, {qty}"
            listing, was_created = Listing.objects.get_or_create(
                title=title,
                defaults={
                    "seller": seller,
                    "material_type": material,
                    "city": city,
                    "material_raw": mat_name,
                    "city_raw": city_name,
                    "description": (
                        f"{mat_name} с доставкой из {city_name}. Самовывоз и доставка "
                        f"самосвалами, работаем ежедневно. Звоните — подберём объём."
                    ),
                    "price": base_price + delta,
                    "price_unit": unit,
                    "quantity": qty,
                    "status": Listing.Status.ACTIVE,
                    "contact_name": seller.first_name,
                    "contact_phone": f"+7 (900) 000-01-{i:02d}",
                    "published_at": now - datetime.timedelta(days=i),
                },
            )
            created += int(was_created)

        self.stdout.write(self.style.SUCCESS(
            f"Готово. Объявлений создано: {created}, всего в базе: {Listing.objects.count()}."
        ))
