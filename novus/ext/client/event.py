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
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from __future__ import annotations

from collections.abc import Awaitable
from typing import TYPE_CHECKING, Any, Callable, TypeAlias

if TYPE_CHECKING:
    import novus

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
        'owner',
    )

    def __init__(self, event_name: str, func: Callable[..., Awaitable[Any]]) -> None:
        self.event = event_name
        self.func: Callable[..., Awaitable[Any]] = func
        self.owner: Any = None


Self = Any  # Self
AA = Awaitable[Any]
EL: TypeAlias = EventListener


class EventBuilder:

    __slots__ = ()

    @classmethod
    def message(cls, func: Callable[[Self, novus.Message], AA]) -> EL:
        return EventListener("message", func)

    @staticmethod
    def __call__(event_name: str) -> Callable[..., EL]:
        def wrapper(func: Callable[..., AA]) -> EL:
            return EventListener(event_name, func)
        return wrapper  # pyright: ignore


event = EventBuilder()
