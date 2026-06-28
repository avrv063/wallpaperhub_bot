from repositories.collections import get_collection, get_collection_items


def make_caption(title: str) -> str:
    return (
        f"{title}\n\n"
        f"Подборка атмосферных обоев для телефона и ПК.\n\n"
        f"#обои #атмосфера"
    )


async def build_post(collection_id: int):
    collection = await get_collection(collection_id)
    items = await get_collection_items(collection_id)

    if not collection:
        return None

    collection_id, title, status = collection

    return {
        "collection_id": collection_id,
        "title": title,
        "caption": make_caption(title),
        "items": items,
    }