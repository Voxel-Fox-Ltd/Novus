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
from typing import TYPE_CHECKING, Any, overload

import emoji

from ..utils import (
    MISSING,
    cached_slot_property,
    generate_repr,
    try_id,
    try_object,
    try_snowflake,
)
from .abc import Hashable
from .asset import Asset

if TYPE_CHECKING:
    from .. import payloads
    from ..api import HTTPConnection
    from ..utils.types import FileT
    from . import abc
    from .guild import BaseGuild

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


class Emoji(PartialEmoji):
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
    guild: BaseGuild | None

    def __init__(
            self,
            *,
            state: HTTPConnection,
            data: payloads.PartialEmoji | payloads.Emoji,
            guild_id: int | None = None,
            guild: BaseGuild | None = None):
        self.state = state
        super().__init__(data=data)
        self.role_ids = try_snowflake(data.get("roles", list()))  # pyright: ignore
        self.requires_colons = data.get('require_colons', True)
        self.managed = data.get('managed', False)
        self.available = data.get('available', True)
        if guild:
            self.guild = guild
        elif guild_id:
            self.guild = self.state.cache.get_guild(guild_id)
        else:
            self.guild = None

    # API methods

    @classmethod
    async def create(
            cls,
            state: HTTPConnection,
            guild: int | abc.Snowflake,
            *,
            name: str,
            image: FileT,
            roles: list[int | abc.Snowflake] | None = None,
            reason: str | None = None) -> Emoji:
        """
        Create an emoji within a guild.

        Parameters
        ----------
        state : novus.HTTPConnection
            The API connection to create the entity with.
        guild : int | novus.abc.Snowflake
            The guild that the emoji is to be created in.
        name : str
            The name of the emoji you want to add.
        image : str | bytes | io.IOBase
            The image that you want to add.
        roles : list[int | novus.abc.Snowflake] | None
            A list of roles that are allowed to use the emoji.
        reason : str | None
            A reason you're adding the emoji to be shown in the audit log.

        Returns
        -------
        novus.Emoji
            The newly created emoji.
        """

        return await state.emoji.create_guild_emoji(
            try_id(guild),
            reason=reason,
            **{
                "name": name,
                "image": image,
                "roles": [try_object(i) for i in roles or ()],
            },
        )

    @classmethod
    async def fetch(
            cls,
            state: HTTPConnection,
            guild_id: int,
            emoji_id: int) -> Emoji:
        """
        Fetch a specific emoji by its ID from the API.

        .. seealso:: :func:`novus.Guild.fetch_emoji`

        Parameters
        ----------
        guild_id : int
            The ID of the guild that you want to fetch from.
        emoji_id : int
            The ID of the emoji that you want to fetch.

        Returns
        -------
        novus.Emoji
            The emoji from the API.
        """

        return await state.emoji.get_emoji(guild_id, emoji_id)

    @classmethod
    async def fetch_all_for_guild(
            cls,
            state: HTTPConnection,
            guild: int | abc.Snowflake) -> list[Emoji]:
        """
        Fetch all of the emojis from a guild.

        .. seealso:: :func:`novus.Guild.fetch_emojis`

        Parameters
        ----------
        guild : int | novus.abc.Snowflake
            The guild that you want to fetch from.

        Returns
        -------
        list[novus.Emoji]
            The list of emojis that the guild has.
        """

        return await state.emoji.list_guild_emojis(try_id(guild))

    async def delete(
            self: abc.StateSnowflakeWithGuild,
            *,
            reason: str | None = None) -> None:
        """
        Delete this emoji.

        Parameters
        ----------
        reason : str | None
            The reason shown in the audit log.
        """

        await self.state.emoji.delete_guild_emoji(
            self.guild.id,
            self.id,
            reason=reason,
        )
        return None

    async def edit(
            self: abc.StateSnowflakeWithGuild,
            *,
            reason: str | None = None,
            name: str = MISSING,
            roles: list[int | abc.Snowflake] = MISSING) -> Emoji:
        """
        Edit the current emoji.

        Parameters
        ----------
        name : str
            The new name for the emoji.
        roles : list[int | novus.abc.Snowflake]
            A list of the roles that can use the emoji.
        reason : str | None
            The reason shown in the audit log.

        Returns
        -------
        novus.Emoji
            The newly updated emoji.
        """

        update: dict[str, Any] = {}

        if name is not MISSING:
            update["name"] = name
        if roles is not MISSING:
            update["roles"] = [try_object(i) for i in roles]

        return await self.state.emoji.modify_guild_emoji(
            self.guild.id,
            self.id,
            reason=reason,
            **update,
        )
