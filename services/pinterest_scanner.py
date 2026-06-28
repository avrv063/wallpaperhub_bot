import hashlib
import re
from pathlib import Path
from urllib.parse import quote_plus

import aiohttp

from repositories.sources import get_active_pinterest_sources
from repositories.candidates import add_candidate, candidate_exists

CANDIDATES_DIR = Path("data/images/candidates")
LIMIT_PER_SOURCE = 20


def ensure_dirs():
    CANDIDATES_DIR.mkdir(parents=True, exist_ok=True)


def source_to_url(source_text: str) -> str:
    source_text = source_text.strip()

    if source_text.startswith("http"):
        return source_text

    query = quote_plus(source_text)
    return f"https://www.pinterest.com/search/pins/?q={query}"


def extract_image_urls(html: str) -> list[str]:
    urls = re.findall(r'https://i\.pinimg\.com/[^"\']+', html)

    cleaned = []

    for url in urls:
        url = url.replace("\\u002F", "/")
        url = url.replace("\\/", "/")
        url = url.split("?")[0]

        if url not in cleaned and any(ext in url.lower() for ext in [".jpg", ".jpeg", ".png", ".webp"]):
            cleaned.append(url)

    return cleaned


def url_to_id(url: str) -> int:
    digest = hashlib.md5(url.encode("utf-8")).hexdigest()
    return int(digest[:12], 16)


async def download_image(session: aiohttp.ClientSession, url: str, path: Path) -> bool:
    try:
        async with session.get(url) as response:
            print("DOWNLOAD STATUS:", response.status)
            print("CONTENT TYPE:", response.headers.get("content-type"))

            if response.status != 200:
                return False

            content = await response.read()
            print("CONTENT SIZE:", len(content))

            if len(content) < 5_000:
                return False

            path.write_bytes(content)
            return True

    except Exception as e:
        print("DOWNLOAD ERROR:", e)
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
            source_id, username, title, url = source
            source_text = url or username
            page_url = source_to_url(source_text)

            if progress_callback:
                await progress_callback(
                    f"Pinterest {index}/{len(sources)}: {source_text}"
                )

            try:
                async with session.get(page_url) as response:
                    html = await response.text()

                image_urls = extract_image_urls(html)[:LIMIT_PER_SOURCE]
                print("PINTEREST SOURCE:", source_text)
                print("HTML LENGTH:", len(html))
                print("IMAGE URLS:", len(image_urls))
                result["images_found"] += len(image_urls)

                for image_url in image_urls:
                    image_id = url_to_id(image_url)

                    if await candidate_exists(source_id, image_id):
                        continue

                    ext = image_url.split(".")[-1].split("/")[0]
                    if ext.lower() not in ["jpg", "jpeg", "png", "webp"]:
                        ext = "jpg"

                    file_path = CANDIDATES_DIR / f"pin_{source_id}_{image_id}.{ext}"
                    print("IMAGE URL:", image_url)
                    print("FILE PATH:", file_path)
                    downloaded = await download_image(session, image_url, file_path)
                    print("DOWNLOADED:", downloaded)

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