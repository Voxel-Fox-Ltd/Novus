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

from ..models import Emoji
from ._route import Route

if TYPE_CHECKING:
    from .. import payloads
    from ._http import HTTPConnection

__all__ = (
    'EmojiHTTPConnection',
)


class EmojiHTTPConnection:

    def __init__(self, parent: HTTPConnection):
        self.parent = parent

    async def list_guild_emojis(
            self,
            guild_id: int) -> list[Emoji]:
        """
        Get all guild emojis.
        """

        route = Route(
            "GET",
            "/guilds/{guild_id}/emojis",
            guild_id=guild_id,
        )
        data: list[payloads.Emoji] = await self.parent.request(
            route,
        )

        return [
            Emoji(
                state=self.parent,
                data=d,
                guild_id=guild_id,
            )
            for d in data
        ]

    async def get_emoji(
            self,
            guild_id: int,
            emoji_id: int) -> Emoji:
        """
        Get one guild emoji.
        """

        route = Route(
            "GET",
            "/guilds/{guild_id}/emojis/{emoji_id}",
            guild_id=guild_id,
            emoji_id=emoji_id,
        )
        data: payloads.Emoji = await self.parent.request(
            route,
        )
        return Emoji(
            state=self.parent,
            data=data,
            guild_id=guild_id,
        )

    async def create_guild_emoji(
            self,
            guild_id: int,
            /,
            *,
            reason: str | None = None,
            **kwargs: Any) -> Emoji:
        """
        Create a guild emoji.
        """

        post_data = self.parent._get_kwargs(
            {
                "type": (
                    'name',
                ),
                "snowflake": (
                    'roles',
                ),
                "image": (
                    'image',
                ),
            },
            kwargs,
        )
        route = Route(
            "POST",
            "/guilds/{guild_id}/emojis",
            guild_id=guild_id,
        )
        data: payloads.Emoji = await self.parent.request(
            route,
            reason=reason,
            data=post_data,
        )
        return Emoji(
            state=self.parent,
            data=data,
            guild_id=guild_id,
        )

    async def modify_guild_emoji(
            self,
            guild_id: int,
            emoji_id: int,
            /,
            *,
            reason: str | None = None,
            **kwargs: Any) -> Emoji:
        """
        Modify guild emoji.
        """

        post_data = self.parent._get_kwargs(
            {
                "type": (
                    'name',
                ),
                "snowflake": (
                    'roles',
                ),
            },
            kwargs,
        )
        route = Route(
            "PATCH",
            "/guilds/{guild_id}/emojis/{emoji_id}",
            guild_id=guild_id,
            emoji_id=emoji_id,
        )
        data: payloads.Emoji = await self.parent.request(
            route,
            reason=reason,
            data=post_data,
        )
        return Emoji(
            state=self.parent,
            data=data,
            guild_id=guild_id,
        )

    async def delete_guild_emoji(
            self,
            guild_id: int,
            emoji_id: int,
            /,
            *,
            reason: str | None = None) -> None:
        """
        Delete guild emoji.
        """

        route = Route(
            "DELETE",
            "/guilds/{guild_id}/emojis/{emoji_id}",
            guild_id=guild_id,
            emoji_id=emoji_id,
        )
        await self.parent.request(
            route,
            reason=reason,
        )
        return
