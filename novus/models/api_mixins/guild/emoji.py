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

    from ... import Emoji
    from ...abc import Snowflake, StateSnowflake

    FileT: TypeAlias = str | bytes | io.IOBase


class GuildEmojiAPI:

    async def fetch_emoji(self: StateSnowflake, id: int) -> Emoji:
        """
        List all of the emojis for the guild.

        .. seealso:: :func:`novus.Emoji.fetch`

        Returns
        -------
        list[novus.Emoji]
            A list of the guild's emojis.
        """

        emoji = await self.state.emoji.get_emoji(self.id, id)
        emoji.guild = self
        return emoji

    async def fetch_all_emojis(self: StateSnowflake) -> list[Emoji]:
        """
        List all of the emojis for the guild.

        .. seealso:: :func:`novus.Emoji.fetch_all_for_guild`

        Returns
        -------
        list[novus.Emoji]
            A list of the guild's emojis.
        """

        emojis = await self.state.emoji.list_guild_emojis(self.id)
        for e in emojis:
            e.guild = self
        return emojis

    async def create_emoji(
            self: StateSnowflake,
            *,
            name: str,
            image: FileT,
            roles: list[Snowflake] | None = None,
            reason: str | None = None) -> Emoji:
        """
        Create an emoji within a guild.

        Parameters
        ----------
        name : str
            The name of the emoji you want to add.
        image : str | bytes | io.IOBase
            The image that you want to add.
        roles : list[int | novus.abc.Snowflake] | None
            A list of roles that are allowed to use the emoji.
        reason : str | None
            A reason you're adding the emoji.

        Returns
        -------
        novus.Emoji
            The newly created emoji.
        """

        return await self.state.emoji.create_guild_emoji(
            self.id,
            reason=reason,
            **{
                "name": name,
                "image": image,
                "roles": roles or list(),
            },
        )
