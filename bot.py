import asyncio
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔥 Новые кандидаты", callback_data="candidates")],
        [InlineKeyboardButton(text="📦 Мои подборки", callback_data="collections")],
        [InlineKeyboardButton(text="➕ Добавить источник", callback_data="add_source")],
        [InlineKeyboardButton(text="🚀 Тест публикации", callback_data="test_publish")],
    ])


@dp.message(CommandStart())
async def start(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Нет доступа.")
        return

    await message.answer(
        "Wallpaper Hub Bot запущен.\n\nВыбери действие:",
        reply_markup=main_menu()
    )


@dp.callback_query()
async def callbacks(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Нет доступа.", show_alert=True)
        return

    if callback.data == "candidates":
        await callback.message.answer("Раздел кандидатов пока в разработке.")

    elif callback.data == "collections":
        await callback.message.answer("Раздел подборок пока в разработке.")

    elif callback.data == "add_source":
        await callback.message.answer("Скоро сюда можно будет отправлять ссылки на ТГК.")

    elif callback.data == "test_publish":
        await callback.message.answer("Тест публикации пока не подключён.")

    await callback.answer()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())