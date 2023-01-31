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
from typing import TYPE_CHECKING, Any, NoReturn, TypeAlias, overload

from ...enums import ChannelType
from ...utils import MISSING, try_id, try_object

if TYPE_CHECKING:
    import io

    from ...api import HTTPConnection
    from ...enums import (
        AuditLogEventType,
        AutoModerationEventType,
        AutoModerationTriggerType,
        ContentFilterLevel,
        Locale,
        NotificationLevel,
        VerificationLevel,
    )
    from ...flags import Permissions, SystemChannelFlags
    from ..abc import OauthStateSnowflake, Snowflake, StateSnowflake
    from ..audit_log import AuditLog
    from ..auto_moderation import (
        AutoModerationAction,
        AutoModerationRule,
        AutoModerationTriggerMetadata,
    )
    from ..channel import Channel, ForumTag, GuildTextChannel, PermissionOverwrite, Thread
    from ..emoji import Emoji, Reaction
    from ..guild import Guild, GuildBan
    from ..invite import Invite
    from ..role import Role
    from ..user import GuildMember

    FileT: TypeAlias = str | bytes | io.IOBase


class GuildAPIMixin:

    # Guild API methods

    @classmethod
    async def create(cls, state: HTTPConnection, *, name: str) -> Guild:
        """
        Create a guild.

        Parameters
        ----------
        state : novus.HTTPConnection
            The API connection to create the entity with.
        name : str
            The name for the guild that you want to create.

        Returns
        -------
        novus.Guild
            The created guild.
        """

        return await state.guild.create_guild(name=name)

    @classmethod
    async def fetch(cls, state: HTTPConnection, guild: int | Snowflake) -> Guild:
        """
        Get an instance of a guild from the API. Unlike the gateway's
        ``GUILD_CREATE`` payload, this method does not return members,
        channels, or voice states.

        Parameters
        ----------
        state : HTTPConnection
            The API connection.
        guild : int | novus.abc.Snowflake
            A reference to the guild that you want to fetch.

        Returns
        -------
        novus.Guild
            The guild associated with the given ID.
        """

        return await state.guild.get_guild(try_id(guild))

    async def fetch_preview(self: StateSnowflake) -> NoReturn:
        raise NotImplementedError()

    async def edit(
            self: StateSnowflake,
            *,
            name: str = MISSING,
            verification_level: VerificationLevel | None = MISSING,
            default_message_notifications: NotificationLevel | None = MISSING,
            explicit_content_filter: ContentFilterLevel | None = MISSING,
            afk_channel: int | Snowflake | None = MISSING,
            icon: FileT | None = MISSING,
            owner: int | Snowflake = MISSING,
            splash: FileT | None = MISSING,
            discovery_splash: FileT | None = MISSING,
            banner: FileT | None = MISSING,
            system_channel: int | Snowflake | None = MISSING,
            system_channel_flags: SystemChannelFlags | None = MISSING,
            rules_channel: int | Snowflake | None = MISSING,
            preferred_locale: Locale | None = MISSING,
            public_updates_channel: int | Snowflake = MISSING,
            features: list[str] = MISSING,
            description: str | None = MISSING,
            premium_progress_bar_enabled: bool = MISSING,
            reason: str | None = None) -> Guild:
        """
        Edit the guild parameters.

        .. note::

            The updated guild is not immediately put into cache - the bot
            waits for the guild update notification to be sent over the
            gateway before updating (which will not happen if you don't have
            the correct gateway intents).

        Parameters
        ----------
        name : str
            The name you want to set the guild to.
        verification_level : novus.guild.VerificationLevel | None
            The verification level you want to set the guild to.
        default_message_notifications : novus.guild.NotificationLevel | None
            The default message notification level you want to set the guild to.
        explicit_content_filter : novus.guild.ContentFilterLevel | None
            The content filter level you want to set the guild to.
        afk_channel : int | novus.abc.Snowflake | None
            The channel you want to set as the guild's AFK channel.
        icon : str | bytes | io.IOBase | None
            The icon that you want to set for the guild. Can be its bytes, a
            file path, or a file object.
        owner : int | novus.abc.Snowflake
            The person you want to set as owner of the guild. Can only be run
            if the current user is the existing owner.
        splash : str | bytes | io.IOBase | None
            The splash that you want to set for the guild. Can be its bytes, a
            file path, or a file object.
        discovery_splash : str | bytes | io.IOBase | None
            The discovery splash for the guild. Can be its bytes, a file path,
            or a file object.
        banner : str | bytes | io.IOBase | None
            The banner for the guild. Can be its bytes, a file path, or a file
            object.
        system_channel : int | novus.abc.Snowflake | None
            The system channel you want to set for the guild.
        system_channel_flags : novus.guild.SystemChannelFlags | None
            The system channel flags you want to set.
        rules_channel : int | novus.abc.Snowflake | None
            The channel you want to set as the rules channel.
        preferred_locale : Locale | None
            The locale you want to set as the guild's preferred.
        public_updates_channel : int | novus.abc.Snowflake
            The channel you want to set as the updates channel for the guild.
        features : list[str]
            A list of features for the guild.
        description : str | None
            A description for the guild.
        premium_progress_bar_enabled : bool
            Whether or not to enable the premium progress bar for the guild.
        reason : str | None
            A reason for modifying the guild (shown in the audit log).

        Returns
        -------
        novus.Guild
            The updated guild.
        """

        updates: dict[str, Any] = {}

        if name is not None:
            updates["name"] = name
        if verification_level is not None:
            updates["verification_level"] = verification_level
        if default_message_notifications is not None:
            updates["default_message_notifications"] = default_message_notifications
        if explicit_content_filter is not None:
            updates["explicit_content_filter"] = explicit_content_filter
        if afk_channel is not None:
            updates["afk_channel"] = try_object(afk_channel)
        if icon is not None:
            updates["icon"] = icon
        if owner is not None:
            updates["owner"] = try_object(owner)
        if splash is not None:
            updates["splash"] = splash
        if discovery_splash is not None:
            updates["discovery_splash"] = discovery_splash
        if banner is not None:
            updates["banner"] = banner
        if system_channel is not None:
            updates["system_channel"] = try_object(system_channel)
        if system_channel_flags is not None:
            updates["system_channel_flags"] = system_channel_flags
        if rules_channel is not None:
            updates["rules_channel"] = try_object(rules_channel)
        if preferred_locale is not None:
            updates["preferred_locale"] = preferred_locale
        if public_updates_channel is not None:
            updates["public_updates_channel"] = try_object(public_updates_channel)
        if features is not None:
            updates["features"] = features
        if description is not None:
            updates["description"] = description
        if premium_progress_bar_enabled is not None:
            updates["premium_progress_bar_enabled"] = premium_progress_bar_enabled

        return await self._state.guild.modify_guild(
            self.id,
            reason=reason,
            **updates,
        )

    async def delete(self: StateSnowflake) -> None:
        """
        Delete the current guild permanently. You must be the owner of the
        guild to run this successfully.
        """

        await self._state.guild.delete_guild(self.id)
        return None

    async def fetch_channels(self: StateSnowflake) -> list[Channel]:
        """
        Fetch all of the channels from a guild.

        Returns
        -------
        list[novus.model.Channel]
            A list of channels from the guild.
        """

        channels = await self._state.guild.get_guild_channels(self.id)
        for c in channels:
            c.guild = self
        return channels

    @overload
    async def create_channel(
            self: StateSnowflake,
            *,
            name: str,
            type: ChannelType = ChannelType.guild_text,
            bitrate: int = ...,
            user_limit: int = ...,
            rate_limit_per_user: int = ...,
            position: int = ...,
            permission_overwrites: list[PermissionOverwrite] = ...,
            parent: int | Snowflake = ...,
            nsfw: bool = ...,
            default_auto_archive_duration: int = ...,
            default_reaction_emoji: Reaction = ...,
            available_tags: list[ForumTag] = ...) -> GuildTextChannel:
        ...

    @overload
    async def create_channel(
            self: StateSnowflake,
            *,
            name: str,
            type: ChannelType = ChannelType.private_thread,
            bitrate: int = ...,
            user_limit: int = ...,
            rate_limit_per_user: int = ...,
            position: int = ...,
            permission_overwrites: list[PermissionOverwrite] = ...,
            parent: int | Snowflake = ...,
            nsfw: bool = ...,
            default_auto_archive_duration: int = ...,
            default_reaction_emoji: Reaction = ...,
            available_tags: list[ForumTag] = ...) -> Thread:
        ...

    @overload
    async def create_channel(
            self: StateSnowflake,
            *,
            name: str,
            type: ChannelType = ChannelType.public_thread,
            bitrate: int = ...,
            user_limit: int = ...,
            rate_limit_per_user: int = ...,
            position: int = ...,
            permission_overwrites: list[PermissionOverwrite] = ...,
            parent: int | Snowflake = ...,
            nsfw: bool = ...,
            default_auto_archive_duration: int = ...,
            default_reaction_emoji: Reaction = ...,
            available_tags: list[ForumTag] = ...) -> Thread:
        ...

    async def create_channel(
            self: StateSnowflake,
            *,
            name: str,
            type: ChannelType = MISSING,
            bitrate: int = MISSING,
            user_limit: int = MISSING,
            rate_limit_per_user: int = MISSING,
            position: int = MISSING,
            permission_overwrites: list[PermissionOverwrite] = MISSING,
            parent: int | Snowflake = MISSING,
            nsfw: bool = MISSING,
            default_auto_archive_duration: int = MISSING,
            default_reaction_emoji: Reaction = MISSING,
            available_tags: list[ForumTag] = MISSING) -> Channel:
        """
        Create a channel within the guild.

        Parameters
        ----------
        name : str
            The name of the channel.
        type : novus.ChannelType
            The type of the channel.
        bitrate : int
            The bitrate for the channel. Only for use with voice channels.
        user_limit : int
            The user limit for the channel. Only for use with voice channels.
        rate_limit_per_user : int
            The slowmode seconds on the channel.
        position : int
            The channel position.
        permission_overwrites : list[novus.PermissionOverwrite]
            A list of permission overwrites for the channel.
        parent : int | novus.abc.Snowflake
            A parent object for the channel.
        nsfw : bool
            Whether or not the channel will be set to NSFW.
        default_auto_archive_duration : int
            The default duration that clients use (in minutes) to automatically
            archive the thread after recent activity. Only for use with forum
            channels.
        default_reaction_emoji : Reaction
            The default add reaction button to be shown on threads. Only for
            use with forum channels.
        available_tags : list[ForumTag]
            The tags available for threads. Only for use with forum channels.

        Returns
        -------
        novus.model.Channel
            The created channel.
        """

        update: dict[str, Any] = {}

        if name is not MISSING:
            update["name"] = name
        if type is not MISSING:
            update["type"] = type
        if bitrate is not MISSING:
            update["bitrate"] = bitrate
        if user_limit is not MISSING:
            update["user_limit"] = user_limit
        if rate_limit_per_user is not MISSING:
            update["rate_limit_per_user"] = rate_limit_per_user
        if position is not MISSING:
            update["position"] = position
        if permission_overwrites is not MISSING:
            update["permission_overwrites"] = permission_overwrites
        if parent is not MISSING:
            update["parent"] = try_object(parent)
        if nsfw is not MISSING:
            update["nsfw"] = nsfw
        if default_auto_archive_duration is not MISSING:
            update["default_auto_archive_duration"] = default_auto_archive_duration
        if default_reaction_emoji is not MISSING:
            update["default_reaction_emoji"] = default_reaction_emoji
        if available_tags is not MISSING:
            update["available_tags"] = available_tags

        channel = await self._state.guild.create_guild_channel(self.id, **update)
        channel.guild = self
        return channel

    async def move_channels(self: StateSnowflake) -> None:
        raise NotImplementedError()

    async def fetch_active_threads(self: StateSnowflake) -> list[Thread]:
        """
        Get the active threads from inside the guild.

        Returns
        -------
        list[novus.model.Thread]
            A list of threads.
        """

        threads = await self._state.guild.get_active_guild_threads(self.id)
        for t in threads:
            t.guild = self
        return threads

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

        member = await self._state.guild.get_guild_member(self.id, member_id)
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

        members = await self._state.guild.get_guild_members(
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

        members = await self._state.guild.search_guild_members(
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

        member = await self._state.guild.add_guild_member(
            self.id,
            user_id,
            **params,
        )
        if member:
            member.guild = self  # type: ignore  # Assigned an Oauth state
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

        member = await self._state.guild.modify_guild_member(
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

        await self._state.guild.add_guild_member_role(
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

        await self._state.guild.add_guild_member_role(
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

        await self._state.guild.remove_guild_member(
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

        return await self._state.guild.get_guild_bans(
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

        return await self._state.guild.get_guild_ban(
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

        await self._state.guild.create_guild_ban(
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

        await self._state.guild.remove_guild_ban(
            self.id,
            try_id(user),
            reason=reason,
        )

    async def fetch_roles(self: StateSnowflake) -> list[Role]:
        """
        Get a list of roles for the guild.

        Returns
        -------
        list[novus.model.Role]
            A list of roles in the guild.
        """

        roles = await self._state.guild.get_guild_roles(self.id)
        for r in roles:
            r.guild = self
        return roles

    async def create_role(
            self: StateSnowflake,
            *,
            reason: str | None = None,
            name: str = MISSING,
            permissions: Permissions = MISSING,
            color: int = MISSING,
            hoist: bool = MISSING,
            icon: FileT = MISSING,
            unicode_emoji: str = MISSING,
            mentionable: bool = MISSING) -> Role:
        """
        Create a role within the guild.

        Parameters
        ----------
        name : str
            The name of the role.
        permissions : novus.Permissions
            The permissions attached to the role.
        color : int
            The color of the role.
        hoist : bool
            Whether the role is displayed seperately in the sidebar.
        icon : str | bytes | io.IOBase | None
            The role icon image. Only usable if the guild has the
            ``ROLE_ICONS`` feature.
        unicode_emoji : str
            The role's unicode emoji. Only usable if the guild has the
            ``ROLE_ICONS`` feature.
        mentionable : bool
            Whether the role should be mentionable.
        reason : str | None
            The reason to be shown in the audit log.
        """

        update: dict[str, Any] = {}

        if name is not MISSING:
            update['name'] = name
        if permissions is not MISSING:
            update['permissions'] = permissions
        if color is not MISSING:
            update['color'] = color
        if hoist is not MISSING:
            update['hoist'] = hoist
        if icon is not MISSING:
            update['icon'] = icon
        if unicode_emoji is not MISSING:
            update['unicode_emoji'] = unicode_emoji
        if mentionable is not MISSING:
            update['mentionable'] = mentionable

        role = await self._state.guild.create_guild_role(
            self.id,
            reason=reason,
            **update,
        )
        role.guild = self
        return role

    async def move_roles(self) -> NoReturn:
        raise NotImplementedError()

    async def edit_role(
            self: StateSnowflake,
            role_id: int,
            *,
            reason: str | None = None,
            name: str = MISSING,
            permissions: Permissions = MISSING,
            color: int = MISSING,
            hoist: bool = MISSING,
            icon: FileT = MISSING,
            unicode_emoji: str = MISSING,
            mentionable: bool = MISSING) -> Role:
        """
        Edit a role.

        Parameters
        ----------
        role_id : int
            The ID of the role to be edited.
        name : str
            The new name of the role.
        permissions : novus.Permissions
            The permissions to be applied to the role.
        color : int
            The color to apply to the role.
        hoist : bool
            If the role should be displayed seperately in the sidebar.
        icon : str | bytes | io.IOBase | None
            The role's icon image. Only usable if the guild has the
            ``ROLE_ICONS`` feature.
        unicode_emoji : str
            The role's unicode emoji. Only usable if the guild has the
            ``ROLE_ICONS`` feature.
        mentionable : bool
            If the role is mentionable.
        reason : str | None
            The reason to be shown in the audit log.
        """

        update: dict[str, Any] = {}

        if name is not MISSING:
            update['name'] = name
        if permissions is not MISSING:
            update['permissions'] = permissions
        if color is not MISSING:
            update['color'] = color
        if hoist is not MISSING:
            update['hoist'] = hoist
        if icon is not MISSING:
            update['icon'] = icon
        if unicode_emoji is not MISSING:
            update['unicode_emoji'] = unicode_emoji
        if mentionable is not MISSING:
            update['mentionable'] = mentionable

        role = await self._state.guild.modify_guild_role(
            self.id,
            role_id,
            reason=reason,
            **update,
        )
        role.guild = self
        return role

    async def edit_mfa_level(self) -> NoReturn:
        raise NotImplementedError()

    async def delete_role(
            self: StateSnowflake,
            role: int | Snowflake,
            *,
            reason: str | None = None) -> None:
        """
        A role to delete.

        Parameters
        ----------
        role : int | novus.abc.Snowflake
            The ID of the role to delete.
        reason : str | None
            The reason to be shown in the audit log.
        """

        await self._state.guild.delete_guild_role(
            self.id,
            try_id(role),
            reason=reason,
        )
        return None

    async def fetch_prune_count(self) -> NoReturn:
        raise NotImplementedError()

    async def prune(self) -> NoReturn:
        raise NotImplementedError()

    async def fetch_voice_regions(self) -> NoReturn:
        raise NotImplementedError()

    async def fetch_invites(self: StateSnowflake) -> list[Invite]:
        """
        Get the invites for the guild.

        Requires the ``MANAGE_GUILD`` permission.

        Returns
        -------
        list[novus.Invite]
            A list of invites.
        """

        return await self._state.guild.get_guild_invites(self.id)

    async def fetch_integrations(self) -> NoReturn:
        raise NotImplementedError()

    async def delete_integration(self) -> NoReturn:
        raise NotImplementedError()

    async def fetch_widget(self) -> NoReturn:
        raise NotImplementedError()

    async def edit_widget(self) -> NoReturn:
        raise NotImplementedError()

    async def edit_vainity_url(self) -> NoReturn:
        raise NotImplementedError()

    async def edit_widget_image(self) -> NoReturn:
        raise NotImplementedError()

    async def fetch_welcome_screen(self) -> NoReturn:
        raise NotImplementedError()

    async def edit_welcome_screen(self) -> NoReturn:
        raise NotImplementedError()

    async def edit_member_voice_state(self) -> NoReturn:
        raise NotImplementedError()

    async def edit_my_voice_state(self) -> NoReturn:
        raise NotImplementedError()

    # Emoji API endpoints

    async def fetch_emojis(self: StateSnowflake) -> list[Emoji]:
        """
        List all of the emojis for the guild.

        .. seealso:: :func:`novus.Emoji.fetch_all_for_guild`

        Returns
        -------
        list[novus.Emoji]
            A list of the guild's emojis.
        """

        emojis = await self._state.emoji.list_guild_emojis(self.id)
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

        return await self._state.emoji.create_guild_emoji(
            self.id,
            reason=reason,
            **{
                "name": name,
                "image": image,
                "roles": roles or list(),
            },
        )

    # User API methods

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

        member = await self._state.user.get_current_user_guild_member(self.id)
        member.guild = self
        return member

    async def leave(self: StateSnowflake) -> None:
        """
        Leave the current guild.
        """

        await self._state.user.leave_guild(self.id)

    # Audit log API methods

    async def fetch_audit_logs(
            self: StateSnowflake,
            *,
            user_id: int | None = None,
            action_type: AuditLogEventType | None = None,
            before: int | None = None,
            after: int | None = None,
            limit: int = 50) -> AuditLog:
        """
        Get the audit logs for the guild.

        Parameters
        ----------
        user_id: int | None
            The ID of the moderator you want to to filter by.
        action_type: AuditLogEventType | None
            The ID of an action to filter by.
        before: int | None
            The snowflake before which to get entries.
        after: int | None
            The snowflake after which to get entries.
        limit: int
            The number of entries to get. Max 100, defaults to 50.

        Returns
        -------
        novus.AuditLog
            The audit log for the guild.
        """

        return await self._state.audit_log.get_guild_audit_log(
            self.id,
            user_id=user_id,
            action_type=action_type,
            before=before,
            after=after,
            limit=limit,
        )

    # Auto moderation API methods

    async def fetch_auto_moderation_rules(
            self: StateSnowflake) -> list[AutoModerationRule]:
        """
        Get the auto moderation rules for this guild.

        Returns
        -------
        list[novus.AutoModerationRule]
            A list of the auto moderation rules for the guild.
        """

        return await (
            self._state.auto_moderation
            .list_auto_moderation_rules_for_guild(self.id)
        )

    async def create_auto_moderation_rule(
            self: StateSnowflake,
            *,
            reason: str | None = None,
            name: str,
            event_type: AutoModerationEventType,
            trigger_type: AutoModerationTriggerType,
            actions: list[AutoModerationAction],
            trigger_metadata: AutoModerationTriggerMetadata | None = None,
            enabled: bool = False,
            exempt_roles: list[int | Snowflake] | None = None,
            exempt_channels: list[int | Snowflake] | None = None) -> AutoModerationRule:
        """
        Create a new auto moderation rule.

        Parameters
        ----------
        name : str
            The new name for the role.
        event_type : novus.AutoModerationEventType
            The event type.
        trigger_type : novus.AutoModerationTriggerType
            The trigger type.
        actions : list[novus.AutoModerationAction]
            The actions to be taken on trigger.
        trigger_metadata : novus.AutoModerationTriggerMetadata | None
            The trigger metadata.
        enabled : bool
            Whether the rule is enabled or not.
        exempt_roles : list[int | novus.abc.Snowflake] | None
            A list of roles that are exempt from the rule.
        exempt_channels : list[int | novus.abc.Snowflake] | None
            A list of channels that are exempt from the rule.
        reason : str | None
            The reason shown in the audit log.

        Returns
        -------
        novus.AutoModerationRule
            The created rule.
        """

        updates: dict[str, Any] = {}
        updates["name"] = name
        updates["event_type"] = event_type
        updates["trigger_type"] = trigger_type
        updates["trigger_metadata"] = trigger_metadata
        if actions:
            updates["actions"] = actions
        updates["enabled"] = enabled
        if exempt_roles:
            updates["exempt_roles"] = [try_object(i) for i in exempt_roles]
        if exempt_channels:
            updates["exempt_channels"] = [try_object(i) for i in exempt_channels]

        return await self._state.auto_moderation.create_auto_moderation_rule(
            self.id,
            reason=reason,
            **updates,
        )
