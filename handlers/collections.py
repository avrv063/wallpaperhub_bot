from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from aiogram.types import FSInputFile
import os

from config import ADMIN_ID
from repositories.collections import (
    create_collection,
    get_draft_collections,
    add_candidate_to_collection,
    get_collection_items,
    clear_collection_items,
)
from keyboards.collections import (
    choose_collection_keyboard,
    collections_list_keyboard,
    collection_actions_keyboard,
)

from services.post_builder import build_post
from services.publisher import publish_collection
from keyboards.collections import post_preview_keyboard

router = Router()


class CreateCollection(StatesGroup):
    waiting_for_title = State()
    waiting_for_title_with_candidate = State()


@router.callback_query(F.data.startswith("candidate_add:"))
async def choose_collection(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Нет доступа.", show_alert=True)
        return

    candidate_id = int(callback.data.split(":")[1])
    collections = await get_draft_collections()

    await callback.message.answer(
        "Куда добавить изображение?",
        reply_markup=choose_collection_keyboard(collections, candidate_id)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("add_to_collection:"))
async def add_to_collection(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Нет доступа.", show_alert=True)
        return

    _, candidate_id, collection_id = callback.data.split(":")
    await add_candidate_to_collection(int(collection_id), int(candidate_id))

    await callback.message.answer("✅ Добавлено в подборку.")
    await callback.answer()


@router.callback_query(F.data.startswith("new_collection:"))
async def new_collection_from_candidate(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Нет доступа.", show_alert=True)
        return

    candidate_id = int(callback.data.split(":")[1])
    await state.update_data(candidate_id=candidate_id)
    await state.set_state(CreateCollection.waiting_for_title_with_candidate)

    await callback.message.answer("Напиши название новой подборки:")
    await callback.answer()


@router.message(CreateCollection.waiting_for_title_with_candidate)
async def create_collection_with_candidate(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Нет доступа.")
        return

    data = await state.get_data()
    candidate_id = data["candidate_id"]

    collection_id = await create_collection(message.text.strip())
    await add_candidate_to_collection(collection_id, candidate_id)

    await state.clear()
    await message.answer(f"✅ Подборка создана и изображение добавлено:\n\n{message.text.strip()}")


@router.callback_query(F.data == "collections")
async def collections_menu(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Нет доступа.", show_alert=True)
        return

    collections = await get_draft_collections()

    if not collections:
        await callback.message.answer("Подборок пока нет.", reply_markup=collections_list_keyboard(collections))
    else:
        await callback.message.answer("📦 Мои подборки:", reply_markup=collections_list_keyboard(collections))

    await callback.answer()


@router.callback_query(F.data == "create_collection")
async def create_collection_start(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Нет доступа.", show_alert=True)
        return

    await state.set_state(CreateCollection.waiting_for_title)
    await callback.message.answer("Напиши название новой подборки:")
    await callback.answer()


@router.message(CreateCollection.waiting_for_title)
async def create_collection_finish(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Нет доступа.")
        return

    title = message.text.strip()
    await create_collection(title)
    await state.clear()

    await message.answer(f"✅ Подборка создана:\n\n{title}")


@router.callback_query(F.data.startswith("open_collection:"))
async def open_collection(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Нет доступа.", show_alert=True)
        return

    collection_id = int(callback.data.split(":")[1])
    items = await get_collection_items(collection_id)

    if not items:
        await callback.message.answer("В подборке пока нет изображений.")
        await callback.answer()
        return

    await callback.message.answer(
        f"📦 Подборка #{collection_id}\n\n"
        f"Изображений: {len(items)}",
        reply_markup=collection_actions_keyboard(collection_id)
    )

    for item_id, candidate_id, file_path, position in items:
        if not os.path.exists(file_path):
            await callback.message.answer(f"⚠️ Файл #{candidate_id} не найден.")
            continue

        await callback.message.answer_photo(
            photo=FSInputFile(file_path),
            caption=f"#{position} • Candidate ID: {candidate_id}"
        )

    await callback.answer()

@router.callback_query(F.data.startswith("build_post:"))
async def build_post_handler(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Нет доступа.", show_alert=True)
        return

    collection_id = int(callback.data.split(":")[1])
    post = await build_post(collection_id)

    if not post or not post["items"]:
        await callback.message.answer("В подборке нет изображений.")
        await callback.answer()
        return

    await callback.message.answer(
        f"📝 Черновик поста:\n\n{post['caption']}\n\n"
        f"Изображений: {len(post['items'])}",
        reply_markup=post_preview_keyboard(collection_id)
    )

    await callback.answer()

@router.callback_query(F.data.startswith("publish_post:"))
async def publish_post_handler(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Нет доступа.", show_alert=True)
        return

    collection_id = int(callback.data.split(":")[1])
    post = await build_post(collection_id)

    if not post or not post["items"]:
        await callback.message.answer("Не удалось собрать пост.")
        await callback.answer()
        return

    file_paths = [item[2] for item in post["items"]]

    ok = await publish_collection(
        bot=callback.bot,
        caption=post["caption"],
        file_paths=file_paths
    )

    if ok:
        await callback.message.answer("✅ Пост опубликован.")
    else:
        await callback.message.answer("❌ Не удалось опубликовать пост.")

    await callback.answer()

@router.callback_query(F.data.startswith("clear_collection:"))
async def clear_collection(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Нет доступа.", show_alert=True)
        return

    collection_id = int(callback.data.split(":")[1])

    await clear_collection_items(collection_id)

    await callback.message.answer(
        f"🗑 Подборка #{collection_id} очищена."
    )

    await callback.answer()


@router.callback_query(F.data.startswith("rename_collection:"))
async def rename_collection(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Нет доступа.", show_alert=True)
        return

    collection_id = int(callback.data.split(":")[1])

    await callback.message.answer(
        f"✏️ Переименование подборки #{collection_id} пока не подключено.\n"
        "Следующим шагом добавим ввод нового названия."
    )

    await callback.answer()