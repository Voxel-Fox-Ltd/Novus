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

from datetime import datetime as dt
from typing import TYPE_CHECKING, Any, TypeAlias

from ....utils import MISSING, try_id, try_object

if TYPE_CHECKING:
    import io

    from ... import GuildBan, GuildMember
    from ...abc import OauthStateSnowflake, Snowflake, StateSnowflake

    FileT: TypeAlias = str | bytes | io.IOBase


class GuildUserAPI:

    async def fetch_me(self: StateSnowflake) -> GuildMember:
        """
        Get the member object associated with the current guild and the current
        connection.

        .. note:: Only usable via Oauth with the ``guilds.members.read`` scope.

        .. seealso:: :func:`novus.GuildMember.fetch_me`

        Returns
        -------
        novus.GuildMember
            The member object for the current user.
        """

        member = await self.state.user.get_current_user_guild_member(self.id)
        member.guild = self
        return member

    async def leave(self: StateSnowflake) -> None:
        """
        Leave the current guild.
        """

        await self.state.user.leave_guild(self.id)

    async def fetch_member(self: StateSnowflake, member_id: int, /) -> GuildMember:
        """
        Get a member from the guild.

        .. seealso:: :func:`novus.GuildMember.fetch`

        Parameters
        ----------
        member_id : int
            The ID of the member you want to get.

        Returns
        -------
        novus.GuildMember
            The member object for the given user.
        """

        member = await self.state.guild.get_guild_member(self.id, member_id)
        member.guild = self
        return member

    async def fetch_members(
            self: StateSnowflake,
            *,
            limit: int = 1,
            after: int = 0) -> list[GuildMember]:
        """
        Get a list of members for the guild.

        .. note::

            This endpoint is restricted according to whether the
            ``GUILD_MEMBERS`` privileged intent is enabled for your application.

        .. note::

            This endpoint can return a maximum of 1000 members per request.

        Parameters
        ----------
        limit : int
            The number of guild members you want in the response payload.
        after : int
            The snowflake to get guild members after.

        Returns
        -------
        list[novus.GuildMember]
            A list of members from the guild.
        """

        members = await self.state.guild.get_guild_members(
            self.id,
            limit=limit,
            after=after,
        )
        for m in members:
            m.guild = self
        return members

    async def search_members(
            self: StateSnowflake,
            *,
            query: str,
            limit: int = 1) -> list[GuildMember]:
        """
        Get a list of members for the guild whose username of nickname starts
        with the provided string.

        .. note::

            This endpoint can return a maximum of 1000 members per request.

        Parameters
        ----------
        query : str
            the query string to match usernames and nicknames agains.
        limit : int
            The number of guild members you want in the response payload.

        Returns
        -------
        list[novus.GuildMember]
            A list of members from the guild.
        """

        members = await self.state.guild.search_guild_members(
            self.id,
            query=query,
            limit=limit,
        )
        for m in members:
            m.guild = self
        return members

    async def add_member(
            self: OauthStateSnowflake,
            user_id: int,
            access_token: str,
            *,
            nick: str = MISSING,
            mute: bool = MISSING,
            deaf: bool = MISSING) -> GuildMember | None:
        """
        Add a member to the guild.

        .. note::

            This requires an Oauth access token, and the provided user ID must
            be the same one that matches the account.

        Parameters
        ----------
        user_id : int
            The ID of the user that you want to add.
        access_token : str
            The access token with the ``guilds.join`` scope to the bot's
            application for the user you want to add to the guild.
        nick : str
            The nickname youy want to set the user to.
        mute : bool
            Whether the user is muted in voice channels.
        deaf : bool
            Whether the user is deafened in voice channels.

        Returns
        -------
        novus.GuildMember | None
            The member for the user that was added to the guild, or ``None``
            if the user was already present.
        """

        params: dict[str, Any] = {
            "access_token": access_token,
        }

        if nick is not MISSING:
            params["nick"] = nick
        if mute is not MISSING:
            params["mute"] = mute
        if deaf is not MISSING:
            params["deaf"] = deaf

        member = await self.state.guild.add_guild_member(
            self.id,
            user_id,
            **params,
        )
        if member:
            member.guild = self  # pyright: ignore  # Assigned an Oauth state
        return member

    async def edit_member(
            self: StateSnowflake,
            user: int | Snowflake,
            *,
            reason: str | None = None,
            nick: str | None = MISSING,
            roles: list[int | Snowflake] = MISSING,
            mute: bool = MISSING,
            deaf: bool = MISSING,
            voice_channel: int | Snowflake | None = MISSING,
            timeout_until: dt | None = MISSING) -> GuildMember:
        """
        Edit a guild member.

        .. seealso:: :func:`novus.GuildMember.edit`

        Parameters
        ----------
        user : int | novus.abc.Snowflake
            The ID of the user you want to edit.
        nick : str | None
            The nickname you want to set for the user.
        roles : list[int | novus.abc.Snowflake]
            A list of roles that you want the user to have.
        mute : bool
            Whether or not the user is muted in voice channels. Will error if
            the user is not currently in a voice channel.
        deaf : bool
            Whether or not the user is deafened in voice channels. Will error
            if the user is not currently in a voice channel.
        voice_channel : int | novus.abc.Snowflake | None
            The voice channel that the user is in.
        timeout_until : datetime.datetime | None
            When the user's timeout should expire (up to 28 days in the
            future).
        """

        update: dict[str, Any] = {}

        if nick is not MISSING:
            update["nick"] = nick
        if roles is not MISSING:
            update["roles"] = [try_object(r) for r in roles]
        if mute is not MISSING:
            update["mute"] = mute
        if deaf is not MISSING:
            update["deaf"] = deaf
        if voice_channel is not MISSING:
            update["channel"] = try_object(voice_channel)
        if timeout_until is not MISSING:
            update["communication_disabled_until"] = timeout_until

        member = await self.state.guild.modify_guild_member(
            self.id,
            try_id(user),
            reason=reason,
            **update,
        )
        member.guild = self
        return member

    async def add_member_role(
            self: StateSnowflake,
            user: int | Snowflake,
            role: int | Snowflake,
            *,
            reason: str | None = None) -> None:
        """
        Add a role to a user.

        Requires the ``MANAGE_ROLES`` permission.

        .. seealso:: :func:`novus.GuildMember.add_role`

        Parameters
        ----------
        user : int | novus.abc.Snowflake
            The user you want to add the role to.
        role : int | novus.abc.Snowflake
            The role you want to add.
        reason : str | None
            The reason shown in the audit log.
        """

        await self.state.guild.add_guild_member_role(
            self.id,
            try_id(user),
            try_id(role),
            reason=reason,
        )

    async def remove_member_role(
            self: StateSnowflake,
            user: int | Snowflake,
            role: int | Snowflake,
            *,
            reason: str | None = None) -> None:
        """
        Remove a role from a member.

        Requires the ``MANAGE_ROLES`` permission.

        .. seealso:: :func:`novus.GuildMember.remove_role`

        Parameters
        ----------
        user : int | novus.abc.Snowflake
            The user you want to add the role to.
        role : int | novus.abc.Snowflake
            The ID of the role you want to add.
        reason : str | None
            The reason shown in the audit log.
        """

        await self.state.guild.remove_guild_member_role(
            self.id,
            try_id(user),
            try_id(role),
            reason=reason,
        )

    async def kick(
            self: StateSnowflake,
            user: int | Snowflake,
            *,
            reason: str | None = None) -> None:
        """
        Remove a user from the guild.

        Requires the ``KICK_MEMBERS`` permission.

        Parameters
        ----------
        user : int | novus.abc.Snowflake
            The user you want to remove.
        reason : str | None
            The reason to be shown in the audit log.
        """

        await self.state.guild.remove_guild_member(
            self.id,
            try_id(user),
            reason=reason,
        )

    async def fetch_bans(
            self: StateSnowflake,
            *,
            limit: int = 1_000,
            before: int | None = None,
            after: int | None = None) -> list[GuildBan]:
        """
        Get a list of bans from the guild.

        Parameters
        ----------
        limit : str
            The number of bans to get.
        before : int | None
            The snowflake to search around.
        after : int | None
            The snowflake to search around.

        Returns
        -------
        list[novus.model.GuildBan]
            A list of bans from the guild.
        """

        update: dict[str, Any] = {
            "limit": limit,
        }

        if before is not None:
            update['before'] = before
        if after is not None:
            update['after'] = after

        return await self.state.guild.get_guild_bans(
            self.id,
            **update,
        )

    async def fetch_ban(
            self: StateSnowflake,
            user: int | Snowflake) -> GuildBan:
        """
        Get an individual user's ban.

        Parameters
        ----------
        user : int | novus.abc.Snowflake
            The user whose ban you want to get.

        Returns
        -------
        novus.GuildBan
            The ban for the user.
        """

        return await self.state.guild.get_guild_ban(
            self.id,
            try_id(user),
        )

    async def ban(
            self: StateSnowflake,
            user: int | Snowflake,
            *,
            reason: str | None = None,
            delete_message_seconds: int = MISSING) -> None:
        """
        Ban a user from the guild.

        .. seealso:: :func:`novus.GuildMember.ban`

        Parameters
        ----------
        user : int | novus.abc.Snowflake
            The user who you want to ban.
        delete_message_seconds : int
            The number of seconds of messages you want to delete.
        reason : str | None
            The reason to be shown in the audit log.
        """

        updates: dict[str, Any] = {}

        if delete_message_seconds is not MISSING:
            updates['delete_message_seconds'] = delete_message_seconds

        await self.state.guild.create_guild_ban(
            self.id,
            try_id(user),
            reason=reason,
            **updates
        )
        return

    async def unban(
            self: StateSnowflake,
            user: int | Snowflake,
            *,
            reason: str | None = None) -> None:
        """
        Remove a user's ban

        Parameters
        ----------
        user : int | novus.abc.Snowflake
            The user who you want to ban.
        reason : str | None
            The reason to be shown in the audit log.
        """

        await self.state.guild.remove_guild_ban(
            self.id,
            try_id(user),
            reason=reason,
        )
