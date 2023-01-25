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


from ..guild import Guild
from ..object import Object
from ...utils import try_id

if TYPE_CHECKING:
    from ..abc import Snowflake, StateSnowflakeWithGuild
    from ..user import User, GuildMember
    from ..guild import OauthGuild
    from ...api import HTTPConnection


class UserAPIMixin:

    @classmethod
    async def fetch(
            cls,
            state: HTTPConnection,
            user_id: int) -> User:
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
    async def fetch_current(
            cls,
            state: HTTPConnection) -> User:
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
    async def fetch_current_guilds(
            cls,
            state: HTTPConnection,
            *,
            before: int | None = None,
            after: int | None = None,
            limit: int = 200) -> list[OauthGuild]:
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
            cls,
            state: HTTPConnection,
            guild_id: int,
            user_id: int) -> GuildMember:
        """
        Get an instance of a user from the API.

        Parameters
        ----------
        state : HTTPConnection
            The API connection.
        guild_id : int
            The ID associated with the guild you want to get.
        user_id : int
            The ID associated with the user you want to get.

        Returns
        -------
        novus.models.GuildMember
            The user associated with the given ID.
        """

        guild = Object(guild_id, state=state)
        return await Guild.fetch_member(guild, user_id)

    @classmethod
    async def fetch_current(
            cls,
            state: HTTPConnection,
            guild_id: int) -> GuildMember:
        """
        Get the member object associated with the current connection and a
        given guild ID.

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

        guild = Object(guild_id, state=state)
        return await Guild.fetch_current_member(guild)

    async def edit(
            self: StateSnowflakeWithGuild,
            *args,
            **kwargs) -> GuildMember:
        """
        Edit a guild member.

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

        guild = Object(self.guild.id, state=self._state)
        return await Guild.edit_member(guild, self.id, *args, **kwargs)

    async def add_role(
            self: StateSnowflakeWithGuild,
            role: int | Snowflake,
            *,
            reason: str | None = None) -> None:
        """
        Add a role to the user.

        Requires the ``MANAGE_ROLES`` permission.

        Parameters
        ----------
        role : int | novus.models.abc.Snowflake
            The role you want to add.
        reason : str | None
            The reason shown in the audit log.
        """

        guild = Object(self.guild.id, state=self._state)
        return await Guild.add_member_role(
            guild,
            self.id,
            try_id(role),
            reason=reason,
        )

    async def remove_role(
            self: StateSnowflakeWithGuild,
            role: int | Snowflake,
            *,
            reason: str | None = None) -> None:
        """
        Remove a role from the user.

        Requires the ``MANAGE_ROLES`` permission.

        Parameters
        ----------
        role : int | novus.models.abc.Snowflake
            The role you want to remove.
        reason : str | None
            The reason shown in the audit log.
        """

        guild = Object(self.guild.id, state=self._state)
        return await Guild.remove_member_role(
            guild,
            self.id,
            try_id(role),
            reason=reason,
        )
