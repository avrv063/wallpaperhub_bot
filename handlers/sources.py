from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import ADMIN_ID
from repositories.sources import add_source, get_sources
from services.telegram_parser import check_telegram_source

router = Router()


class AddSource(StatesGroup):
    waiting_for_source = State()


def normalize_source(text: str):
    text = text.strip()

    if text.startswith("https://t.me/"):
        username = text.replace("https://t.me/", "").split("/")[0]
    elif text.startswith("t.me/"):
        username = text.replace("t.me/", "").split("/")[0]
    elif text.startswith("@"):
        username = text[1:]
    else:
        username = text

    username = username.strip()

    if not username:
        return None, None

    return username, f"https://t.me/{username}"


@router.callback_query(F.data == "add_source")
async def add_source_start(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Нет доступа.", show_alert=True)
        return

    await state.set_state(AddSource.waiting_for_source)
    await callback.message.answer(
        "Пришли ссылку или username Telegram-канала.\n\n"
        "Например:\n"
        "@example_channel\n"
        "или\n"
        "https://t.me/example_channel"
    )
    await callback.answer()


@router.message(AddSource.waiting_for_source)
async def add_source_finish(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Нет доступа.")
        return

    username, url = normalize_source(message.text)

    if not username:
        await message.answer("Не смог распознать источник. Пришли @username или ссылку t.me.")
        return

    try:
        info = await check_telegram_source(username)
    except Exception as e:
        await message.answer(
            "Не смог проверить источник.\n\n"
            f"Ошибка: {e}\n\n"
            "Проверь, что канал существует и доступен твоему аккаунту."
        )
        return

    await add_source(username=username, url=url, title=info["title"])
    await state.clear()

    await message.answer(
        f"Источник добавлен:\n\n"
        f"Название: {info['title']}\n"
        f"Канал: @{username}\n\n"
        f"Позже бот будет забирать оттуда только изображения."
    )


@router.callback_query(F.data == "sources_list")
async def sources_list(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Нет доступа.", show_alert=True)
        return

    sources = await get_sources()

    if not sources:
        await callback.message.answer("Источников пока нет.")
        await callback.answer()
        return

    text = "📚 Источники:\n\n"

    for source_id, source_type, username, title, status, last_message_id in sources:
        name = title or f"@{username}"
        text += f"{source_id}. {name} — @{username} — {status}\n"

    await callback.message.answer(text)
    await callback.answer()