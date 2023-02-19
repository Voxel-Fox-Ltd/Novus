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

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..api import HTTPConnection
    from .abc import Snowflake

__all__ = (
    'EqualityComparable',
    'Hashable',
    'HasChannel',
)


class EqualityComparable:

    __slots__ = ()

    id: int

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, self.__class__)
            and other.id == self.id
        )

    def __ne__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            return other.id != self.id
        return True


class Hashable(EqualityComparable):

    __slots__ = ()

    def __hash__(self) -> int:
        return self.id >> 22


class HasChannel:
    """
    Mixin that returns a channel object.
    """

    state: HTTPConnection

    async def _get_channel(self) -> Snowflake:
        return self  # pyright: ignore
