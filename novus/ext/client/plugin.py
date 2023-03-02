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
from collections import defaultdict
from typing import TYPE_CHECKING, Any, ClassVar, TypeAlias, TypeVar

import novus as n

from .command import Command, CommandDescription, CommandGroup
from .event import EventListener

if TYPE_CHECKING:
    from .client import Client

    JsonPrimitive = str | bool | int | float
    JsonPrimList = list['JsonPrimitive' | list['JsonPrimList'] | list['JsonPrimDict']]
    JsonPrimDict = dict[str, 'JsonPrimitive' | 'JsonPrimList' | 'JsonPrimDict']
    JsonValue =  JsonPrimDict

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
        cls._commands: set[Command | CommandGroup] = set()

        # Iterate over items
        subcommands: dict[str, set[Command]] = defaultdict(set)
        descriptions: dict[str, CommandDescription] = {}
        for name, val in dct.items():

            # Add event listeners to cache
            if isinstance(val, EventListener):
                if val.event not in cls._event_listeners:
                    cls._event_listeners[val.event] = set()
                cls._event_listeners[val.event].add(val)

            # Add commands to cache
            if isinstance(val, Command):
                val.owner = cls
                if val.type == n.ApplicationCommandType.chat_input and " " in val.name:
                    subcommands[val.name.split(" ")[0]].add(val)
                cls._commands.add(val)

            # Temporarily cache command descriptions
            if isinstance(val, CommandDescription):
                descriptions[name] = val

        # Group subcommands
        groups: dict[str, CommandGroup] = {}
        for _, subs in subcommands.items():
            base_name = list(subs)[0].name.split(" ")[0]
            created_group = CommandGroup.from_commands(
                subs,
                run_checks=base_name not in descriptions
            )
            cls._commands.add(created_group)
            groups[created_group.name] = created_group
        for g, d in descriptions.items():
            groups[g].add_description(d)


class Plugin(metaclass=PluginMeta):
    """
    The base command class for any novus client commands.
    """

    _event_listeners: ClassVar[dict[str, set[EventListener]]]
    _commands: ClassVar[set[Command]]
    _command_ids: ClassVar[dict[int, Command]]

    CONFIG: ClassVar[JsonValue] = {}

    def __init__(self, bot: Client) -> None:
        self.bot: Client = bot

    def __repr__(self) -> str:
        return f"<Plugin[{self.__class__.__name__}]>"

    async def on_load(self) -> None:
        """
        A function to be run when the plugin is loaded.
        The plugin is not automatically loaded on its addition to the bot, but
        on its connection to the gateway. If the bot does not connect to the
        gateway, this function will never be called.
        """

        pass

    async def on_unload(self) -> None:
        """
        A function to be run automatically where the plugin is removed from the
        bot.
        This function is not run if there is not an event loop running.
        """
        pass

    def dispatch(self, event_name: str, *args: Any, **kwargs: Any) -> None:
        """
        Send data to an event within the plugin.
        """

        if event_name in self._event_listeners:
            for el in self._event_listeners[event_name]:
                run = True
                try:
                    run = el.predicate(*args, **kwargs)
                except Exception as e:
                    log.error("Failed to run predicate for event listener", exc_info=e)
                    continue
                if not run:
                    continue
                try:
                    asyncio.create_task(
                        el.func(self, *args, **kwargs),  # pyright: ignore
                        name=f"{event_name} dispatch in {self.__class__.__name__}"
                    )
                except Exception as e:
                    log.error("Failed to run listener from dispatch", exc_info=e)
