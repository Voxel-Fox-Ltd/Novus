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

from typing import TYPE_CHECKING, Any, NoReturn

from ..models import Sticker
from ._route import Route

if TYPE_CHECKING:
    from .. import payloads
    from ._http import HTTPConnection

__all__ = (
    'StickerHTTPConnection',
)


class StickerHTTPConnection:

    def __init__(self, parent: HTTPConnection):
        self.parent = parent

    async def get_sticker(self, sticker_id: int) -> Sticker:
        """
        Get a sticker from the API via its ID.

        This route shouldn't really be used, but is included for completeness
        sake.
        """

        route = Route(
            "GET",
            "/stickers/{sticker_id}",
            sticker_id=sticker_id,
        )
        data: payloads.Sticker = await self.parent.request(route)
        return Sticker(state=self.parent, data=data)

    async def list_nitro_sticker_packs(self) -> NoReturn:
        raise NotImplementedError()

    async def list_guild_stickers(self, guild_id: int) -> list[Sticker]:
        """
        List the stickers within a guild.
        """

        route = Route(
            "GET",
            "/guilds/{guild_id}/stickers",
            guild_id=guild_id,
        )
        data: list[payloads.Sticker] = await self.parent.request(route)
        return [
            Sticker(state=self.parent, data=d)
            for d in data
        ]

    async def get_guild_sticker(self, guild_id: int, sticker_id: int) -> Sticker:
        """
        Get a sticker form a guild.
        """

        route = Route(
            "GET",
            "/guilds/{guild_id}/stickers/{sticker_id}",
            guild_id=guild_id,
            sticker_id=sticker_id,
        )
        data: payloads.Sticker = await self.parent.request(route)
        return Sticker(state=self.parent, data=data)

    async def create_guild_sticker(
            self,
            guild_id: int,
            *,
            reason: str | None = None,
            **kwargs: dict[str, Any]) -> Sticker:
        """
        Create a sticker within a guild.
        """

        route = Route(
            "POST",
            "/guilds/{guild_id}/stickers",
            guild_id=guild_id,
        )
        post_data = self.parent._get_kwargs(
            {
                "type": (
                    "name",
                    "description",
                    "tags",
                    "file",
                ),
            },
            kwargs,
        )
        data: payloads.Sticker = await self.parent.request(
            route,
            data=post_data,
            reason=reason,
            multipart=True,
        )
        return Sticker(state=self.parent, data=data)

    async def modify_guild_sticker(
            self,
            guild_id: int,
            sticker_id: int,
            *,
            reason: str | None = None,
            **kwargs: dict[str, Any]) -> Sticker:
        """
        Edit a sticker within a guild.
        """

        route = Route(
            "PATCH",
            "/guilds/{guild_id}/stickers/{sticker_id}",
            guild_id=guild_id,
            sticker_id=sticker_id,
        )
        post_data = self.parent._get_kwargs(
            {
                "type": (
                    "name",
                    "description",
                    "tags",
                ),
            },
            kwargs,
        )
        data: payloads.Sticker = await self.parent.request(
            route,
            data=post_data,
            reason=reason,
        )
        return Sticker(state=self.parent, data=data)

    async def delete_guild_sticker(
            self,
            guild_id: int,
            sticker_id: int,
            *,
            reason: str) -> None:
        """
        Delete a guild sticker.
        """

        route = Route(
            "DELETE",
            "/guilds/{guild_id}/stickers/{sticker_id}",
            guild_id=guild_id,
            sticker_id=sticker_id,
        )
        await self.parent.request(
            route,
            reason=reason,
        )
