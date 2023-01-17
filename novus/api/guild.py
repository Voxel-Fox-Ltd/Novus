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

from typing import TYPE_CHECKING

from ._route import Route
from .. import models

if TYPE_CHECKING:
    from ._http import HTTPConnection
    from .. import payloads

__all__ = (
    'GuildHTTPConnection',
)


class GuildHTTPConnection:

    def __init__(self, parent: HTTPConnection):
        self.parent = parent

    async def get_guild(
            self,
            id: int,
            /,
            with_counts: bool = False) -> models.Guild:
        """
        Get a guild from the API.
        """

        route = Route(
            "GET",
            "/guilds/{guild_id}",
            guild_id=id,
        )
        data: payloads.Guild = await self.parent.request(
            route,
            params={
                "with_counts": (
                    "true" if with_counts
                    else "false"
                ),
            }
        )
        return models.Guild(
            state=self.parent,
            data=data,
        )

    async def get_guild_preview(
            self,
            id: int, /) -> models.GuildPreview:
        """
        Get a guild preview from the API.
        """

        route = Route(
            "GET",
            "/guilds/{guild_id}/preview",
            guild_id=id,
        )
        data: payloads.GuildPreview = await self.parent.request(
            route,
        )
        return models.GuildPreview(
            data=data,
        )

    async def modify_guild(
            self,
            id: int,
            /,
            reason: str | None = None,
            **kwargs) -> models.Guild:
        """
        Edit the guild.
        """

        post_data = {
            **self.parent._get_type_kwargs(
                (
                    'name',
                    'region',
                    'afk_timeout',
                    'description',
                    'premium_progress_bar_enabled',
                ),
                kwargs,
            ),
            **self.parent._get_enum_kwargs(
                (
                    'verification_level',
                    'default_message_notifications',
                    'explicit_content_filter',
                    'preferred_locale',
                    'system_channel_flags',
                ),
                kwargs,
            ),
            **self.parent._get_snowflake_kwargs(
                (
                    ('afk_channel_id', 'afk_channel',),
                    ('owner_id', 'owner',),
                    ('system_channel_id', 'system_channel',),
                    ('rules_channel_id', 'rules_channel',),
                    ('public_updates_channel_id', 'public_updates_channel',),
                ),
                kwargs,
            ),
            **self.parent._get_image_kwargs(
                (
                    'icon',
                    'splash',
                    'discovery_splash',
                    'banner',
                ),
                kwargs,
            ),
            **kwargs,
        }
        route = Route(
            "PATCH",
            "/guilds/{guild_id}",
            guild_id=id,
        )
        data: payloads.Guild = await self.parent.request(
            route,
            reason=reason,
            data=post_data,
        )
        return models.Guild(
            state=self.parent,
            data=data,
        )

    async def delete_guild(
            self,
            id: int,
            /) -> None:
        """
        Delete the guild.
        """

        route = Route(
            "DELETE",
            "/guilds/{guild_id}",
            guild_id=id,
        )
        await self.parent.request(route)
        return None
