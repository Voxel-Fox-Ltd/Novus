from __future__ import annotations

import pathlib
import random
from typing import TYPE_CHECKING, Any, Generator, Iterable, TypeVar

import pytest
import yaml

import novus

__all__ = (
    'get_connection',
    'get_data',
    'max_choices',
    'cache',
    'ConfigUser',
    'ConfigGuild',
)


current_directory = pathlib.Path(__file__).parent
T = TypeVar('T')


class CacheList(list):

    def pop(self, *args, **kwargs):
        try:
            return super().pop(*args, **kwargs)
        except IndexError:
            pytest.skip("Exhausted list in cache")


class Cache:

    if TYPE_CHECKING:

        def __getattr__(self, name: str) -> list[Any]:
            ...

    def __setattr__(self, name: str, value: Any) -> None:
        if name not in self.__dict__:
            self.__dict__[name] = CacheList()
        self.__dict__[name].append(value)

    @staticmethod
    def iterate(val: Iterable[T]) -> Generator[T, None, None]:
        yield from val


cache = Cache()


def max_choices(it: Iterable[T], *, k: int) -> list[T]:
    it = list(it)
    return random.choices(it, k=min(k, len(it)))


def to_object(
        c: ConfigGuild | ConfigUser,
        state: novus.HTTPConnection,
        guild_id: int | None = None) -> novus.Object:
    return novus.Object(c.id, state=state, guild_id=guild_id)


def read_toml() -> dict:
    with open(current_directory / "env.yaml") as a:
        v = yaml.load(a, yaml.Loader)
    return v


def get_connection() -> novus.HTTPConnection:
    token = read_toml()['token']
    if not token:
        raise ValueError("Missing token from .env")
    return novus.HTTPConnection(token)


class ConfigUser:

    ALL: dict[int, ConfigUser] = {}

    def __init__(self, id: int, bot: bool) -> None:
        self.id: int = id
        self.bot: bool = bot
        self.ALL[self.id] = self
        self.state: novus.HTTPConnection | None = None


class ConfigGuild:

    ALL: dict[int, ConfigGuild] = {}

    def __init__(
            self,
            id: int,
            admin: bool = False,
            present: bool = False,
            test: bool = False,
            members: list[int] | None = None,
            automod_rules: list[int] | None = None,
            scheduled_events: list[int] | None = None) -> None:
        self.id: int = id
        self.admin: bool = admin
        self.present: bool = present
        self.members: list[ConfigUser] = [ConfigUser.ALL[i] for i in members or {}]
        self.automod_rules: list[int] = automod_rules or []
        self.scheduled_events: list[int] = scheduled_events or []
        self.test = test
        self.ALL[self.id] = self
        self.state: novus.HTTPConnection | None = None

    @classmethod
    def get_test(cls) -> ConfigGuild:
        guilds = tuple(i for i in cls.ALL.values() if i.test)
        if not guilds:
            pytest.skip("Missing test guild")
        return random.choice(guilds)


def get_data() -> tuple[list[ConfigUser], list[ConfigGuild]]:
    config = read_toml()
    for i in config['users']:
        ConfigUser(**i)
    for i in config['guilds']:
        ConfigGuild(**i)
    return (
        [*ConfigUser.ALL.values()],
        [*ConfigGuild.ALL.values()],
    )
