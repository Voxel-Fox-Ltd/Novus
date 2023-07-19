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

from typing import Any, Callable, Generic, Type, TypeVar, overload

__all__ = (
    'cached_slot_property',
)


T = TypeVar("T")
R = TypeVar("R")


class CachedSlotProperty(Generic[T, R]):

    __slots__ = (
        'name',
        'func',
        '__doc__',
    )

    def __init__(self, name: str, func: Callable[[T], R]) -> None:
        self.name = name
        self.func = func
        self.__doc__ = getattr(func, '__doc__')

    @overload
    def __get__(self, instance: None, owner: Type[T]) -> CachedSlotProperty[T, R]:
        ...

    @overload
    def __get__(self, instance: T, owner: Type[T]) -> R:
        ...

    def __get__(self, instance: T | None, owner: Type[T]) -> Any:
        if instance is None:
            return self
        try:
            return getattr(instance, self.name)
        except AttributeError:
            value = self.func(instance)
            setattr(instance, self.name, value)
            return value

    def __delete__(self, instance: T) -> None:
        try:
            delattr(instance, self.name)
        except AttributeError:
            pass


def cached_slot_property(name: str) -> Callable[[Callable[[T], R]], CachedSlotProperty[T, R]]:
    def decorator(func: Callable[[T], R]) -> CachedSlotProperty[T, R]:
        return CachedSlotProperty(name, func)
    return decorator
