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

import re
from collections.abc import Awaitable
from typing import TYPE_CHECKING, Any, Callable, TypeAlias, TypeVar

import novus

if TYPE_CHECKING:
    from novus.models import Interaction, Message, MessageComponentData

__all__ = (
    'event',
    'EventListener',
)


class EventListener:
    """
    An object that listens for an event.
    """

    __slots__ = (
        'event',
        'func',
        'predicate',
        'owner',
    )

    def __init__(
            self,
            event_name: str,
            func: Callable[..., Awaitable[Any]],
            predicate: Callable[..., bool] | None = None) -> None:
        self.event = event_name
        self.func: Callable[..., Awaitable[Any]] = func
        self.predicate: Callable[..., bool] = lambda x: True
        if predicate:
            self.predicate = predicate
        self.owner: Any = None

    async def run(self, *args, **kwargs) -> None:
        await self.func(self.owner, *args, **kwargs)


Self: TypeAlias = Any  # Named Any
AA = Awaitable[Any]  # Any awaitable
EL: TypeAlias = EventListener
T = TypeVar("T")
W = Callable[[Self, T], AA]  # Wrapper
WEL = Callable[[Callable[[Self, T], Any]], EL]  # Wrapped event listener


class EventBuilder:

    __slots__ = ()

    @classmethod
    def filtered_component(cls, match_string: str) -> WEL[Interaction[MessageComponentData]]:
        def wrapper(func: W[Interaction[MessageComponentData]]) -> EL:
            return EventListener(
                "INTERACTION_CREATE",
                func,
                lambda i: bool(
                    i.type == novus.InteractionType.message_component
                    and i.custom_id
                    and re.search(match_string, i.custom_id)
                ),
            )
        return wrapper

    @classmethod
    def component(cls, func: W[Interaction[MessageComponentData]]) -> EL:
        return EventListener(
            "INTERACTION_CREATE",
            func,
            lambda i: i.type == novus.InteractionType.message_component,
        )

    @classmethod
    def interaction(cls, func: W[Interaction]) -> EL:
        return EventListener("INTERACTION_CREATE", func)

    @classmethod
    def message(cls, func: W[Message]) -> EL:
        return EventListener("MESSAGE_CREATE", func)

    @staticmethod
    def __call__(
            event_name: str,
            predicate: Callable[..., bool] | None = None) -> WEL:
        def wrapper(func: Callable[..., AA]) -> EL:
            return EventListener(event_name, func, predicate)
        return wrapper  # pyright: ignore


event = EventBuilder()
