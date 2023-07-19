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

from typing import TYPE_CHECKING

from ..utils import generate_repr

if TYPE_CHECKING:
    from ..api import HTTPConnection
    from ..models import abc

__all__ = (
    'Object',
)


class Object:
    """
    An abstract class that you can pass around to other classes requiring
    IDs and a state.
    """

    def __init__(
            self,
            id: int | str,
            *,
            state: HTTPConnection = None,  # pyright: ignore  # Making compatible with statesnowflake
            guild: abc.Snowflake | None = None,
            guild_id: int | None = None):
        self.id = int(id)
        self.state = state
        self.guild = None
        if guild:
            self.guild = guild
        elif guild_id:
            from .guild import BaseGuild
            self.guild = BaseGuild(state=self.state, data={"id": guild_id})  # pyright: ignore
        else:
            del self.guild

    __repr__ = generate_repr(('id', 'guild', 'bases',))

    def __str__(self) -> str:
        return f"<Object ({self.id})>"
