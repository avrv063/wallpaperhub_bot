import aiosqlite
from database import DB_PATH


async def add_candidate(source_id: int, message_id: int, file_path: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO candidates (source_id, message_id, file_path)
            VALUES (?, ?, ?)
            """,
            (source_id, message_id, file_path)
        )
        await db.commit()


async def candidate_exists(source_id: int, message_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            SELECT id FROM candidates
            WHERE source_id = ? AND message_id = ?
            LIMIT 1
            """,
            (source_id, message_id)
        )
        row = await cursor.fetchone()
        return row is not None


async def get_new_candidates(limit: int = 10):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            SELECT id, file_path, source_id, message_id
            FROM candidates
            WHERE status = 'new'
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,)
        )
        return await cursor.fetchall()
    
async def get_next_candidate():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            SELECT 
                c.id,
                c.file_path,
                c.source_id,
                c.message_id,
                s.type,
                s.username,
                s.title
            FROM candidates c
            LEFT JOIN sources s ON s.id = c.source_id
            WHERE c.status = 'new'
            ORDER BY c.id ASC
            LIMIT 1
            """
        )
        return await cursor.fetchone()


async def update_candidate_status(candidate_id: int, status: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            UPDATE candidates
            SET status = ?
            WHERE id = ?
            """,
            (status, candidate_id)
        )
        await db.commit()


async def count_new_candidates():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            SELECT COUNT(*)
            FROM candidates
            WHERE status = 'new'
            """
        )
        row = await cursor.fetchone()
        return row[0]
    
async def get_cleanup_candidates():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            SELECT id, file_path
            FROM candidates
            WHERE status IN ('new', 'skipped')
            """
        )
        return await cursor.fetchall()


async def delete_candidate(candidate_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            DELETE FROM candidates
            WHERE id = ?
            """,
            (candidate_id,)
        )
        await db.commit()    