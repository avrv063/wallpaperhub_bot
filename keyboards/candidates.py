from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def candidate_keyboard(candidate_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="➕ В подборку",
                callback_data=f"candidate_add:{candidate_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="⭐ Избранное",
                callback_data=f"candidate_fav:{candidate_id}"
            ),
            InlineKeyboardButton(
                text="❌ Пропустить",
                callback_data=f"candidate_skip:{candidate_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="➡️ Следующая",
                callback_data="candidate_next"
            )
        ],
    ])