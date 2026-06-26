import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from config import BOT_TOKEN
from database import init_db

from handlers.sources import router as sources_router
from handlers.scanner import router as scanner_router
from handlers.collections import router as collections_router
from handlers.candidates import router as candidates_router
from handlers.start import router as start_router


async def set_commands(bot: Bot):
    await bot.set_my_commands([
        BotCommand(command="start", description="Главное меню"),
        BotCommand(command="menu", description="Открыть меню"),
    ])


async def main():
    await init_db()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(sources_router)
    dp.include_router(scanner_router)
    dp.include_router(collections_router)
    dp.include_router(candidates_router)
    dp.include_router(start_router)

    await set_commands(bot)

    print("Wallpaper Hub Studio started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())