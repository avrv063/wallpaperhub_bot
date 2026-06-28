from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def source_type_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Telegram", callback_data="add_source_type:telegram")],
        [InlineKeyboardButton(text="Pinterest", callback_data="add_source_type:pinterest")],
    ])