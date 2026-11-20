import asyncio
import logging

from aiogram import Dispatcher
from app.bot import create_bot
from app.config import settings
from app.handlers.start import router as start_router


async def main() -> None:
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    bot = create_bot()
    dp = Dispatcher()
    dp.include_router(start_router)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
