import aiosqlite
from database import DB_PATH


async def add_source(
    username: str,
    url: str | None = None,
    title: str | None = None,
    source_type: str = "telegram"
):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT OR IGNORE INTO sources (type, username, url, title)
            VALUES (?, ?, ?, ?)
            """,
            (source_type, username, url, title)
        )
        await db.commit()


async def get_sources():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            SELECT id, type, username, title, status, last_message_id
            FROM sources
            ORDER BY id DESC
            """
        )
        return await cursor.fetchall()


async def get_active_telegram_sources():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            SELECT id, username, title, last_message_id
            FROM sources
            WHERE type = 'telegram' AND status = 'active'
            ORDER BY id DESC
            """
        )
        return await cursor.fetchall()


async def update_last_message_id(source_id: int, last_message_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            UPDATE sources
            SET last_message_id = ?
            WHERE id = ?
            """,
            (last_message_id, source_id)
        )
        await db.commit()