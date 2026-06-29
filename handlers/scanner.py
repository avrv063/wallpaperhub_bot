from aiogram import Router, types, F

from config import ADMIN_ID
from services.source_scanner import scan_all_sources

from services.scan_control import request_scan_cancel, reset_scan_cancel

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

    reset_scan_cancel()    

    result = await scan_all_sources(progress_callback=progress)

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

@router.callback_query(F.data == "cancel_scan")
async def cancel_scan(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Нет доступа.", show_alert=True)
        return

    request_scan_cancel()
    await callback.answer("Остановка поиска запрошена")
    await callback.message.answer("🛑 Останавливаю поиск...")