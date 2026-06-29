from playwright.async_api import async_playwright


async def get_page_image_urls(url: str, scrolls: int = 5) -> list[str]:
    image_urls = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        page = await browser.new_page(
            viewport={"width": 1280, "height": 1800},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )

        await page.goto(url, wait_until="domcontentloaded", timeout=90000)
        await page.wait_for_timeout(5000)

        for _ in range(scrolls):
            await page.mouse.wheel(0, 3000)
            await page.wait_for_timeout(2000)

        images = await page.locator("img").evaluate_all(
            """
            imgs => imgs
                .map(img => img.src)
                .filter(src => src && src.includes('pinimg.com'))
            """
        )

        await browser.close()

    for src in images:
        if src not in image_urls:
            image_urls.append(src)

    return image_urls