"""Наполнение справочников: типы материалов и города СПб и Ленобласти.

Запуск: python manage.py seed_catalog
Идемпотентный: повторный запуск не создаёт дубликатов.
"""

from django.core.management.base import BaseCommand

from catalog.models import City, MaterialType

MATERIALS = [
    "Песок карьерный",
    "Песок речной",
    "Песок намывной",
    "Песок мытый сеяный",
    "Щебень гранитный",
    "Щебень гравийный",
    "Щебень известняковый",
    "Гравий",
    "ПГС",
    "ОПГС",
    "Гранитный отсев",
    "Керамзит",
    "Песчаный грунт",
    "Плодородный грунт",
    "Чернозём",
    "Торф",
    "Бой кирпича",
    "Асфальтовая крошка",
]

# (название, регион)
CITIES = [
    ("Санкт-Петербург", "Санкт-Петербург"),
    ("Гатчина", "Ленинградская область"),
    ("Всеволожск", "Ленинградская область"),
    ("Кировск", "Ленинградская область"),
    ("Тосно", "Ленинградская область"),
    ("Пушкин", "Санкт-Петербург"),
    ("Колпино", "Санкт-Петербург"),
    ("Сертолово", "Ленинградская область"),
    ("Волосово", "Ленинградская область"),
    ("Луга", "Ленинградская область"),
    ("Выборг", "Ленинградская область"),
    ("Приозерск", "Ленинградская область"),
    ("Тихвин", "Ленинградская область"),
    ("Кингисепп", "Ленинградская область"),
    ("Бокситогорск", "Ленинградская область"),
    ("Никольское", "Ленинградская область"),
    ("Отрадное", "Ленинградская область"),
    ("Коммунар", "Ленинградская область"),
    ("Мурино", "Ленинградская область"),
    ("Кудрово", "Ленинградская область"),
    ("Сланцы", "Ленинградская область"),
    ("Сосновый Бор", "Ленинградская область"),
]


class Command(BaseCommand):
    help = "Наполняет справочники материалов и городов СПб и Ленобласти"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Перед наполнением очистить справочники (осторожно!)",
        )

    def handle(self, *args, **options):
        if options["reset"]:
            deleted = City.objects.count() + MaterialType.objects.count()
            City.objects.all().delete()
            MaterialType.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Удалено записей: {deleted}"))

        materials_created = 0
        for name in MATERIALS:
            _, created = MaterialType.objects.get_or_create(
                name=name,
                defaults={"slug": self._slugify(name)},
            )
            if created:
                materials_created += 1

        cities_created = 0
        for name, region in CITIES:
            _, created = City.objects.get_or_create(
                name=name, region=region
            )
            if created:
                cities_created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Готово. Материалов создано: {materials_created} "
                f"(всего {MaterialType.objects.count()}), "
                f"городов создано: {cities_created} "
                f"(всего {City.objects.count()})."
            )
        )

    @staticmethod
    def _slugify(name: str) -> str:
        # Простая замена для наших названий: не тянем весь slugify ради пары строк
        return name.lower().replace(" ", "-")
