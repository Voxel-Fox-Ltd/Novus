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

from ...utils import MISSING, try_id

if TYPE_CHECKING:
    from ...api import HTTPConnection
    from ..abc import Snowflake, StateSnowflakeWithGuild
    from ..file import File
    from ..sticker import Sticker

__all__ = (
    'StickerAPIMixin',
)


class StickerAPIMixin:

    id: int
    state: HTTPConnection

    @classmethod
    async def create(
            cls,
            state: HTTPConnection,
            guild: int | Snowflake,
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
            guild: int | Snowflake,
            id: int) -> Sticker:
        """
        Get an instance of a guild sticker from the API.

        .. seealso:: :func:`novus.Guild.fetch_sticker`

        Parameters
        ----------
        state : novus.HTTPConnection
            The API connection.
        guild : int | novus.abc.Snowflake
            The ID associated with the guild where the sticker resides.
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
            guild: int | Snowflake) -> list[Sticker]:
        """
        Get an instance of a guild sticker from the API.

        .. seealso:: :func:`novus.Guild.fetch_all_stickers`

        Parameters
        ----------
        state : novus.HTTPConnection
            The API connection.
        guild : int | novus.abc.Snowflake
            The ID associated with the guild where the stickers reside.

        Returns
        -------
        list[novus.Sticker]
            The retrieved sticker instances.
        """

        return await state.sticker.list_guild_stickers(
            try_id(guild),
        )

    async def edit(
            self: StateSnowflakeWithGuild,
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
            self: StateSnowflakeWithGuild,
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
