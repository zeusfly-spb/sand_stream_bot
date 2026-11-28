from app.config import settings


def is_admin(user_id: int | None) -> bool:
    """Проверяет, входит ли Telegram ID в список администраторов."""
    return user_id is not None and user_id in settings.admin_id_set
