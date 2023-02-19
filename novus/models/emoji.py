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

import re
from typing import TYPE_CHECKING, TypeAlias, overload

import emoji

from ..utils import cached_slot_property, generate_repr, try_snowflake
from .api_mixins.emoji import EmojiAPIMixin
from .asset import Asset
from .mixins import Hashable

if TYPE_CHECKING:
    import io

    from .. import payloads
    from ..api import HTTPConnection
    from . import Guild
    from . import api_mixins as amix

    FileT: TypeAlias = str | bytes | io.IOBase

__all__ = (
    'PartialEmoji',
    'Emoji',
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

    EMOJI_REGEX = re.compile(r"<(?P<a>a)?:(?P<name>[a-zA-Z0-9\-_]):(?P<id>\d{16,23})>")

    id: int | None
    name: str | None
    animated: bool

    def __init__(self, *, data: payloads.PartialEmoji | payloads.Emoji):
        self.id = try_snowflake(data.get('id'))
        self.name = data.get('name')
        self.animated = data.get('animated', False)

    def __str__(self) -> str:
        if self.id is None:
            assert isinstance(self.name, str)
            return self.name
        if self.animated:
            return f"<a:{self.name}:{self.id}>"
        return f"<:{self.name}:{self.id}>"

    __repr__ = generate_repr(('id', 'name', 'animated',))

    def _to_data(self) -> payloads.PartialEmoji:
        d: payloads.PartialEmoji = {}
        if self.id:
            d["id"] = str(self.id)
        if self.name:
            d["name"] = self.name
        if self.animated:
            d["animated"] = self.animated
        return d

    @cached_slot_property('_cs_asset')
    def asset(self) -> Asset | None:
        if self.id is None:
            return None
        return Asset.from_emoji(self)

    @overload
    @classmethod
    def from_str(cls, value: None) -> None:
        ...

    @overload
    @classmethod
    def from_str(cls, value: str | PartialEmoji) -> PartialEmoji:
        ...

    @classmethod
    def from_str(cls, value: str | PartialEmoji | None) -> PartialEmoji | None:
        """
        Transform a string into an emoji object.

        Parameters
        ----------
        value : str | novus.PartialEmoji | None
            The emoji you want converted. Can either be a Discord-style emoji
            string, a unicode emoji, or a ":smile:" style emoji via its name.
            If an emoji object is provided, then it is returned unchanged. If
            ``None`` is provided, it is returned as is.

        Returns
        -------
        novus.PartialEmoji | None
            The converted emoji, if a value was provided.

        Raises
        ------
        ValueError
            If the given value wasn't convertable to an emoji.
        """

        # Just a lil basic check
        if value is None:
            return None
        if isinstance(value, PartialEmoji):
            return value
        if " " in value:
            raise ValueError("Failed to convert %s to an emoji" % value)

        # Discord emoji
        if value.startswith("<"):
            match = cls.EMOJI_REGEX.search(value)
            if match is None:
                raise ValueError("Failed to convert %s to an emoji" % value)
            return PartialEmoji(data={
                "id": match.group("id"),
                "name": match.group("name"),
                "animated": bool(match.group("a")),
            })

        # Unicode emoji
        elif emoji.is_emoji(value):
            return PartialEmoji(data={
                "id": None,
                "name": value,
                "animated": False,
            })

        # ":thumbs_up:" style emoji
        converted = emoji.emojize(value, language="alias")
        if converted != value:
            return PartialEmoji(data={
                "id": None,
                "name": converted,
                "animated": False,
            })

        raise ValueError("Failed to convert %s to an emoji" % value)


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
        'state',
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

    id: int | None
    name: str | None
    animated: bool
    role_ids: list[int]
    requires_colons: bool
    managed: bool
    available: bool
    guild: Guild | amix.GuildAPIMixin | None

    def __init__(
            self,
            *,
            state: HTTPConnection,
            data: payloads.PartialEmoji | payloads.Emoji,
            guild_id: int | None = None,
            guild: Guild | None = None):
        self.state = state
        super().__init__(data=data)
        self.role_ids = [
            try_snowflake(i)
            for i in data.get('roles', [])
        ]
        self.requires_colons = data.get('require_colons', True)
        self.managed = data.get('managed', False)
        self.available = data.get('available', True)
        if guild:
            self.guild = guild
        elif guild_id:
            self.guild = self.state.cache.get_guild(guild_id)
        else:
            self.guild = None
