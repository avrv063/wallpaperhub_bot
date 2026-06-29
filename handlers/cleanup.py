from aiogram import Router, types, F

from config import ADMIN_ID
from services.cleanup import cleanup_candidates_files

router = Router()


@router.callback_query(F.data == "cleanup_candidates")
async def cleanup_candidates(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Нет доступа.", show_alert=True)
        return

    await callback.answer()

    result = await cleanup_candidates_files()

    text = (
        "🧹 Очистка завершена\n\n"
        f"Файлов удалено: {result['deleted_files']}\n"
        f"Записей удалено: {result['deleted_rows']}"
    )

    if result["errors"]:
        text += "\n\nОшибки:\n"
        text += "\n".join(result["errors"][:5])

    await callback.message.answer(text)