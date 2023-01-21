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

from typing import TYPE_CHECKING, Any, overload, Literal, TypeAlias
from datetime import datetime as dt
from dataclasses import dataclass

from .mixins import Hashable
from .channel import Channel
from .role import Role
from .asset import Asset
from .emoji import Emoji
from .welcome_screen import WelcomeScreen
from .sticker import Sticker
from ..flags import Permissions, SystemChannelFlags
from ..enums import (
    Locale,
    VerificationLevel,
    NotificationLevel,
    ContentFilterLevel,
    MFALevel,
    PremiumTier,
    NSFWLevel,
    ChannelType,
)
from ..utils import (
    MISSING,
    try_snowflake,
    generate_repr,
    cached_slot_property,
    parse_timestamp,
)

if TYPE_CHECKING:
    import io

    from .abc import Snowflake, StateSnowflake, OauthStateSnowflake
    from .channel import (
        GuildTextChannel,
        Thread,
        PermissionOverwrite,
        ForumTag,
    )
    from .emoji import Reaction
    from .user import User, GuildMember
    from ..api import HTTPConnection, OauthHTTPConnection
    from ..payloads import (
        Guild as APIGuildPayload,
        GatewayGuild as GatewayGuildPayload,
        GuildPreview as GuildPreviewPayload,
        InviteWithMetadata as InviteMetadataPayload,
    )

    FileT: TypeAlias = str | bytes | io.IOBase

__all__ = (
    'Invite',
    'GuildBan',
    'Guild',
    'OauthGuild',
    'GuildPreview',
)


class Invite:
    """
    A model representing a guild invite.

    Attributes
    ----------
    code : str
        The code associated with the invite.
    channel : novus.models.Channel | None
        The channel that the invite leads to.
    uses : int | None
        How many times the invite has been used.
    max_uses : int | None
        The maximum number of times the invite can be used.
    max_age : int | None
        Duration (in seconds) after which the invite expires.
    temporary : bool | None
        Whether the invite only grants temporary membership.
    created_at : datetime.datetime | None
        The time that the invite was created.
    """

    def __init__(self, *, state: HTTPConnection, data: InviteMetadataPayload):
        self._state = state
        self.code = data['code']
        self.channel = None
        channel = data.get('channel')
        if channel:
            self.channel = Channel._from_data(state=self._state, data=channel)
        self.uses = data.get('uses')
        self.max_uses = data.get('max_uses')
        self.max_age = data.get('max_age')
        self.temporary = data.get('temporary')
        self.created_at = parse_timestamp(data.get('created_at'))


@dataclass
class GuildBan:
    """
    A ban object for a guild.

    .. warning::

        This object should not be created yourself, but is used to represent
        a model from the API.

    Attributes
    ----------
    reason : str | None
        The given reason that the user was banned.
    user : novus.models.User
        The user that was banned.
    """

    reason: str | None
    user: User


class GuildAPIMixin:

    @classmethod
    async def create(cls, state: HTTPConnection, *, name: str) -> Guild:
        """
        Create a guild.

        Parameters
        ----------
        name : str
            The name for the guild that you want to create.

        Returns
        -------
        novus.models.Guild
            The created guild.
        """

        return await state.guild.create_guild(name=name)

    @overload
    @classmethod
    async def fetch(cls, state: OauthHTTPConnection, guild_id: int) -> OauthGuild:
        ...

    @overload
    @classmethod
    async def fetch(cls, state: HTTPConnection, guild_id: int) -> Guild:
        ...

    @classmethod
    async def fetch(cls, state: HTTPConnection, guild_id: int) -> Guild | OauthGuild:
        """
        Get an instance of a guild from the API. Unlike the gateway's
        ``GUILD_CREATE`` payload, this method does not return members,
        channels, or voice states.

        Parameters
        ----------
        state : HTTPConnection
            The API connection.
        guild_id : int
            The ID associated with the guild you want to get.

        Returns
        -------
        novus.models.Guild
            The guild associated with the given ID.
        """

        return await state.guild.get_guild(guild_id)

    async def fetch_preview(self: StateSnowflake):
        raise NotImplementedError()

    async def edit(
            self: StateSnowflake,
            *,
            name: str = MISSING,
            verification_level: VerificationLevel | None = MISSING,
            default_message_notifications: NotificationLevel | None = MISSING,
            explicit_content_filter: ContentFilterLevel | None = MISSING,
            afk_channel: Snowflake | None = MISSING,
            icon: FileT | None = MISSING,
            owner: Snowflake = MISSING,
            splash: FileT | None = MISSING,
            discovery_splash: FileT | None = MISSING,
            banner: FileT | None = MISSING,
            system_channel: Snowflake | None = MISSING,
            system_channel_flags: SystemChannelFlags | None = MISSING,
            rules_channel: Snowflake | None = MISSING,
            preferred_locale: Locale | None = MISSING,
            public_updates_channel: Snowflake = MISSING,
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
        verification_level : novus.enums.guild.VerificationLevel | None
            The verification level you want to set the guild to.
        default_message_notifications : novus.enums.guild.NotificationLevel | None
            The default message notification level you want to set the guild to.
        explicit_content_filter : novus.enums.guild.ContentFilterLevel | None
            The content filter level you want to set the guild to.
        afk_channel : novus.models.abc.Snowflake | None
            The channel you want to set as the guild's AFK channel.
        icon : str | bytes | io.IOBase | None
            The icon that you want to set for the guild. Can be its bytes, a
            file path, or a file object.
        owner : novus.models.abc.Snowflake
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
        system_channel : novus.models.abc.Snowflake | None
            The system channel you want to set for the guild.
        system_channel_flags : novus.flags.guild.SystemChannelFlags | None
            The system channel flags you want to set.
        rules_channel : novus.models.abc.Snowflake | None
            The channel you want to set as the rules channel.
        preferred_locale : Locale | None
            The locale you want to set as the guild's preferred.
        public_updates_channel : novus.models.abc.Snowflake
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
        novus.models.Guild
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
            updates["afk_channel"] = afk_channel
        if icon is not None:
            updates["icon"] = icon
        if owner is not None:
            updates["owner"] = owner
        if splash is not None:
            updates["splash"] = splash
        if discovery_splash is not None:
            updates["discovery_splash"] = discovery_splash
        if banner is not None:
            updates["banner"] = banner
        if system_channel is not None:
            updates["system_channel"] = system_channel
        if system_channel_flags is not None:
            updates["system_channel_flags"] = system_channel_flags
        if rules_channel is not None:
            updates["rules_channel"] = rules_channel
        if preferred_locale is not None:
            updates["preferred_locale"] = preferred_locale
        if public_updates_channel is not None:
            updates["public_updates_channel"] = public_updates_channel
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
            type: Literal[ChannelType.public_thread, ChannelType.private_thread] = ...,
            bitrate: int = ...,
            user_limit: int = ...,
            rate_limit_per_user: int = ...,
            position: int = ...,
            permission_overwrites: list[PermissionOverwrite] = ...,
            parent: Snowflake = ...,
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
            type: ChannelType = ChannelType.guild_text,
            bitrate: int = ...,
            user_limit: int = ...,
            rate_limit_per_user: int = ...,
            position: int = ...,
            permission_overwrites: list[PermissionOverwrite] = ...,
            parent: Snowflake = ...,
            nsfw: bool = ...,
            default_auto_archive_duration: int = ...,
            default_reaction_emoji: Reaction = ...,
            available_tags: list[ForumTag] = ...) -> GuildTextChannel:
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
            parent: Snowflake = MISSING,
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
        type : novus.enums.ChannelType
            The type of the channel.
        bitrate : int
            The bitrate for the channel. Only for use with voice channels.
        user_limit : int
            The user limit for the channel. Only for use with voice channels.
        rate_limit_per_user : int
            The slowmode seconds on the channel.
        position : int
            The channel position.
        permission_overwrites : list[novus.models.PermissionOverwrite]
            A list of permission overwrites for the channel.
        parent : novus.models.abc.Snowflake
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
            update["parent"] = parent
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
        Get a member from the server.
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
        list[novus.models.GuildMember]
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
        list[novus.models.GuildMember]
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
        novus.models.GuildMember | None
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
            user_id: int,
            *,
            reason: str | None = None,
            nick: str | None = MISSING,
            roles: list[Snowflake] = MISSING,
            mute: bool = MISSING,
            deaf: bool = MISSING,
            voice_channel: Snowflake | None = MISSING,
            timeout_until: dt | None = MISSING) -> GuildMember:
        """
        Edit a guild member.

        Parameters
        ----------
        user_id : int
            The ID of the user you want to edit.
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
            update["roles"] = roles
        if mute is not MISSING:
            update["mute"] = mute
        if deaf is not MISSING:
            update["deaf"] = deaf
        if voice_channel is not MISSING:
            update["channel"] = voice_channel
        if timeout_until is not MISSING:
            update["communication_disabled_until"] = timeout_until

        member = await self._state.guild.modify_guild_member(
            self.id,
            user_id,
            reason=reason,
            **update,
        )
        member.guild = self
        return member

    async def add_member_role(
            self: StateSnowflake,
            user_id: int,
            role_id: int,
            *,
            reason: str | None = None) -> None:
        """
        Add a role to a user.

        Requires the ``MANAGE_ROLES`` permission.

        Parameters
        ----------
        user_id : int
            The user you want to add the role to.
        role_id : int
            The ID of the role you want to add.
        reason : str | None
            The reason shown in the audit log.
        """

        await self._state.guild.add_guild_member_role(
            self.id,
            user_id,
            role_id,
            reason=reason,
        )

    async def remove_member_role(
            self: StateSnowflake,
            user_id: int,
            role_id: int,
            *,
            reason: str | None = None) -> None:
        """
        Remove a role from a member.

        Requires the ``MANAGE_ROLES`` permission.

        Parameters
        ----------
        user_id : int
            The user you want to add the role to.
        role_id : int
            The ID of the role you want to add.
        reason : str | None
            The reason shown in the audit log.
        """

        await self._state.guild.add_guild_member_role(
            self.id,
            user_id,
            role_id,
            reason=reason,
        )

    async def kick_member(
            self: StateSnowflake,
            user_id: int,
            *,
            reason: str | None = None) -> None:
        """
        Remove a user from the guild.

        Requires the ``KICK_MEMBERS`` permission.

        Parameters
        ----------
        user_id : int
            The user you want to remove.
        reason : str | None
            The reason to be shown in the audit log.
        """

        await self._state.guild.remove_guild_member(
            self.id,
            user_id,
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

    async def fetch_ban(self: StateSnowflake, user_id: int) -> GuildBan:
        """
        Get an individual user's ban.

        Parameters
        ----------
        user_id : int
            The user whose ban you want to get.

        Returns
        -------
        novus.models.GuildBan
            The ban for the user.
        """

        return await self._state.guild.get_guild_ban(
            self.id,
            user_id,
        )

    async def create_ban(
            self: StateSnowflake,
            user_id: int,
            *,
            reason: str | None = None,
            delete_message_seconds: int = MISSING) -> None:
        """
        Get an individual user's ban.

        Parameters
        ----------
        user_id : int
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
            user_id,
            reason=reason,
            **updates
        )
        return

    async def remove_ban(
            self: StateSnowflake,
            user_id: int,
            *,
            reason: str | None = None) -> None:
        """
        Remove a user's ban

        Parameters
        ----------
        user_id : int
            The user who you want to ban.
        reason : str | None
            The reason to be shown in the audit log.
        """

        await self._state.guild.remove_guild_ban(
            self.id,
            user_id,
            reason=reason,
        )
        return

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
        permissions : novus.flags.Permissions
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

    async def move_roles(self, *args, **kwargs):
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
        permissions : novus.flags.Permissions
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

    async def edit_mfa_level(self, *args, **kwargs):
        raise NotImplementedError()

    async def delete_role(
            self: StateSnowflake,
            role_id: int,
            *,
            reason: str | None = None) -> None:
        """
        A role to delete.

        Parameters
        ----------
        role_id : int
            The ID of the role to delete.
        reason : str | None
            The reason to be shown in the audit log.
        """

        await self._state.guild.delete_guild_role(
            self.id,
            role_id,
            reason=reason,
        )
        return None

    async def fetch_prune_count(self, *args, **kwargs):
        raise NotImplementedError()

    async def prune(self, *args, **kwargs):
        raise NotImplementedError()

    async def fetch_voice_regions(self, *args, **kwargs):
        raise NotImplementedError()

    async def fetch_invites(self: StateSnowflake) -> list[Invite]:
        """
        Get the invites for the guild.

        Requires the ``MANAGE_GUILD`` permission.

        Returns
        -------
        list[novus.models.Invite]
            A list of invites.
        """

        return await self._state.guild.get_guild_invites(self.id)

    async def fetch_integrations(self, *args, **kwargs):
        raise NotImplementedError()

    async def delete_integration(self, *args, **kwargs):
        raise NotImplementedError()

    async def fetch_widget(self, *args, **kwargs):
        raise NotImplementedError()

    async def edit_widget(self, *args, **kwargs):
        raise NotImplementedError()

    async def edit_vainity_url(self, *args, **kwargs):
        raise NotImplementedError()

    async def edit_widget_image(self, *args, **kwargs):
        raise NotImplementedError()

    async def fetch_welcome_screen(self, *args, **kwargs):
        raise NotImplementedError()

    async def edit_welcome_screen(self, *args, **kwargs):
        raise NotImplementedError()

    async def edit_member_voice_state(self, *args, **kwargs):
        raise NotImplementedError()

    async def edit_current_member_voice_state(self, *args, **kwargs):
        raise NotImplementedError()


class Guild(Hashable, GuildAPIMixin):
    """
    A model representing a guild given by Discord's API or gateway.

    Attributes
    ----------
    id : int
        The ID of the guild.
    name : str
        The name of the guild.
    icon_hash : str | None
        The hash associated with the guild's icon.
    icon : novus.models.Asset | None
        The asset associated with the guild's icon hash.
    splash_hash : str | None
        The hash associated with the guild's splash.
    splash : novus.models.Asset | None
        The asset associated with the guild's splash hash.
    discovery_splash_hash : str | None
        The hash associated with the guild's discovery splash.
    discovery_splash : novus.models.Asset | None
        The asset associated with the guild's discovery splash hash.
    owner_id : int
        The ID of the user that owns the guild.
    afk_channel_id : int | None
        The ID of the guild's AFK channel, if one is set.
    widget_enabled : bool
        Whether or not the widget for the guild is enabled.
    widget_channel_id : int | None
        If the widget is enabled, this will be the ID of the widget's channel.
    verification_level : novus.enums.VerificationLevel
        The verification level required for the guild.
    default_message_notifications : novus.enums.NotificationLevel
        The default message notification level.
    explicit_content_filter : novus.enums.ContentFilterLevel
        The explicit content filter level.
    roles : list[novus.models.Role]
        The roles associated with the guild, as returned from the cache.
    emojis : list[novus.models.Emoji]
        The emojis associated with the guild, as returned from the cache.
    features : list[str]
        A list of guild features.
    mfa_level : novus.enums.MFALevel
        The required MFA level for the guild.
    application_id : int | None
        The application ID of the guild creator, if the guild is bot-created.
    system_channel_id: int | None
        The ID of the channel where guild notices (such as welcome messages
        and boost events) are posted.
    system_channel_flags : novus.flags.SystemChannelFlags
        The flags associated with the guild's system channel.
    rules_channel_id : int | None
        The ID of the guild's rules channel.
    max_presences : int | None
        The maximum number of presences for the guild. For most guilds, this
        will be ``None``.
    max_members : int | None
        The maximum number of members allowed in the guild.
    vanity_url_code : str | None
        The vanity code for the guild's invite link.
    description : str | None
        The guild's description.
    banner_hash : str | None
        The hash associated with the guild's banner splash.
    banner : novus.models.Asset | None
        The asset associated with the guild's banner splash hash.
    premium_tier : novus.enums.PremiumTier
        The premium tier of the guild.
    premium_subscription_count : int
        The number of boosts the guild currently has.
    preferred_locale : novus.enums.Locale
        The locale for the guild, if set. Defaults to US English.
    public_updates_channel_id : int | None
        The ID of the channel when admins and moderators of community guilds
        receive notices from Discord.
    max_video_channel_users : int | None
        The maximum amount of users in a video channel.
    approximate_member_count : int | None
        The approximate number of members in the guild. Present in guild GET
        requests when ``with_counts`` is ``True``.
    approximate_presence_count : int | None
        The approximate number of non-offline members in the guild. Present
        in guild GET requests when ``with_counts`` is ``True``.
    welcome_screen : novus.models.WelcomeScreen | None
        The welcome screen of a community guild.
    nsfw_level : novus.enums.NSFWLevel
        The guild NSFW level.
    stickers : list[novus.models.Sticker]
        The list of stickers added to the guild.
    premium_progress_bar_enabled : bool
        Whether or not the progress bar is enabled.
    """

    __slots__ = (
        '_state',
        'id',
        'name',
        'icon_hash',
        'splash_hash',
        'discovery_splash_hash',
        'owner_id',
        'afk_channel_id',
        'afk_timeout',
        'verification_level',
        'default_message_notifications',
        'explicit_content_filter',
        'features',
        'mfa_level',
        'application_id',
        'system_channel_id',
        'system_channel_flags',
        'rules_channel_id',
        'vanity_url_code',
        'description',
        'banner_hash',
        'premium_tier',
        'preferred_locale',
        'public_updates_channel_id',
        'nsfw_level',
        'premium_progress_bar_enabled',
        'widget_enabled',
        'widget_channel_id',
        'max_presences',
        'max_members',
        'premium_subscription_count',
        'max_video_channel_users',
        'approximate_member_count',
        'welcome_screen',
        'emojis',
        'stickers',

        '_roles',
        '_members',
        '_guild_scheduled_events',
        '_threads',
        '_voice_states',
        '_channels',

        '_cs_icon',
        '_cs_splash',
        '_cs_discovery_splash',
        '_cs_banner',
    )

    def __init__(self, *, state: HTTPConnection, data: APIGuildPayload):
        self._state = state
        self.id = try_snowflake(data['id'])
        self.name = data['name']
        self.icon_hash = data['icon'] or data.get('icon_hash')
        self.splash_hash = data['splash']
        self.discovery_splash_hash = data['discovery_splash']
        self.owner_id = try_snowflake(data['owner_id'])
        self.afk_channel_id = try_snowflake(data['afk_channel_id'])
        self.afk_timeout = data['afk_timeout']
        self.verification_level = VerificationLevel(data['verification_level'])
        self.default_message_notifications = NotificationLevel(data['default_message_notifications'])
        self.explicit_content_filter = ContentFilterLevel(data['explicit_content_filter'])
        self.features = data['features']
        self.mfa_level = MFALevel(data['mfa_level'])
        self.application_id = try_snowflake(data['application_id'])
        self.system_channel_id = try_snowflake(data['system_channel_id'])
        self.system_channel_flags = SystemChannelFlags(data['system_channel_flags'])
        self.rules_channel_id = try_snowflake(data['rules_channel_id'])
        self.vanity_url_code = data['vanity_url_code']
        self.description = data['description']
        self.banner_hash = data['banner']
        self.premium_tier = PremiumTier(data['premium_tier'])
        self.preferred_locale = Locale(data['preferred_locale'])
        self.public_updates_channel_id = try_snowflake(data['public_updates_channel_id'])
        self.nsfw_level = NSFWLevel(data.get('nsfw_level', 0))
        self.premium_progress_bar_enabled = data.get('premium_progress_bar_enabled', False)

        # Optional attrs
        self.widget_enabled = data.get('widget_enabled', False)
        self.widget_channel_id = try_snowflake(data.get('widget_channel_id'))
        self.max_presences = data.get('max_presences')
        self.max_members = data.get('max_members')
        self.premium_subscription_count = data.get('premium_subscription_count', 0)
        self.max_video_channel_users = data.get('max_video_channel_users')
        self.approximate_member_count = data.get('approximate_member_count')
        self.welcome_screen = None
        if 'welcome_screen' in data:
            self.welcome_screen = WelcomeScreen(data=data['welcome_screen'])
        self.emojis = [
            Emoji(state=self._state, data=d, guild=self)
            for d in data['emojis']
        ]
        self.stickers = [
            Sticker(state=self._state, data=d, guild=self)
            for d in data.get('stickers', list())
        ]

        # Gateway attributes
        self._roles: dict[int, Role] = {}  # Guild role crate/update/delete
        self._members: dict[int, GuildMember] = {}  # Guild member add/remove/update/chunk
        self._guild_scheduled_events: dict[int, None] = {}  # Guild scheduled event create/update/delete/useradd/userremove
        self._threads: dict[int, None] = {}  # Thread create/update/delete/listsync
        self._voice_states: dict[int, None] = {}
        self._channels: dict[int, Channel] = {}  # Channel create/update/delete/pinsupdate
        self._sync(data=data)  # type: ignore

    def _sync(self, *, data: GatewayGuildPayload):
        """
        Sync the cached state with the given gateway payload.
        """

        if 'roles' in data:
            for d0 in data['roles']:
                id = int(d0['id'])
                self._roles[id] = Role(
                    state=self._state,
                    data=d0,
                    guild=self,
                )
        if 'members' in data:
            for d1 in data.get('members', ()):
                id = int(d1['user']['id'])
                self._members[id] = GuildMember(
                    state=self._state,
                    data=d1,
                    guild=self,
                )
        if 'guild_scheduled_events' in data:
            for d2 in data.get('guild_scheduled_events', ()):
                id = int(d2['id'])
                self._guild_scheduled_events[id] = None
        if 'threads' in data:
            for d3 in data.get('threads', ()):
                id = int(d3['id'])
                self._threads[id] = None
        if 'voice_states' in data:
            for d4 in data.get('voice_states', ()):
                id = int(d4['user_id'])
                self._voice_states[id] = None
        if 'channels' in data:
            for d5 in data.get('channels', ()):
                id = int(d5['id'])
                self._channels[id] = c = Channel._from_data(
                    state=self._state,
                    data=d5,
                )
                c.guild = self

    __repr__ = generate_repr(('id', 'name',))

    @cached_slot_property('_cs_icon')
    def icon(self) -> Asset:
        return Asset.from_guild_icon(self)

    @cached_slot_property('_cs_splash')
    def splash(self) -> Asset:
        return Asset.from_guild_splash(self)

    @cached_slot_property('_cs_discovery_splash')
    def discovery_splash(self) -> Asset:
        return Asset.from_guild_discovery_splash(self)

    @cached_slot_property('_cs_banner')
    def banner(self) -> Asset:
        return Asset.from_guild_banner(self)

    def roles(self) -> list[Role]:
        return [
            i
            for i in
            self._roles.values()
        ]


class OauthGuild(Guild):
    """
    A model for a Discord guild when fetched by an authenticated user through
    the API.

    Attributes
    ----------
    owner : bool
        Whether the authenticated user owns the guild.
    permissions : novus.flags.Permissions
        The authenticated user's permissions in the guild.
    """

    def __init__(self, *, state, data: APIGuildPayload):
        self.owner: bool = data.get('owner', False)
        self.permissions: Permissions = Permissions(int(data.get('permissions', 0)))
        super().__init__(state=state, data=data)


class GuildPreview(GuildAPIMixin):
    """
    A model for the preview of a guild.

    Attributes
    ----------
    id : int
        The ID of the guild.
    name : str
        The name of the guild.
    icon_hash : str | None
        The icon hash for the guild.
    icon : novus.models.Asset | None
        The icon asset associated with the guild.
    splash_hash : str | None
        The splash hash for the guild.
    splash : novus.models.Asset | None
        The splash asset associated with the guild.
    discovery_splash_hash : str | None
        The discovery splash hash for the guild.
    discovery_splash : novus.models.Asset | None
        The discovery splash asset associated with the guild.
    emojis : list[novus.models.Emoji]
        A list of emojis in the guild.
    features : list[str]
        A list of features that the guild has.
    approximate_member_count : int
        The approximate member count for the guild.
    approximate_presence_count : int
        The approximate online member count for the guild.
    description : str
        The description of the guild.
    stickers : list[novus.models.Sticker]
        A list of the stickers in the guild.
    """

    __slots__ = (
        '_state',
        'id',
        'name',
        'icon_hash',
        'splash_hash',
        'discovery_splash_hash',
        'emojis',
        'features',
        'approximate_member_count',
        'approximate_presence_count',
        'description',
        'stickers',

        '_cs_icon',
        '_cs_splash',
        '_cs_discovery_splash',
    )

    def __init__(self, *, state: HTTPConnection, data: GuildPreviewPayload):
        self._state = state
        self.id = try_snowflake(data['id'])
        self.name = data['name']
        self.icon_hash = data.get('icon')
        self.splash_hash = data.get('splash')
        self.discovery_splash_hash = data.get('discovery_splash')
        self.emojis = [
            Emoji(state=self._state, data=i, guild=self)
            for i in data.get('emojis', list())
        ]
        self.features = data.get('features', list())
        self.approximate_member_count = data['approximate_member_count']
        self.approximate_presence_count = data['approximate_presence_count']
        self.description = data.get('description')
        self.stickers = [
            Sticker(state=self._state, data=i, guild=self)
            for i in data.get('stickers', list())
        ]

    @cached_slot_property('_cs_icon')
    def icon(self) -> Asset:
        return Asset.from_guild_icon(self)

    @cached_slot_property('_cs_splash')
    def splash(self) -> Asset:
        return Asset.from_guild_splash(self)

    @cached_slot_property('_cs_discovery_splash')
    def discovery_splash(self) -> Asset:
        return Asset.from_guild_discovery_splash(self)
