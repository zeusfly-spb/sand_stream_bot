import asyncio
import logging

from aiogram import Dispatcher

from app.bot import create_bot
from app.config import settings
from app.django_setup import setup_django


async def main() -> None:
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    # Инициализируем Django до загрузки обработчиков
    setup_django()
    from app.handlers.listings import router as listings_router

    # Импортируем обработчики после инициализации Django
    from app.handlers.start import router as start_router

    bot = create_bot()
    dp = Dispatcher()
    dp.include_router(start_router)
    dp.include_router(listings_router)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
