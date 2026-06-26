import os
from telethon import TelegramClient

from config import API_ID, API_HASH

SESSION_PATH = "data/wallpaperhub"


def get_telethon_client() -> TelegramClient:
    os.makedirs("data", exist_ok=True)

    return TelegramClient(
        SESSION_PATH,
        API_ID,
        API_HASH
    )