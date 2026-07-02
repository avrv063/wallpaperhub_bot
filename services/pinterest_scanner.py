import hashlib
from pathlib import Path
from urllib.parse import quote_plus

import aiohttp
import random

from repositories.sources import get_active_pinterest_sources
from repositories.candidates import add_candidate, candidate_exists
from services.playwright_client import get_page_image_urls

from services.scan_control import is_scan_cancelled

CANDIDATES_DIR = Path("data/images/candidates")
LIMIT_PER_SOURCE = 10


def ensure_dirs():
    CANDIDATES_DIR.mkdir(parents=True, exist_ok=True)


def source_to_url(source_text: str) -> str:
    source_text = source_text.strip()

    if source_text.startswith("http"):
        return source_text

    query = quote_plus(source_text)
    return f"https://www.pinterest.com/search/pins/?q={query}"


def url_to_id(url: str) -> int:
    digest = hashlib.md5(url.encode("utf-8")).hexdigest()
    return int(digest[:12], 16)


async def download_image(session: aiohttp.ClientSession, url: str, path: Path) -> bool:
    try:
        async with session.get(url) as response:
            if response.status != 200:
                return False

            content = await response.read()

            if len(content) < 5_000:
                return False

            path.write_bytes(content)
            return True

    except Exception:
        return False


async def scan_pinterest_sources(progress_callback=None) -> dict:
    ensure_dirs()

    sources = await get_active_pinterest_sources()

    result = {
        "sources_total": len(sources),
        "sources_checked": 0,
        "images_found": 0,
        "images_saved": 0,
        "errors": [],
    }

    if not sources:
        return result

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        for index, source in enumerate(sources, start=1):
            if is_scan_cancelled():
                result["errors"].append("Поиск остановлен пользователем.")
                break
            source_id, username, title, url = source
            source_text = url or username
            page_url = source_to_url(source_text)

            if progress_callback:
                await progress_callback(
                    f"🔎 Pinterest {index}/{len(sources)}\n\n"
                    f"Источник:\n{source_text}\n\n"
                    f"Ищу картинки..."
                )

            try:
                image_urls = await get_page_image_urls(page_url)
                random.shuffle(image_urls)
                image_urls = image_urls[:LIMIT_PER_SOURCE]

                result["images_found"] += len(image_urls)

                for image_url in image_urls:
                    if is_scan_cancelled():
                        result["errors"].append("Поиск остановлен пользователем.")
                        break
                    image_id = url_to_id(image_url)

                    if await candidate_exists(source_id, image_id):
                        continue

                    ext = image_url.split(".")[-1].split("?")[0].lower()
                    if ext not in ["jpg", "jpeg", "png", "webp"]:
                        ext = "jpg"

                    file_path = CANDIDATES_DIR / f"pin_{source_id}_{image_id}.{ext}"

                    downloaded = await download_image(session, image_url, file_path)

                    if not downloaded:
                        continue

                    await add_candidate(
                        source_id=source_id,
                        message_id=image_id,
                        file_path=str(file_path)
                    )

                    result["images_saved"] += 1

                result["sources_checked"] += 1

            except Exception as e:
                result["errors"].append(f"Pinterest {source_text}: {e}")

    return result