import pathlib

import toml

import novus

__all__ = (
    'get_connection',
    'get_data',
)


current_directory = pathlib.Path(__file__).parent


def read_toml() -> dict:
    with open(current_directory / "env.toml") as a:
        return toml.load(a)


def get_connection() -> novus.HTTPConnection:
    token = read_toml()['token']
    if not token:
        raise ValueError("Missing token from .env")
    return novus.HTTPConnection(token)


def get_data() -> tuple[list[int], list[int], list[int]]:
    known_users = read_toml()['known_human_users']
    known_bots = read_toml()['known_bot_users']
    known_guilds = read_toml()['known_guilds']
    if not known_users:
        raise ValueError("Missing known_human_users from .env")
    if not known_bots:
        raise ValueError("Missing known_bot_users from .env")
    if not known_guilds:
        raise ValueError("Missing known_guilds from .env")
    return (
        known_users,
        known_bots,
        known_guilds,
    )
