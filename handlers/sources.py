from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards.sources import source_type_keyboard

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

    await callback.message.answer(
        "Выбери тип источника:",
        reply_markup=source_type_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data.startswith("add_source_type:"))
async def choose_source_type(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Нет доступа.", show_alert=True)
        return

    source_type = callback.data.split(":")[1]

    await state.update_data(source_type=source_type)
    await state.set_state(AddSource.waiting_for_source)

    if source_type == "telegram":
        await callback.message.answer(
            "Пришли ссылку или username Telegram-канала.\n\n"
            "Например:\n"
            "@example_channel\n"
            "или\n"
            "https://t.me/example_channel"
        )
    elif source_type == "pinterest":
        await callback.message.answer(
            "Пришли ссылку Pinterest-доски, профиля или поисковый запрос.\n\n"
            "Например:\n"
            "https://www.pinterest.com/username/board/\n"
            "или\n"
            "foggy forest wallpaper"
        )

    await callback.answer()

@router.message(AddSource.waiting_for_source)
async def add_source_finish(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Нет доступа.")
        return

    data = await state.get_data()
    source_type = data.get("source_type", "telegram")

    if source_type == "telegram":
        username, url = normalize_source(message.text)

        if not username:
            await message.answer(
                "Не смог распознать Telegram-канал."
            )
            return

        try:
            info = await check_telegram_source(username)
        except Exception as e:
            await message.answer(
                f"Ошибка проверки Telegram:\n{e}"
            )
            return

        await add_source(
            username=username,
            url=url,
            title=info["title"],
            source_type="telegram"
        )

    elif source_type == "pinterest":

        url = message.text.strip()

        await add_source(
            username=url,
            url=url,
            title="Pinterest",
            source_type="pinterest"
        )

    await state.clear()

    await message.answer(
        "✅ Источник успешно добавлен."
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
        if source_type == "telegram":
            text += f"{source_id}. 🟦 Telegram — @{username} — {status}\n"
        elif source_type == "pinterest":
            text += f"{source_id}. 🟥 Pinterest — {username} — {status}\n"
        else:
            text += f"{source_id}. {source_type} — {username} — {status}\n"

    await callback.message.answer(text)
    await callback.answer()