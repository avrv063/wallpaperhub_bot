from services.telethon_client import get_telethon_client


async def check_telegram_source(username: str):
    client = get_telethon_client()

    async with client:
        entity = await client.get_entity(username)

        return {
            "title": getattr(entity, "title", username),
            "username": username,
            "id": entity.id,
        }