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
from typing import TYPE_CHECKING, Any, Type, overload

from ..utils import generate_repr

if TYPE_CHECKING:
    from ..api import HTTPConnection
    from ..models import Channel, Emoji, Guild, GuildMember, Message, Role, User
    from ..models import api_mixins as amix

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
            state: HTTPConnection = None,  # pyright: ignore
            guild_id: int | None = None,
            bases: tuple[Any] | None = None):
        self.id = int(id)
        self.state = state
        self.guild = None
        if guild_id:
            from .guild import Guild
            self.guild = Object(guild_id, state=state).add_api(Guild)
        else:
            del self.guild
        self.bases = bases or ()

    __repr__ = generate_repr(('id', 'guild', 'bases',))

    def __str__(self) -> str:
        if self.bases:
            return f"<({', '.join((i.__name__ for i in self.bases))}) Object[{self.id}]>"
        return f"<Object ({self.id})>"

    @overload
    def add_api(self, base: Type[Guild]) -> amix.GuildAPIMixin:
        ...

    @overload
    def add_api(self, base: Type[Channel]) -> amix.ChannelAPIMixin:
        ...

    @overload
    def add_api(self, base: Type[Emoji]) -> amix.EmojiAPIMixin:
        ...

    @overload
    def add_api(self, base: Type[Message]) -> amix.MessageAPIMixin:
        ...

    @overload
    def add_api(self, base: Type[Role]) -> amix.RoleAPIMixin:
        ...

    @overload
    def add_api(self, base: Type[User]) -> amix.UserAPIMixin:
        ...

    @overload
    def add_api(self, base: Type[GuildMember]) -> amix.GuildMemberAPIMixin:
        ...

    def add_api(self, base: Any) -> Any:
        base_inheritance = base.mro()
        api_bases = [i for i in base_inheritance if "APIMixin" in i.__name__]
        if not api_bases:
            raise TypeError("Missing 'APIMixin' class from mro")
        NewObject = types.new_class("NewObject", (Object, *api_bases))
        v = NewObject(self.id, state=self.state, bases=(base,))
        if hasattr(self, 'guild'):
            v.guild = self.guild
        return v
