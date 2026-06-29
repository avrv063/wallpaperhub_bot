from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔥 Новые кандидаты", callback_data="candidates")],
        [InlineKeyboardButton(text="📦 Мои подборки", callback_data="collections")],
        [InlineKeyboardButton(text="➕ Добавить источник", callback_data="add_source")],
        [InlineKeyboardButton(text="📚 Источники", callback_data="sources_list")],
        [InlineKeyboardButton(text="🔍 Найти контент", callback_data="scan_sources")],
        [InlineKeyboardButton(text="🚀 Тест публикации", callback_data="test_publish")],
        [InlineKeyboardButton(text="🧹 Очистить мусор", callback_data="cleanup_candidates")],
        [InlineKeyboardButton(text="🛑 Остановить поиск", callback_data="cancel_scan")],
    ])