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

from typing import TYPE_CHECKING, Any

from ..models import DMChannel, GuildMember, OauthGuild, User
from ..models.channel import channel_builder
from ._route import Route

if TYPE_CHECKING:
    from .. import payloads
    from ._http import HTTPConnection

__all__ = (
    'UserHTTPConnection',
)


class UserHTTPConnection:

    def __init__(self, parent: HTTPConnection):
        self.parent = parent

    async def get_current_user(
            self) -> User:
        """
        Get the current user from the API.
        """

        route = Route(
            "GET",
            "/users/@me",
        )
        data: payloads.User = await self.parent.request(
            route,
        )
        return User(
            state=self.parent,
            data=data,
        )

    async def get_user(
            self,
            user_id: int) -> User:
        """
        Get a user from the API.
        """

        route = Route(
            "GET",
            "/users/{user_id}",
            user_id=user_id,
        )
        data: payloads.User = await self.parent.request(
            route,
        )
        return User(
            state=self.parent,
            data=data,
        )

    async def modify_current_user(
            self,
            **kwargs: Any) -> User:
        """
        Edit the current user.
        """

        post_data = self.parent._get_kwargs(
            {
                "type": (
                    'username',
                ),
                "image": (
                    'avatar',
                ),
            },
            kwargs,
        )
        route = Route(
            "PATCH",
            "/users/@me",
        )
        data: payloads.User = await self.parent.request(
            route,
            data=post_data,
        )
        return User(
            state=self.parent,
            data=data,
        )

    async def get_current_user_guilds(
            self,
            *,
            before: int | None = None,
            after: int | None = None,
            limit: int = 200) -> list[OauthGuild]:
        """
        Get a list of guilds from the oauth user.
        """

        params: dict[str, Any] = {}
        if before is not None:
            params['before'] = before
        if after is not None:
            params['after'] = after
        if limit is not None:
            params['limit'] = limit

        route = Route(
            "GET",
            "/users/@me/guilds",
        )
        data: list[payloads.Guild] = await self.parent.request(
            route,
            params=params,
        )
        return [
            OauthGuild(
                state=self.parent,
                data=d,
            )
            for d in data
        ]

    async def get_current_user_guild_member(
            self,
            guild_id: int) -> GuildMember:
        """
        Get the current user's guild member object.
        """

        route = Route(
            "GET",
            "/users/@me/guild/{guild_id}/member",
            guild_id=guild_id,
        )
        data: payloads.GuildMember = await self.parent.request(
            route,
        )
        return GuildMember(state=self.parent, data=data)

    async def leave_guild(
            self,
            guild_id: int) -> None:
        """
        Leave a given guild.
        """

        route = Route(
            "DELETE",
            "/users/@me/guild/{guild_id}",
            guild_id=guild_id,
        )
        await self.parent.request(route)

    async def create_dm(
            self,
            recipient_id: int) -> DMChannel:
        """
        Create a DM with a user.
        """

        route = Route(
            "POST",
            "/users/@me/channels",
        )
        json = {
            "recipient_id": recipient_id,
        }
        data: payloads.Channel = await self.parent.request(
            route,
            data=json,
        )
        created = channel_builder(state=self.parent, data=data)
        if not isinstance(created, DMChannel):
            raise TypeError("Created channel was not a DM channel.")
        return created

    async def get_user_connections(
            self) -> Any:
        """
        Get a list of connection objects from the API.
        """

        raise NotImplementedError()

    async def get_user_application_role_connection(
            self,
            application_id: int) -> Any:
        """
        Get the current role connection for an application.
        """

        raise NotImplementedError()

    async def update_user_application_role_connection(
            self,
            application_id: int) -> Any:
        """
        Update a role connection for an application.
        """

        raise NotImplementedError()
