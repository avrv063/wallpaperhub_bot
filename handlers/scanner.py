from aiogram import Router, types, F

from config import ADMIN_ID
from services.telegram_scanner import scan_telegram_sources

router = Router()


@router.callback_query(F.data == "scan_sources")
async def scan_sources(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Нет доступа.", show_alert=True)
        return

    await callback.answer()

    status_message = await callback.message.answer("🔍 Начинаю проверку источников...")

    async def progress(text: str):
        await status_message.edit_text(f"🔍 {text}")

    result = await scan_telegram_sources(progress_callback=progress)

    text = (
        "✅ Проверка завершена\n\n"
        f"Источников всего: {result['sources_total']}\n"
        f"Проверено: {result['sources_checked']}\n"
        f"Изображений найдено: {result['images_found']}\n"
        f"Новых сохранено: {result['images_saved']}"
    )

    if result["errors"]:
        text += "\n\n⚠️ Ошибки:\n"
        text += "\n".join(result["errors"][:5])

    await status_message.edit_text(text)