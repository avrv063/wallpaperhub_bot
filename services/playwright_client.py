from playwright.async_api import async_playwright


async def get_page_image_urls(url: str, scrolls: int = 3) -> list[str]:
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

        page.set_default_timeout(15000)
        page.set_default_navigation_timeout(30000)

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(3000)

            for _ in range(scrolls):
                await page.mouse.wheel(0, 2500)
                await page.wait_for_timeout(1000)

            images = await page.locator("img").evaluate_all(
                """
                imgs => imgs
                    .map(img => img.src)
                    .filter(src => src && src.includes('pinimg.com'))
                """
            )

            for src in images:
                if src not in image_urls:
                    image_urls.append(src)

        finally:
            await browser.close()

    return image_urls