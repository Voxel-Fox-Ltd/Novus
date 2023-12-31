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

from typing import TYPE_CHECKING, Any
from typing_extensions import Self

from ..enums import StickerFormat
from ..utils import MISSING, cached_slot_property, try_id, try_snowflake
from .abc import Hashable
from .asset import Asset

if TYPE_CHECKING:
    from .. import payloads
    from ..api import HTTPConnection
    from . import abc
    from .file import File
    from .guild import BaseGuild

__all__ = (
    'Sticker',
)


class Sticker(Hashable):
    """
    A model for a sticker.

    Attributes
    ----------
    id : int
        The ID of the sticker.
    pack_id : int | None
        The ID of the pack that the sticker came in, for standard stickers.
    name : str
        The name of the sticker.
    description : str
        The description of the sticker.
    format_type : novus.StickerFormat
        The format for the sticker.
    available : bool
        Whether or not the sticker can be used. May be ``False`` due to loss of
        nitro boosts.
    asset : novus.Asset
        The asset associated with the sticker.
    guild : novus.Guild | None
        The guild (or a data container for the ID) that the emoji came from.
        May be ``None`` if the sticker does not come from a guild.
    """

    __slots__ = (
        'state',
        'id',
        'pack_id',
        'name',
        'description',
        # 'type',
        'format_type',
        'available',
        'guild',

        '_cs_asset',
    )

    id: int
    pack_id: int | None
    name: str
    description: str | None
    format_type: StickerFormat
    available: bool
    guild: BaseGuild | None

    def __init__(
            self,
            *,
            state: HTTPConnection,
            data: payloads.Sticker | payloads.PartialSticker):
        self.state = state
        self.id: int = try_snowflake(data['id'])
        self.pack_id: int | None = try_snowflake(data.get('pack_id'))
        self.name: str = data['name']
        self.description: str | None = data.get('description', None)
        # self.type: StickerType = StickerType(data['type'])
        self.format_type: StickerFormat = StickerFormat(data['format_type'])
        self.available: bool = data.get('available', True)
        self.guild = None
        guild_id = data.get("guild_id")
        if guild_id:
            self.guild = self.state.cache.get_guild(guild_id)

    @cached_slot_property('_cs_asset')
    def asset(self) -> Asset:
        return Asset.from_sticker(self)

    def _update(self, data: payloads.Sticker) -> Self:
        self.name = data["name"]
        self.description = data["description"]
        return self

    # API methods

    @classmethod
    async def create(
            cls,
            state: HTTPConnection,
            guild: int | abc.Snowflake,
            *,
            reason: str | None = None,
            name: str,
            description: str | None = None,
            tags: str,
            image: File) -> Sticker:
        """
        Create a sticker within a guild.

        Parameters
        ----------
        state : novus.HTTPConnection
            The API connection.
        guild : int | novus.abc.Snowflake
            The guild you want to create the sticker within.
        name : str
            The name of the sticker.
        tags : str
            Autocomplete/suggestion tags for the sitcker.
        description : str | None
            Description of the sticker.
        image : novus.File
            The image to be uploaded. All aside from the data itself is
            discarded.
        reason : str | None
            The reason shown in the audit log.

        Reutrns
        -------
        novus.Sticker
            The created sticker instance.
        """

        return await state.sticker.create_guild_sticker(
            try_id(guild),
            reason=reason,
            **{
                "name": name,
                "description": description,
                "tags": tags,
                "file": image.data,
            },
        )

    @classmethod
    async def fetch(
            cls,
            state: HTTPConnection,
            guild: int | abc.Snowflake,
            id: int) -> Sticker:
        """
        Get an instance of a guild sticker from the API.

        .. seealso:: :func:`novus.Guild.fetch_sticker`

        Parameters
        ----------
        state : novus.HTTPConnection
            The API connection.
        guild : int | novus.abc.Snowflake
            The guild where the sticker resides.
        id: int
            The ID of the sticker you want to get.

        Returns
        -------
        novus.Sticker
            The retrieved sticker instance.
        """

        return await state.sticker.get_guild_sticker(
            try_id(guild),
            id,
        )

    @classmethod
    async def fetch_all_for_guild(
            cls,
            state: HTTPConnection,
            guild: int | abc.Snowflake) -> list[Sticker]:
        """
        Get an instance of a guild sticker from the API.

        .. seealso:: :func:`novus.Guild.fetch_all_stickers`

        Parameters
        ----------
        state : novus.HTTPConnection
            The API connection.
        guild : int | novus.abc.Snowflake
            The guild where the stickers reside.

        Returns
        -------
        list[novus.Sticker]
            The retrieved sticker instances.
        """

        return await state.sticker.list_guild_stickers(try_id(guild))

    async def edit(
            self: abc.StateSnowflakeWithGuild,
            *,
            reason: str | None = None,
            name: str = MISSING,
            description: str | None = MISSING,
            tags: str = MISSING
            ) -> Sticker:
        """
        Edit a sticker from a guild.

        Parameters
        ----------
        name : str
            The new name for the sticker.
        description : str | None
            The new description for the sticker.
        tags : str
            The new tags for the sticker.
        reason : str | None
            The reason shown in the audit log.

        Returns
        -------
        novus.Sticker
            The updated sticker instance.
        """

        updated: dict[str, Any] = {}

        if name is not MISSING:
            updated["name"] = name
        if description is not MISSING:
            updated["description"] = description
        if tags is not MISSING:
            updated["tags"] = tags

        return await self.state.sticker.modify_guild_sticker(
            self.guild.id,
            self.id,
            reason=reason,
            **updated,
        )

    async def delete(
            self: abc.StateSnowflakeWithGuild,
            *,
            reason: str | None = None) -> Sticker:
        """
        Delete a guild sticker.

        Parameters
        ----------
        reason : str | None
            The reason shown in the audit log.

        Returns
        -------
        novus.Sticker
            The updated sticker instance.
        """

        return await self.state.sticker.modify_guild_sticker(
            self.guild.id,
            self.id,
            reason=reason,
        )
