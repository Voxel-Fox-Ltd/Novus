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

from datetime import datetime as dt
from typing import TYPE_CHECKING, Any

from ...utils import MISSING, try_id, try_object

if TYPE_CHECKING:
    from ...api import HTTPConnection
    from ..abc import Snowflake, StateSnowflakeWithGuild
    from ..guild import OauthGuild
    from ..user import GuildMember, User


class UserAPIMixin:
    @classmethod
    async def fetch(cls, state: HTTPConnection, user_id: int) -> User:
        """
        Get an instance of a user from the API.

        Parameters
        ----------
        state : HTTPConnection
            The API connection.
        user_id : int
            The ID associated with the user you want to get.

        Returns
        -------
        novus.models.User
            The user associated with the given ID.
        """

        return await state.user.get_user(user_id)

    @classmethod
    async def fetch_me(cls, state: HTTPConnection) -> User:
        """
        Get the user associated with the current connection.

        Parameters
        ----------
        state : HTTPConnection
            The API connection.

        Returns
        -------
        novus.models.User
            The user associated with the given ID.
        """

        return await state.user.get_current_user()

    @classmethod
    async def fetch_my_guilds(
        cls,
        state: HTTPConnection,
        *,
        before: int | None = None,
        after: int | None = None,
        limit: int = 200,
    ) -> list[OauthGuild]:
        """
        Return a list of partial guild objects that the current user is a
        member of.

        The endpoint returns 200 guilds by default, which is the maximum number
        of guilds that a non-bot can join.

        Parameters
        ----------
        state : HTTPConnection
            The API connection.
        before: int | None
            The snowflake before which to get guilds.
        after: int | None
            The snowflake after which to get guilds.
        limit: int
            The number of guilds you want to return.

        Returns
        -------
        list[novus.models.OauthGuild]
            A list of guilds associated with the current user.
        """

        return await state.user.get_current_user_guilds(
            before=before,
            after=after,
            limit=limit,
        )


class GuildMemberAPIMixin:
    @classmethod
    async def fetch(
        cls, state: HTTPConnection, guild_id: int, member_id: int
    ) -> GuildMember:
        """
        Get an instance of a user from the API.

        .. seealso:: :func:`novus.models.Guild.fetch_member`

        Parameters
        ----------
        state : HTTPConnection
            The API connection.
        guild_id : int
            The ID associated with the guild you want to get.
        member_id : int
            The ID associated with the user you want to get.

        Returns
        -------
        novus.models.GuildMember
            The user associated with the given ID.
        """

        return await state.guild.get_guild_member(guild_id, member_id)

    @classmethod
    async def fetch_me(cls, state: HTTPConnection, guild_id: int) -> GuildMember:
        """
        Get the member object associated with the current connection and a
        given guild ID.

        .. note:: Only usable via Oauth with the ``guilds.members.read`` scope.

        .. seealso:: :func:`novus.models.Guild.fetch_me`

        Parameters
        ----------
        state : HTTPConnection
            The API connection.
        guild_id : int
            The ID associated with the guild you want to get.

        Returns
        -------
        novus.models.GuildMember
            The member within the given guild.
        """

        return await state.user.get_current_user_guild_member(guild_id)

    async def edit(
        self: StateSnowflakeWithGuild,
        *,
        reason: str | None = None,
        nick: str | None = MISSING,
        roles: list[int | Snowflake] = MISSING,
        mute: bool = MISSING,
        deaf: bool = MISSING,
        voice_channel: int | Snowflake | None = MISSING,
        timeout_until: dt | None = MISSING,
    ) -> GuildMember:
        """
        Edit a guild member.

        .. seealso:: :func:`novus.models.Guild.edit_member`

        Parameters
        ----------
        nick : str | None
            The nickname you want to set for the user.
        roles : list[novus.models.abc.Snowflake]
            A list of roles that you want the user to have.
        mute : bool
            Whether or not the user is muted in voice channels. Will error if
            the user is not currently in a voice channel.
        deaf : bool
            Whether or not the user is deafened in voice channels. Will error
            if the user is not currently in a voice channel.
        voice_channel : novus.models.abc.Snowflake | None
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

        return await self._state.guild.modify_guild_member(
            self.guild.id,
            self.id,
            reason=reason,
            **update,
        )

    async def add_role(
        self: StateSnowflakeWithGuild,
        role: int | Snowflake,
        *,
        reason: str | None = None,
    ) -> None:
        """
        Add a role to the user.

        Requires the ``MANAGE_ROLES`` permission.

        .. seealso:: :func:`novus.models.Guild.add_member_role`

        Parameters
        ----------
        role : int | novus.models.abc.Snowflake
            The role you want to add.
        reason : str | None
            The reason shown in the audit log.
        """

        await self._state.guild.add_guild_member_role(
            self.guild.id,
            self.id,
            try_id(role),
            reason=reason,
        )

    async def remove_role(
        self: StateSnowflakeWithGuild,
        role: int | Snowflake,
        *,
        reason: str | None = None,
    ) -> None:
        """
        Remove a role from the user.

        Requires the ``MANAGE_ROLES`` permission.

        .. seealso:: :func:`novus.models.Guild.remove_member_role`

        Parameters
        ----------
        role : int | novus.models.abc.Snowflake
            The role you want to remove.
        reason : str | None
            The reason shown in the audit log.
        """

        await self._state.guild.add_guild_member_role(
            self.guild.id,
            self.id,
            try_id(role),
            reason=reason,
        )

    async def kick(self: StateSnowflakeWithGuild, *, reason: str | None) -> None:
        """
        Remove a user from the guild.

        Requires the ``KICK_MEMBERS`` permission.

        .. seealso:: :func:`novus.models.Guild.kick`

        Parameters
        ----------
        reason : str | None
            The reason to be shown in the audit log.
        """

        await self._state.guild.remove_guild_member(
            self.guild.id,
            self.id,
            reason=reason,
        )

    async def ban(
        self: StateSnowflakeWithGuild,
        *,
        reason: str | None,
        delete_message_seconds: int = MISSING,
    ) -> None:
        """
        Ban a user from the guild.

        Requires the ``BAN_MEMBERS`` permission.

        .. seealso:: :func:`novus.models.Guild.ban`

        Parameters
        ----------
        delete_message_seconds : int
            The number of seconds of messages you want to delete.
        reason : str | None
            The reason to be shown in the audit log.
        """

        updates: dict[str, Any] = {}

        if delete_message_seconds is not MISSING:
            updates["delete_message_seconds"] = delete_message_seconds

        await self._state.guild.create_guild_ban(
            self.guild.id, self.id, reason=reason, **updates
        )
        return
