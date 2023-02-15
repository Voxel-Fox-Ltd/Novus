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

import types
from typing import TYPE_CHECKING, Any, Type, TypeVar

from ..utils import generate_repr

if TYPE_CHECKING:
    from ..api import HTTPConnection

__all__ = (
    'Object',
)


APIT = TypeVar("APIT")


class Object:
    """
    An abstract class that you can pass around to other classes requiring
    IDs and a state.
    """

    def __init__(
            self,
            id: int | str,
            *,
            state: HTTPConnection,
            guild_id: int | None = None,
            bases: tuple[Any] | None = None):
        self.id = int(id)
        self._state = state
        self.guild = None
        if guild_id:
            self.guild = Object(guild_id, state=state)
        else:
            del self.guild
        self.bases = bases or ()

    __repr__ = generate_repr(('id', 'guild', 'bases',))

    def __str__(self) -> str:
        if self.bases:
            return f"<({', '.join((i.__name__ for i in self.bases))}) Object[{self.id}]>"
        return f"<Object ({self.id})>"

    @classmethod
    def with_api(
            cls,
            bases: tuple[Type[APIT], ...],
            id: int | str,
            *,
            state: HTTPConnection,
            guild_id: int | None = None) -> APIT:
        """
        Return an object instance with an API built into it.
        """

        base_inheritance = []
        for i in bases:
            base_inheritance.extend(i.mro())
        api_bases = [i for i in base_inheritance if "APIMixin" in i.__name__]
        if not api_bases:
            raise TypeError("Missing 'APIMixin' class from mro")
        NewObject = types.new_class("ObjectType", (cls, *api_bases))
        return NewObject(id, state=state, guild_id=guild_id, bases=bases)
