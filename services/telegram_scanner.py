import os
from pathlib import Path

from services.telethon_client import get_telethon_client
from repositories.sources import get_active_telegram_sources, update_last_message_id
from repositories.candidates import add_candidate, candidate_exists


CANDIDATES_DIR = Path("data/images/candidates")
SCAN_LIMIT_FIRST_RUN = 100
SCAN_LIMIT_REGULAR = 50


def ensure_dirs():
    CANDIDATES_DIR.mkdir(parents=True, exist_ok=True)


def is_image_message(message) -> bool:
    if not message.media:
        return False

    if message.photo:
        return True

    document = getattr(message, "document", None)
    if document and getattr(document, "mime_type", None):
        return document.mime_type.startswith("image/")

    return False


async def scan_telegram_sources(progress_callback=None) -> dict:
    ensure_dirs()

    sources = await get_active_telegram_sources()

    result = {
        "sources_total": len(sources),
        "sources_checked": 0,
        "images_found": 0,
        "images_saved": 0,
        "errors": [],
    }

    if not sources:
        return result

    client = get_telethon_client()

    async with client:
        for index, source in enumerate(sources, start=1):
            source_id, username, title, last_message_id = source
            source_name = title or f"@{username}"

            if progress_callback:
                await progress_callback(
                    f"Проверяю {index}/{len(sources)}: {source_name}"
                )

            try:
                entity = await client.get_entity(username)

                limit = SCAN_LIMIT_FIRST_RUN if not last_message_id else SCAN_LIMIT_REGULAR
                max_seen_id = last_message_id or 0

                async for message in client.iter_messages(entity, limit=limit):
                    if not message:
                        continue

                    if message.id <= (last_message_id or 0):
                        break

                    max_seen_id = max(max_seen_id, message.id)

                    if not is_image_message(message):
                        continue

                    result["images_found"] += 1

                    if await candidate_exists(source_id, message.id):
                        continue

                    file_name = f"tg_{source_id}_{message.id}"
                    file_path = CANDIDATES_DIR / file_name

                    downloaded_path = await client.download_media(
                        message,
                        file=str(file_path)
                    )

                    if not downloaded_path:
                        continue

                    await add_candidate(
                        source_id=source_id,
                        message_id=message.id,
                        file_path=downloaded_path
                    )

                    result["images_saved"] += 1

                if max_seen_id > (last_message_id or 0):
                    await update_last_message_id(source_id, max_seen_id)

                result["sources_checked"] += 1

            except Exception as e:
                result["errors"].append(f"{source_name}: {e}")

    return result