from services.telegram_scanner import scan_telegram_sources
from services.pinterest_scanner import scan_pinterest_sources


async def scan_all_sources(progress_callback=None) -> dict:
    telegram_result = await scan_telegram_sources(progress_callback)
    pinterest_result = await scan_pinterest_sources(progress_callback)

    return {
        "sources_total": telegram_result["sources_total"] + pinterest_result["sources_total"],
        "sources_checked": telegram_result["sources_checked"] + pinterest_result["sources_checked"],
        "images_found": telegram_result["images_found"] + pinterest_result["images_found"],
        "images_saved": telegram_result["images_saved"] + pinterest_result["images_saved"],
        "errors": telegram_result["errors"] + pinterest_result["errors"],
    }