from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def choose_collection_keyboard(collections, candidate_id: int):
    keyboard = []

    for collection_id, title, count in collections:
        keyboard.append([
            InlineKeyboardButton(
                text=f"{title} ({count})",
                callback_data=f"add_to_collection:{candidate_id}:{collection_id}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            text="➕ Новая подборка",
            callback_data=f"new_collection:{candidate_id}"
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def collections_list_keyboard(collections):
    keyboard = []

    for collection_id, title, count in collections:
        keyboard.append([
            InlineKeyboardButton(
                text=f"{title} ({count})",
                callback_data=f"open_collection:{collection_id}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            text="➕ Новая подборка",
            callback_data="create_collection"
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def collection_actions_keyboard(collection_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🚀 Собрать пост",
                callback_data=f"build_post:{collection_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="✏️ Переименовать",
                callback_data=f"rename_collection:{collection_id}"
            ),
            InlineKeyboardButton(
                text="🗑 Очистить",
                callback_data=f"clear_collection:{collection_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="⬅️ К подборкам",
                callback_data="collections"
            )
        ],
    ])