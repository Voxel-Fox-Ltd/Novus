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

from collections.abc import Awaitable
from typing import Any, Callable

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


def event(event_name: str) -> Callable[..., EventListener]:
    def wrapper(func: Callable[..., Awaitable[Any]]) -> EventListener:
        return EventListener(event_name, func)
    return wrapper  # pyright: ignore
