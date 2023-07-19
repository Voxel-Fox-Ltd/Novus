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

from typing import TYPE_CHECKING, Any, NoReturn

from ..models import (
    Guild,
    GuildBan,
    GuildMember,
    GuildPreview,
    Invite,
    Role,
    Thread,
    User,
)
from ..models.channel import GuildChannel, channel_builder
from ._route import Route

if TYPE_CHECKING:
    from .. import payloads
    from ._http import HTTPConnection

__all__ = (
    'GuildHTTPConnection',
)


class GuildHTTPConnection:

    def __init__(self, parent: HTTPConnection):
        self.parent = parent

    async def create_guild(
            self,
            **kwargs: Any) -> Guild:
        """
        Create a guild.
        """

        route = Route(
            "POST",
            "/guilds",
        )
        data: payloads.Guild = await self.parent.request(
            route,
            data=kwargs,
        )
        return Guild(
            state=self.parent,
            data=data,
        )

    async def get_guild(
            self,
            guild_id: int,
            /,
            with_counts: bool = False) -> Guild:
        """
        Get a guild.
        """

        route = Route(
            "GET",
            "/guilds/{guild_id}",
            guild_id=guild_id,
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
        return Guild(
            state=self.parent,
            data=data,
        )

    async def get_guild_preview(
            self,
            guild_id: int, /) -> GuildPreview:
        """
        Get a guild preview.
        """

        route = Route(
            "GET",
            "/guilds/{guild_id}/preview",
            guild_id=guild_id,
        )
        data: payloads.GuildPreview = await self.parent.request(
            route,
        )
        return GuildPreview(
            state=self.parent,
            data=data,
        )

    async def modify_guild(
            self,
            guild_id: int,
            /,
            *,
            reason: str | None = None,
            **kwargs: Any) -> Guild:
        """
        Edit a guild.
        """

        post_data = self.parent._get_kwargs(
            {
                "type": (
                    'name',
                    'region',
                    'afk_timeout',
                    'description',
                    'premium_progress_bar_enabled',
                ),
                "enum": (
                    'verification_level',
                    'default_message_notifications',
                    'explicit_content_filter',
                    'preferred_locale',
                    'system_channel_flags',
                ),
                "snowflake": (
                    ('afk_channel_id', 'afk_channel',),
                    ('owner_id', 'owner',),
                    ('system_channel_id', 'system_channel',),
                    ('rules_channel_id', 'rules_channel',),
                    ('public_updates_channel_id', 'public_updates_channel',),
                ),
                "image": (
                    'icon',
                    'splash',
                    'discovery_splash',
                    'banner',
                ),
            },
            kwargs,
        )
        route = Route(
            "PATCH",
            "/guilds/{guild_id}",
            guild_id=guild_id,
        )
        data: payloads.Guild = await self.parent.request(
            route,
            reason=reason,
            data=post_data,
        )
        return Guild(
            state=self.parent,
            data=data,
        )

    async def delete_guild(
            self,
            guild_id: int, /) -> None:
        """
        Delete a guild.
        """

        route = Route(
            "DELETE",
            "/guilds/{guild_id}",
            guild_id=guild_id,
        )
        await self.parent.request(route)
        return None

    async def get_guild_channels(
            self,
            guild_id: int, /) -> list[GuildChannel]:
        """
        Get guild channels.
        """

        route = Route(
            "GET",
            "/guilds/{guild_id}/channels",
            guild_id=guild_id,
        )
        data: list[payloads.Channel] = await self.parent.request(
            route,
        )
        return [
            channel_builder(state=self.parent, data=d)
            for d in data
        ]  # pyright: ignore

    async def create_guild_channel(
            self,
            guild_id: int,
            /,
            *,
            reason: str | None = None,
            **kwargs: Any) -> GuildChannel:
        """
        Create a guild channel.
        """

        route = Route(
            "POST",
            "/guilds/{guild_id}/channels",
            guild_id=guild_id,
        )
        post_data = self.parent._get_kwargs(
            {
                "type": (
                    "name",
                    "bitrate",
                    "user_limit",
                    "rate_limit_per_user",
                    "position",
                    "nsfw",
                    "default_auto_archive_duration",
                ),
                "enum": (
                    "type",
                ),
                "snowflake": (
                    ("parent_id", "parent",),
                ),
                "object": (
                    "permission_overwrites",
                    "default_reaction_emoji",
                    "available_tags",
                ),
            },
            kwargs,
        )
        data: payloads.Channel = await self.parent.request(
            route,
            reason=reason,
            data=post_data,
        )
        return channel_builder(state=self.parent, data=data)

    async def move_guild_channels(self, guild_id: int) -> NoReturn:
        raise NotImplementedError()

    async def get_active_guild_threads(self, guild_id: int) -> list[Thread]:
        """
        Get the threads from the guild.
        """

        route = Route(
            "GET",
            "/guilds/{guild_id}/threads/active",
            guild_id=guild_id,
        )
        data: list[payloads.Channel] = await self.parent.request(
            route,
        )
        return [
            Thread(state=self.parent, data=d)
            for d in data
        ]

    async def get_guild_member(
            self,
            guild_id: int,
            member_id: int) -> GuildMember:
        """
        Get a guild member.
        """

        route = Route(
            "GET",
            "/guilds/{guild_id}/members/{member_id}",
            guild_id=guild_id,
            member_id=member_id,
        )
        data: payloads.GuildMember = await self.parent.request(
            route,
        )
        return GuildMember(state=self.parent, data=data)

    async def get_guild_members(
            self,
            guild_id: int,
            *,
            limit: int = 1,
            after: int = 0) -> list[GuildMember]:
        """
        Get a guild member.
        """

        route = Route(
            "GET",
            "/guilds/{guild_id}/members",
            guild_id=guild_id,
        )
        data: list[payloads.GuildMember] = await self.parent.request(
            route,
            params={
                "limit": limit,
                "after": after,
            }
        )
        return [
            GuildMember(state=self.parent, data=d)
            for d in data
        ]

    async def search_guild_members(
            self,
            guild_id: int,
            *,
            query: str,
            limit: int = 1) -> list[GuildMember]:
        """
        Get a guild member.
        """

        route = Route(
            "GET",
            "/guilds/{guild_id}/members/search",
            guild_id=guild_id,
        )
        data: list[payloads.GuildMember] = await self.parent.request(
            route,
            params={
                "query": query,
                "limit": limit,
            }
        )
        return [
            GuildMember(state=self.parent, data=d)
            for d in data
        ]

    async def add_guild_member(
            self,
            guild_id: int,
            user_id: int,
            *,
            access_token: str,
            **kwargs: Any) -> GuildMember | None:
        """
        Add a member to the guild. Only works if you have a valid Oauth2 access
        token with the guild.join scope.
        """

        route = Route(
            "PUT",
            "/guilds/{guild_id}/members/{user_id}",
            guild_id=guild_id,
            user_id=user_id,
        )
        post_data = self.parent._get_kwargs(
            {
                "type": (
                    "access_token",
                    "nick",
                    "mute",
                    "deaf",
                ),
            },
            {**kwargs, "access_token": access_token},
        )
        data: payloads.GuildMember | None = await self.parent.request(
            route,
            data=post_data,
        )
        if data:
            return GuildMember(state=self.parent, data=data)
        return None

    async def modify_guild_member(
            self,
            guild_id: int,
            user_id: int,
            /,
            *,
            reason: str | None = None,
            **kwargs: Any) -> GuildMember:
        """
        Update a guild member.
        """

        route = Route(
            "PATCH",
            "/guilds/{guild_id}/members/{user_id}",
            guild_id=guild_id,
            user_id=user_id,
        )
        post_data = self.parent._get_kwargs(
            {
                "type": (
                    "nick",
                    "mute",
                    "deaf",
                ),
                "snowflake": (
                    "roles",
                    ("channel_id", "channel",),
                ),
                "timestamp": (
                    "communication_disabled_until",
                ),
            },
            kwargs,
        )
        data: payloads.GuildMember = await self.parent.request(
            route,
            reason=reason,
            data=post_data,
        )
        return GuildMember(state=self.parent, data=data, guild_id=guild_id)

    async def modify_current_guild_member(self, guild_id: int) -> NoReturn:
        raise NotImplementedError()

    async def add_guild_member_role(
            self,
            guild_id: int,
            user_id: int,
            role_id: int,
            /,
            *,
            reason: str | None = None) -> None:
        """
        Add a role to a guild member.
        """

        route = Route(
            "PUT",
            "/guilds/{guild_id}/members/{user_id}/roles/{role_id}",
            guild_id=guild_id,
            user_id=user_id,
            role_id=role_id,
        )
        await self.parent.request(
            route,
            reason=reason,
        )
        return

    async def remove_guild_member_role(
            self,
            guild_id: int,
            user_id: int,
            role_id: int,
            /,
            *,
            reason: str | None = None) -> None:
        """
        Remove a role from a guild member.
        """

        route = Route(
            "DELETE",
            "/guilds/{guild_id}/members/{user_id}/roles/{role_id}",
            guild_id=guild_id,
            user_id=user_id,
            role_id=role_id,
        )
        await self.parent.request(
            route,
            reason=reason,
        )
        return

    async def remove_guild_member(
            self,
            guild_id: int,
            user_id: int,
            /,
            *,
            reason: str | None = None) -> None:
        """
        Remove a member from the guild.
        """

        route = Route(
            "DELETE",
            "/guilds/{guild_id}/members/{user_id}",
            guild_id=guild_id,
            user_id=user_id,
        )
        await self.parent.request(
            route,
            reason=reason,
        )
        return

    async def get_guild_bans(
            self,
            guild_id: int,
            /,
            *,
            limit: int | None = None,
            before: int | None = None,
            after: int | None = None) -> list[GuildBan]:
        """
        Get the bans from a guild.
        """

        route = Route(
            "GET",
            "/guilds/{guild_id}/bans",
            guild_id=guild_id,
        )
        params: dict[str, Any] = {}
        if limit is not None:
            params['limit'] = limit
        if before is not None:
            params['before'] = before
        if after is not None:
            params['after'] = after
        data: list[dict] = await self.parent.request(
            route,
            params=params,
        )
        return [
            GuildBan(
                reason=d.get('reason'),
                user=User(state=self.parent, data=d['user'])
            )
            for d in data
        ]

    async def get_guild_ban(
            self,
            guild_id: int,
            user_id: int, /) -> GuildBan:
        """
        Get a ban for a particular member.
        """

        route = Route(
            "GET",
            "/guilds/{guild_id}/bans/{user_id}",
            guild_id=guild_id,
            user_id=user_id,
        )
        data: dict = await self.parent.request(
            route,
        )
        return GuildBan(
            reason=data.get('reason'),
            user=User(state=self.parent, data=data['user'])
        )

    async def create_guild_ban(
            self,
            guild_id: int,
            user_id: int,
            /,
            *,
            reason: str | None = None,
            **kwargs: Any) -> None:
        """
        Ban a user.
        """

        route = Route(
            "PUT",
            "/guilds/{guild_id}/bans/{user_id}",
            guild_id=guild_id,
            user_id=user_id,
        )
        post_data: dict[str, Any] = {}
        self.parent._get_kwargs(
            {
                "type": (
                    "delete_message_seconds",
                ),
            },
            kwargs,
        )
        await self.parent.request(
            route,
            reason=reason,
            data=post_data,
        )
        return

    async def remove_guild_ban(
            self,
            guild_id: int,
            user_id: int,
            /,
            *,
            reason: str | None = None) -> None:
        """
        Unban a user.
        """

        route = Route(
            "DELETE",
            "/guilds/{guild_id}/bans/{user_id}",
            guild_id=guild_id,
            user_id=user_id,
        )
        await self.parent.request(
            route,
            reason=reason,
        )
        return

    async def get_guild_roles(self, guild_id: int) -> list[Role]:
        """
        List the roles for the guild.
        """

        route = Route(
            "GET",
            "/guilds/{guild_id}/roles",
            guild_id=guild_id,
        )
        data: list[payloads.Role] = await self.parent.request(
            route,
        )
        return [
            Role(
                state=self.parent,
                data=d,
                guild_id=guild_id,
            )
            for d in data
        ]

    async def create_guild_role(
            self,
            guild_id: int,
            *,
            reason: str | None = None,
            **kwargs: Any) -> Role:
        """
        Create a role in the guild.
        """

        route = Route(
            "POST",
            "/guilds/{guild_id}/roles",
            guild_id=guild_id,
        )
        post_data: dict[str, Any] = {}
        self.parent._get_kwargs(
            {
                "type": (
                    "name",
                    "color",
                    "hoist",
                    "unicode_emoji",
                    "mentionable",
                ),
                "image": (
                    "icon",
                ),
                "flags": (
                    "permissions",
                ),
            },
            kwargs,
        )
        data: payloads.Role = await self.parent.request(
            route,
            reason=reason,
            data=post_data,
        )
        return Role(state=self.parent, data=data, guild_id=guild_id)

    async def modify_guild_role_positions(self, _: int) -> NoReturn:
        raise NotImplementedError()

    async def modify_guild_role(
            self,
            guild_id: int,
            role_id: int,
            /,
            *,
            reason: str | None = None,
            **kwargs: Any) -> Role:
        """
        Edit a guild role.
        """

        route = Route(
            "PATCH",
            "/guilds/{guild_id}/roles/{role_id}",
            guild_id=guild_id,
            role_id=role_id,
        )
        post_data: dict[str, Any] = {}
        self.parent._get_kwargs(
            {
                "type": (
                    "name",
                    "color",
                    "hoist",
                    "unicode_emoji",
                    "mentionable",
                ),
                "image": (
                    "icon",
                ),
                "flags": (
                    "permissions",
                ),
            },
            kwargs,
        )
        data: payloads.Role = await self.parent.request(
            route,
            reason=reason,
            data=post_data,
        )
        return Role(state=self.parent, data=data, guild_id=guild_id)

    async def modify_guild_mfa_level(self, _: int) -> NoReturn:
        raise NotImplementedError()

    async def delete_guild_role(
            self,
            guild_id: int,
            role_id: int,
            /,
            *,
            reason: str | None = None) -> None:
        """
        Delete a guild role.
        """

        route = Route(
            "DELETE",
            "/guilds/{guild_id}/roles/{role_id}",
            guild_id=guild_id,
            role_id=role_id,
        )
        await self.parent.request(
            route,
            reason=reason,
        )
        return None

    async def get_guild_prune_count(self, _: int) -> NoReturn:
        raise NotImplementedError()

    async def begin_guild_prune(self, _: int) -> NoReturn:
        raise NotImplementedError()

    async def get_guild_voice_regions(self, _: int) -> NoReturn:
        raise NotImplementedError()

    async def get_guild_invites(
            self,
            guild_id: int, /) -> list[Invite]:
        """
        Get the invites for a guild.
        """

        route = Route(
            "GET",
            "/guilds/{guild_id}/invites",
            guild_id=guild_id,
        )
        data: list[payloads.InviteWithMetadata] = await self.parent.request(
            route,
        )
        return [
            Invite(state=self.parent, data=d)
            for d in data
        ]

    async def get_guild_integrations(self, _: int, /) -> NoReturn:
        raise NotImplementedError()

    async def delete_guild_integration(self, _: int, /) -> NoReturn:
        raise NotImplementedError()

    async def get_guild_widget_settings(self, _: int, /) -> NoReturn:
        raise NotImplementedError()

    async def modify_guild_widget_settings(self, _: int, /) -> NoReturn:
        raise NotImplementedError()

    async def modify_guild_vainity_url(self, _: int, /) -> NoReturn:
        raise NotImplementedError()

    async def modify_guild_widget_image(self, _: int, /) -> NoReturn:
        raise NotImplementedError()

    async def get_guild_welcome_screen(self, _: int, /) -> NoReturn:
        raise NotImplementedError()

    async def modify_guild_welcome_screen(self, _: int, /) -> NoReturn:
        raise NotImplementedError()

    async def modify_current_user_voice_state(self, _: int, /) -> NoReturn:
        raise NotImplementedError()

    async def modify_user_voice_state(self, _: int, /) -> NoReturn:
        raise NotImplementedError()
