from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def source_card_keyboard(source_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⏸ Вкл/выкл",
                    callback_data=f"toggle_source:{source_id}"
                ),
                InlineKeyboardButton(
                    text="🗑 Удалить",
                    callback_data=f"delete_source:{source_id}"
                )
            ]
        ]
    )

def source_type_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Telegram", callback_data="add_source_type:telegram")],
        [InlineKeyboardButton(text="Pinterest", callback_data="add_source_type:pinterest")],
    ])

def source_actions_keyboard(source_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="⏸ Вкл/выкл",
                callback_data=f"toggle_source:{source_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="🗑 Удалить",
                callback_data=f"delete_source:{source_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data="sources_list"
            )
        ],
    ])