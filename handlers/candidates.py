import os

from aiogram import Router, types, F
from aiogram.types import FSInputFile

from config import ADMIN_ID
from repositories.candidates import (
    get_next_candidate,
    update_candidate_status,
    count_new_candidates,
)
from keyboards.candidates import candidate_keyboard

router = Router()


async def send_next_candidate(message: types.Message):
    candidate = await get_next_candidate()
    count = await count_new_candidates()

    if not candidate:
        await message.answer("Новых кандидатов нет. Нажми 🔍 Найти контент.")
        return

    candidate_id, file_path, source_id, message_id = candidate

    if not os.path.exists(file_path):
        await update_candidate_status(candidate_id, "missing")
        await message.answer("Файл не найден, пропускаю...")
        await send_next_candidate(message)
        return

    photo = FSInputFile(file_path)

    caption = (
        f"🖼 Кандидат #{candidate_id}\n\n"
        f"Осталось новых: {count}\n"
        f"Источник ID: {source_id}\n"
        f"Message ID: {message_id}"
    )

    await message.answer_photo(
        photo=photo,
        caption=caption,
        reply_markup=candidate_keyboard(candidate_id)
    )


@router.callback_query(F.data == "candidates")
async def candidates_start(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Нет доступа.", show_alert=True)
        return

    await callback.answer()
    await send_next_candidate(callback.message)


@router.callback_query(F.data == "candidate_next")
async def candidate_next(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Нет доступа.", show_alert=True)
        return

    await callback.answer()
    await send_next_candidate(callback.message)


@router.callback_query(F.data.startswith("candidate_skip:"))
async def candidate_skip(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Нет доступа.", show_alert=True)
        return

    candidate_id = int(callback.data.split(":")[1])
    await update_candidate_status(candidate_id, "skipped")

    await callback.answer("Пропущено")
    await send_next_candidate(callback.message)


@router.callback_query(F.data.startswith("candidate_fav:"))
async def candidate_fav(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Нет доступа.", show_alert=True)
        return

    candidate_id = int(callback.data.split(":")[1])
    await update_candidate_status(candidate_id, "favorite")

    await callback.answer("Добавлено в избранное")
    await send_next_candidate(callback.message)