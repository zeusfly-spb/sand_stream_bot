
import os
import sys
from pathlib import Path


def setup_django() -> None:
    """Подключает Django к Telegram-боту."""

    # Корень проекта SandStreamBot
    project_root = Path(__file__).resolve().parent.parent

    # Папка Django-проекта
    django_dir = project_root / "web"

    # Добавляем Django-проект в Python PATH
    django_path = str(django_dir)

    if django_path not in sys.path:
        sys.path.insert(0, django_path)

    # Указываем настройки Django
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        "config.settings",
    )

    # Инициализируем Django
    import django

    django.setup()
