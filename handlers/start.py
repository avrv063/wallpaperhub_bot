from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command

from config import ADMIN_ID
from keyboards.main_menu import main_menu

router = Router()


@router.message(CommandStart())
async def start(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Нет доступа.")
        return

    await message.answer(
        "Wallpaper Hub Studio запущен.\n\nВыбери действие:",
        reply_markup=main_menu()
    )

@router.message(Command("menu"))
async def menu(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Нет доступа.")
        return

    await message.answer(
        "Главное меню:",
        reply_markup=main_menu()
    )

from aiogram import F
@router.callback_query(F.data.in_({"test_publish"}))
async def menu_callbacks(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Нет доступа.", show_alert=True)
        return

    if callback.data == "candidates":
        await callback.message.answer("Раздел кандидатов пока в разработке.")

    elif callback.data == "collections":
        await callback.message.answer("Раздел подборок пока в разработке.")

    elif callback.data == "test_publish":
        await callback.message.answer("Тест публикации подключим следующим шагом.")

    await callback.answer()