import aiosqlite
from database import DB_PATH


async def create_collection(title: str):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            INSERT INTO collections (title)
            VALUES (?)
            """,
            (title,)
        )
        await db.commit()
        return cursor.lastrowid


async def get_draft_collections():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            SELECT c.id, c.title, COUNT(ci.id) as items_count
            FROM collections c
            LEFT JOIN collection_items ci ON ci.collection_id = c.id
            WHERE c.status = 'draft'
            GROUP BY c.id
            ORDER BY c.id DESC
            """
        )
        return await cursor.fetchall()


async def add_candidate_to_collection(collection_id: int, candidate_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            SELECT COALESCE(MAX(position), 0) + 1
            FROM collection_items
            WHERE collection_id = ?
            """,
            (collection_id,)
        )
        next_position = (await cursor.fetchone())[0]

        await db.execute(
            """
            INSERT INTO collection_items (collection_id, candidate_id, position)
            VALUES (?, ?, ?)
            """,
            (collection_id, candidate_id, next_position)
        )

        await db.execute(
            """
            UPDATE candidates
            SET status = 'in_collection'
            WHERE id = ?
            """,
            (candidate_id,)
        )

        await db.commit()


async def get_collection_items(collection_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            SELECT ci.id, c.id, c.file_path, ci.position
            FROM collection_items ci
            JOIN candidates c ON c.id = ci.candidate_id
            WHERE ci.collection_id = ?
            ORDER BY ci.position ASC
            """,
            (collection_id,)
        )
        return await cursor.fetchall()
    
async def get_collection(collection_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            SELECT id, title, status
            FROM collections
            WHERE id = ?
            """,
            (collection_id,)
        )
        return await cursor.fetchone()
    
async def clear_collection_items(collection_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            UPDATE candidates
            SET status = 'new'
            WHERE id IN (
                SELECT candidate_id
                FROM collection_items
                WHERE collection_id = ?
            )
            """,
            (collection_id,)
        )

        await db.execute(
            """
            DELETE FROM collection_items
            WHERE collection_id = ?
            """,
            (collection_id,)
        )

        await db.commit()

async def delete_collection_item(item_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "DELETE FROM collection_items WHERE id = ?",
            (item_id,)
        )
        await db.commit()