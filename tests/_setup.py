import os

import dotenv

import novus

__all__ = (
    "get_connection",
    "get_data",
)


dotenv.load_dotenv()


def get_connection() -> novus.api.HTTPConnection:
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        raise ValueError("Missing DISCORD_BOT_TOKEN from .env")
    return novus.api.HTTPConnection(token)


def get_data() -> tuple[list[int], list[int]]:
    known_users = os.getenv("KNOWN_EXISTING_USERS")
    known_guilds = os.getenv("KNOWN_EXISTING_GUILDS")
    if not known_users:
        raise ValueError("Missing KNOWN_EXISTING_USERS from .env")
    if not known_guilds:
        raise ValueError("Missing KNOWN_EXISTING_GUILDS from .env")
    return (
        [int(i) for i in known_users.split(",")],
        [int(i) for i in known_guilds.split(",")],
    )
