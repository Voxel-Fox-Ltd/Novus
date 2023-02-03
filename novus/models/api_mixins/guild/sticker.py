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

if TYPE_CHECKING:
    import io

    from ... import File, Sticker
    from ...abc import StateSnowflake

    FileT: TypeAlias = str | bytes | io.IOBase


class GuildStickerAPI:

    async def fetch_sticker(self: StateSnowflake, id: int) -> Sticker:
        """
        Get an individual sticker associated with the guild via its ID.

        .. seealso:: :func:`novus.Sticker.fetch`

        Parameters
        ----------
        id : str
            The ID of the sticker.

        Returns
        -------
        novus.Sticker
            The associated sticker instance.
        """

        sticker = await self._state.sticker.get_guild_sticker(self.id, id)
        sticker.guild = self
        return sticker

    async def fetch_all_stickers(self: StateSnowflake) -> list[Sticker]:
        """
        List all stickers associated with the guild.

        .. seealso:: :func:`novus.Sticker.fetch_all_for_guild`

        Returns
        -------
        list[novus.Sticker]
            The stickers associated with the guild.
        """

        stickers = await self._state.sticker.list_guild_stickers(self.id)
        for s in stickers:
            s.guild = self
        return stickers

    async def create_sticker(
            self: StateSnowflake,
            *,
            reason: str | None = None,
            name: str,
            description: str | None = None,
            tags: str,
            image: File) -> Sticker:
        """
        Create a new sticker.

        .. seealso:: :func:`novus.Sticker.create`

        Parameters
        ----------
        name : str
            The name of the sticker.
        tags : str
            Autocomplete/suggestion tags for the sitcker.
        description : str | None
            Description of the sticker.
        image : novus.File
            The image to be uploaded. All aside from the data itself is
            discarded - the name and description are taken from the other
            parameters.
        reason : str | None
            The reason shown in the audit log.

        Reutrns
        -------
        novus.Sticker
            The created sticker instance.
        """

        return await self._state.sticker.create_guild_sticker(
            self.id,
            reason=reason,
            **{
                "name": name,
                "description": description,
                "tags": tags,
                "file": image.data,
            },
        )
