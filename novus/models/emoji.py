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

from typing import TYPE_CHECKING, TypeAlias

from .asset import Asset
from .mixins import Hashable
from .api_mixins.emoji import EmojiAPIMixin
from ..utils import try_snowflake, generate_repr, cached_slot_property

if TYPE_CHECKING:
    import io

    from .abc import Snowflake
    from ..api import HTTPConnection
    from ..payloads import Emoji as EmojiPayload

    FileT: TypeAlias = str | bytes | io.IOBase

__all__ = (
    'Emoji',
    'Reaction',
)


class Emoji(Hashable, EmojiAPIMixin):
    """
    A custom emoji in a guild.

    Attributes
    ----------
    id : int | None
        The ID of the emoji.
    name : str | None
        The name of the emoji. Could be ``None`` in the case that the emoji
        came from a reaction payload.
    role_ids : list[int]
        A list of role IDs that can use the role. If the list is empty, the
        role is accessible to everyone.
    requires_colons : bool
        Whether or not the emoji requires colons to send.
    managed : bool
        Whether or not the emoji is managed.
    animated : bool
        If the emoji is animated.
    available : bool
        If the emoji is available. May be ``False`` in the case that the guild
        has lost nitro boosts.
    asset : novus.models.Asset | None
        The asset associated with the emoji, if it's a custom emoji.
    guild : novus.models.abc.Snowflake | novus.models.Guild
        The guild (or a data container for the ID) that the emoji came from.
    """

    __slots__ = (
        '_state',
        'id',
        'name',
        'role_ids',
        'requires_colons',
        'managed',
        'animated',
        'available',
        'guild',

        '_cs_asset',
    )

    def __init__(
            self,
            *,
            state: HTTPConnection,
            data: EmojiPayload,
            guild: Snowflake):
        self._state = state
        if data['id'] is None:
            raise ValueError("Emoji ID cannot be None")
        self.id: int = try_snowflake(data['id'])
        self.name = data['name']
        self.role_ids = data.get('roles', list())
        self.requires_colons = data.get('require_colons', True)
        self.managed = data.get('managed', False)
        self.animated = data.get('animated', False)
        self.available = data.get('available', True)
        self.guild: Snowflake = guild

    def __str__(self) -> str:
        if self.animated:
            return f"<a:{self.name}:{self.id}>"
        return f"<:{self.name}:{self.id}>"

    __repr__ = generate_repr(('id', 'name', 'animated',))

    @cached_slot_property('_cs_asset')
    def asset(self) -> Asset | None:
        if self.id is not None:
            return Asset.from_emoji(self)
        return None


class Reaction:
    ...  # TODO
