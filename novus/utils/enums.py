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

from enum import Enum
from typing import Type, TypeVar, overload

__all__ = (
    'try_enum',
)


E = TypeVar('E', bound=Enum)


@overload
def try_enum(enum: Type[E], value: int | str) -> E:
    ...


@overload
def try_enum(enum: Type[E], value: None) -> None:
    ...


def try_enum(enum: Type[E], value: int | str | None = None) -> E | None:
    if value is None:
        return None
    return enum(value)
