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

from typing import TYPE_CHECKING, Any, TypeAlias

from ..utils import cached_slot_property, generate_repr, try_snowflake
from .api_mixins.emoji import EmojiAPIMixin
from .asset import Asset
from .mixins import Hashable
from .user import GuildMember

if TYPE_CHECKING:
    import io

    from ..api import HTTPConnection
    from ..payloads import Emoji as EmojiPayload
    from . import Message, abc

    FileT: TypeAlias = str | bytes | io.IOBase

__all__ = (
    'PartialEmoji',
    'Emoji',
    'Reaction',
)


class PartialEmoji(Hashable):
    """
    Any generic emoji.

    Attributes
    ----------
    id : int | None
        The ID of the emoji.
    name : str | None
        The name of the emoji. Could be ``None`` in the case that the emoji
        came from a reaction payload and isn't unicode.
    animated : bool
        If the emoji is animated.
    asset : novus.Asset | None
        The asset associated with the emoji, if it's a custom emoji.
    """

    __slots__ = (
        'id',
        'name',
        'animated',
        '_cs_asset',
    )

    def __init__(self, *, data: EmojiPayload):
        self.id: int | None = try_snowflake(data['id'])
        self.name = data['name']
        self.animated = data.get('animated', False)

    def __str__(self) -> str:
        if self.animated:
            return f"<a:{self.name}:{self.id}>"
        return f"<:{self.name}:{self.id}>"

    __repr__ = generate_repr(('id', 'name', 'animated',))

    @cached_slot_property('_cs_asset')
    def asset(self) -> Asset | None:
        if self.id is None:
            return None
        return Asset.from_emoji(self)


class Emoji(PartialEmoji, EmojiAPIMixin):
    """
    A custom emoji in a guild.

    Attributes
    ----------
    id : int | None
        The ID of the emoji.
    name : str | None
        The name of the emoji. Could be ``None`` in the case that the emoji
        came from a reaction payload and isn't unicode.
    role_ids : list[int]
        A list of role IDs that can use the role.
    requires_colons : bool
        Whether or not the emoji requires colons to send.
    managed : bool
        Whether or not the emoji is managed.
    animated : bool
        If the emoji is animated.
    available : bool
        If the emoji is available. May be ``False`` in the case that the guild
        has lost nitro boosts.
    asset : novus.Asset | None
        The asset associated with the emoji, if it's a custom emoji.
    guild : novus.abc.Snowflake | novus.Guild | None
        The guild (or a data container for the ID) that the emoji came from, if
        it was available.
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
            guild: abc.Snowflake | None):
        self._state = state
        super().__init__(data=data)
        self.role_ids = data.get('roles', list())
        self.requires_colons = data.get('require_colons', True)
        self.managed = data.get('managed', False)
        self.available = data.get('available', True)
        self.guild: abc.Snowflake | None = guild


class Reaction:
    """
    A reaction container class.

    Attributes
    ----------
    user_id : int
        The ID of the user who reacted.
    message_id : int
        The ID of the message that was reacted on.
    emoji : novus.PartialEmoji
        The emoji that was added to the message. This will only ever be a
        partial emoji (ie it will only have ID, name, and animated attributes
        set).
    channel_id
    burst
    guild_id
    member
    """

    def __init__(self, *, state: HTTPConnection, data: Any):
        self._state = state
        self.user_id: int = try_snowflake(data["user_id"])
        self.message_id: int = try_snowflake(data["message_id"])
        self.emoji: PartialEmoji = PartialEmoji(data=data["emoji"])
        self.channel_id: int = try_snowflake(data["channel_id"])
        self.burst: bool = data.get("burst", False)

        self.guild_id: int | None = try_snowflake(data.get("guild_id"))
        self.member: GuildMember | None
        if self.guild_id is not None:
            self.member = GuildMember(
                state=state,
                data=data["member"],
                guild=self.guild_id,
            )

    async def fetch_message(self) -> Message:
        """
        Get the message associated with the reaction. Generally not required if
        you just need to run some API methods on an object.

        Returns
        -------
        novus.Message
            The message instance for the reaction.
        """

        return await self._state.channel.get_channel_message(
            self.channel_id,
            self.message_id,
        )
