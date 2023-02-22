"""
Copyright (c) Kae Bartlett

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any, ClassVar, TypeVar

from .command import Command
from .event import EventListener

if TYPE_CHECKING:
    import novus as n

    from .client import Client

__all__ = (
    'loadable',
    'Plugin',
)


log = logging.getLogger("novus.ext.bot.plugin")


T = TypeVar("T")


def loadable(cls: T) -> T:
    cls.__novus_loadable__ = None  # type: ignore
    return cls


class PluginMeta(type):
    def __init__(cls, name: str, bases: Any, dct: dict[str, Any]) -> None:
        super().__init__(name, bases, dct)

        # Clear caches
        cls._event_listeners: dict[str, set[EventListener]] = {}
        cls._commands: set[Command] = set()

        # Iterate over items
        for name, val in dct.items():

            # Add event listeners to cache
            if isinstance(val, EventListener):
                if val.event not in cls._event_listeners:
                    cls._event_listeners[val.event] = set()
                cls._event_listeners[val.event].add(val)

            # Add commands to cache
            if isinstance(val, Command):
                val.owner = cls
                cls._commands.add(val)


class Plugin(metaclass=PluginMeta):

    _event_listeners: ClassVar[dict[str, set[EventListener]]]
    _commands: ClassVar[set[Command]]
    _command_ids: ClassVar[dict[int, Command]]

    def __init__(self, bot: Client) -> None:
        self.bot: Client = bot

    def __repr__(self) -> str:
        return f"<Plugin[{self.__class__.__name__}]>"

    async def on_load(self) -> None:
        pass

    async def on_unload(self) -> None:
        pass

    def dispatch(self, event_name: str, *args: Any, **kwargs: Any) -> None:
        """
        Send data to an event within the plugin.
        """

        if event_name in self._event_listeners:
            for el in self._event_listeners[event_name]:
                try:
                    asyncio.create_task(
                        el.func(self, *args, **kwargs),  # pyright: ignore
                        name=f"{event_name} dispatch in {self.__class__.__name__}"
                    )
                except Exception as e:
                    log.error("Failed to run listener from dispatch", exc_info=e)
