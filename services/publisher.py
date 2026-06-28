import os

from aiogram import Bot
from aiogram.types import FSInputFile, InputMediaPhoto

from config import CHANNEL_ID


async def publish_collection(bot: Bot, caption: str, file_paths: list[str]):
    existing_files = [path for path in file_paths if os.path.exists(path)]

    if not existing_files:
        return False

    media = []

    for index, path in enumerate(existing_files[:10]):
        media.append(
            InputMediaPhoto(
                media=FSInputFile(path),
                caption=caption if index == 0 else None
            )
        )

    await bot.send_media_group(
        chat_id=CHANNEL_ID,
        media=media
    )

    for path in existing_files:
        await bot.send_document(
            chat_id=CHANNEL_ID,
            document=FSInputFile(path)
        )

    return True