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

import asyncio
import logging
import random
import string
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal, NoReturn, overload

from typing_extensions import Self

from ..flags import Permissions, SystemChannelFlags
from ..utils import (
    MISSING,
    cached_slot_property,
    generate_repr,
    try_id,
    try_object,
    try_snowflake,
)
from .abc import Hashable
from .asset import Asset
from .channel import Channel
from .emoji import Emoji
from .guild_member import GuildMember
from .role import Role
from .scheduled_event import ScheduledEvent
from .sticker import Sticker
from .user import User
from .voice_state import VoiceState
from .welcome_screen import WelcomeScreen

if TYPE_CHECKING:
    from .. import payloads
    from ..api import HTTPConnection
    from ..utils import DiscordDatetime
    from ..utils.types import AnySnowflake, FileT
    from . import abc
    from .audit_log import AuditLog
    from .auto_moderation import (
        AutoModerationAction,
        AutoModerationRule,
        AutoModerationTriggerMetadata,
    )
    from .channel import ForumTag, PermissionOverwrite
    from .file import File
    from .invite import Invite
    from .reaction import Reaction

__all__ = (
    'BaseGuild',
    'GuildBan',
    'Guild',
    'PartialGuild',
    'OauthGuild',
    'GuildPreview',
)


log = logging.getLogger("novus.guild")


class BaseGuild:
    """
    The bare minimum guild instance we can have. Basically a snowflake with a
    state, a name, and API methods.

    Attributes
    ----------
    state : novus.api.HTTPConnection
        The connection to Discord.
    id : int
        The ID of the guild.
    name : str | None
        The name of the guild. Can be ``None`` if this is just a state snowflake
        implementing API methods.
    """

    __slots__ = (
        'state',
        'id',
        'name',
    )

    def __init__(self, *, state: HTTPConnection, data: payloads.Guild):
        self.state = state
        self.id: int = try_snowflake(data["id"])
        self.name: str | None = data.get("name")

    def __str__(self) -> str:
        return str(self.name)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id!r} name={self.name!r}>"

    # API methods

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
    async def fetch(cls, state: HTTPConnection, guild: AnySnowflake) -> Guild:
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

    async def fetch_preview(self: abc.StateSnowflake) -> NoReturn:
        raise NotImplementedError()

    async def edit(
            self: abc.StateSnowflake,
            *,
            name: str = MISSING,
            verification_level: int | None = MISSING,
            default_message_notifications: int | None = MISSING,
            explicit_content_filter: int | None = MISSING,
            afk_channel: AnySnowflake | None = MISSING,
            icon: FileT | None = MISSING,
            owner: AnySnowflake = MISSING,
            splash: FileT | None = MISSING,
            discovery_splash: FileT | None = MISSING,
            banner: FileT | None = MISSING,
            system_channel: AnySnowflake | None = MISSING,
            system_channel_flags: SystemChannelFlags | None = MISSING,
            rules_channel: AnySnowflake | None = MISSING,
            preferred_locale: str | None = MISSING,
            public_updates_channel: AnySnowflake = MISSING,
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
        verification_level : int | None
            The verification level you want to set the guild to.

            .. seealso:: `novus.VerificationLevel`
        default_message_notifications : int | None
            The default message notification level you want to set the guild to.

            .. seealso:: `novus.NotificationLevel`
        explicit_content_filter : int | None
            The content filter level you want to set the guild to.

            .. seealso:: `novus.guild.ContentFilterLevel`
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
        preferred_locale : str | None
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

        if name is not MISSING:
            updates["name"] = name
        if verification_level is not MISSING:
            updates["verification_level"] = verification_level
        if default_message_notifications is not MISSING:
            updates["default_message_notifications"] = default_message_notifications
        if explicit_content_filter is not MISSING:
            updates["explicit_content_filter"] = explicit_content_filter
        if afk_channel is not MISSING:
            updates["afk_channel"] = try_object(afk_channel)
        if icon is not MISSING:
            updates["icon"] = icon
        if owner is not MISSING:
            updates["owner"] = try_object(owner)
        if splash is not MISSING:
            updates["splash"] = splash
        if discovery_splash is not MISSING:
            updates["discovery_splash"] = discovery_splash
        if banner is not MISSING:
            updates["banner"] = banner
        if system_channel is not MISSING:
            updates["system_channel"] = try_object(system_channel)
        if system_channel_flags is not MISSING:
            updates["system_channel_flags"] = system_channel_flags
        if rules_channel is not MISSING:
            updates["rules_channel"] = try_object(rules_channel)
        if preferred_locale is not MISSING:
            updates["preferred_locale"] = preferred_locale
        if public_updates_channel is not MISSING:
            updates["public_updates_channel"] = try_object(public_updates_channel)
        if features is not MISSING:
            updates["features"] = features
        if description is not MISSING:
            updates["description"] = description
        if premium_progress_bar_enabled is not MISSING:
            updates["premium_progress_bar_enabled"] = premium_progress_bar_enabled

        return await self.state.guild.modify_guild(
            self.id,
            reason=reason,
            **updates,
        )

    async def delete(self: abc.StateSnowflake) -> None:
        """
        Delete the current guild permanently. You must be the owner of the
        guild to run this successfully.
        """

        await self.state.guild.delete_guild(self.id)
        return None

    async def edit_mfa_level(self) -> NoReturn:
        raise NotImplementedError()

    async def fetch_prune_count(self) -> NoReturn:
        raise NotImplementedError()

    async def prune(self) -> NoReturn:
        raise NotImplementedError()

    async def fetch_voice_regions(self) -> NoReturn:
        raise NotImplementedError()

    async def fetch_invites(self: abc.StateSnowflake) -> list[Invite]:
        """
        Get the invites for the guild.

        Requires the ``MANAGE_GUILD`` permission.

        Returns
        -------
        list[novus.Invite]
            A list of invites.
        """

        return await self.state.guild.get_guild_invites(self.id)

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

    @overload
    async def chunk_members(
            self: abc.StateSnowflake,
            query: str,
            limit: int,
            user_ids: list[int],
            wait: Literal[False]) -> None:
        ...

    @overload
    async def chunk_members(
            self: abc.StateSnowflake,
            query: str,
            limit: int,
            user_ids: list[int],
            wait: Literal[True]) -> list[GuildMember]:
        ...

    async def chunk_members(
            self: abc.StateSnowflake,
            query: str = "",
            limit: int = 0,
            user_ids: list[int] | None = None,
            wait: bool = True) -> list[GuildMember] | None:
        """
        Request member chunks from the gateway.

        This will *only* work if you are connected to the gateway - this will
        not work with HTTP-only bots.

        Parameters
        ----------
        query : str
            A search string for usernames.
        limit : int
            A limit for the retrieved member count.
        user_ids : list[int]
            A list of user IDs to request.
        wait : bool
            Whether or not to wait for a response.

        Returns
        -------
        list[novus.GuildMember] | None
            A list of requested users or ``None`` if you chose not to wait.
        """

        # Get shard
        shard_id = (self.id >> 22) % self.state.gateway.shard_count
        try:
            shard = self.state.gateway.shards[shard_id]
        except KeyError:
            raise ValueError("Could not find shard associated with this guild.")

        # Get stuff
        nonce = None
        if wait:
            nonce = str("".join(random.choices(string.ascii_lowercase)))
        event = await shard.chunk_guild(
            self.id,
            query=query,
            limit=limit,
            user_ids=user_ids,
            nonce=nonce,
        )
        if event is None:
            return None
        assert nonce
        await event.wait()
        return shard.chunk_groups.pop(nonce)

    async def fetch_audit_logs(
            self: abc.StateSnowflake,
            *,
            user_id: int | None = None,
            action_type: int | None = None,
            before: int | None = None,
            after: int | None = None,
            limit: int = 50) -> AuditLog:
        """
        Get the audit logs for the guild.

        Parameters
        ----------
        user_id: int | None
            The ID of the moderator you want to to filter by.
        action_type: int | None
            The ID of an action to filter by.

            .. seealso:: `novus.AuditLogEventType`
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

        return await self.state.audit_log.get_guild_audit_log(
            self.id,
            user_id=user_id,
            action_type=action_type,
            before=before,
            after=after,
            limit=limit,
        )

    async def fetch_auto_moderation_rules(
            self: abc.StateSnowflake) -> list[AutoModerationRule]:
        """
        Get the auto moderation rules for this guild.

        Returns
        -------
        list[novus.AutoModerationRule]
            A list of the auto moderation rules for the guild.
        """

        return await (
            self.state.auto_moderation
            .list_auto_moderation_rules_for_guild(self.id)
        )

    async def create_auto_moderation_rule(
            self: abc.StateSnowflake,
            *,
            reason: str | None = None,
            name: str,
            event_type: int,
            trigger_type: int,
            actions: list[AutoModerationAction],
            trigger_metadata: AutoModerationTriggerMetadata | None = None,
            enabled: bool = False,
            exempt_roles: list[AnySnowflake] | None = None,
            exempt_channels: list[AnySnowflake] | None = None) -> AutoModerationRule:
        """
        Create a new auto moderation rule.

        Parameters
        ----------
        name : str
            The new name for the role.
        event_type : int
            The event type.

            .. seealso:: `novus.AutoModerationEventType`
        trigger_type : int
            The trigger type.

            .. seealso:: `novus.AutoModerationTriggerType`
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

        return await self.state.auto_moderation.create_auto_moderation_rule(
            self.id,
            reason=reason,
            **updates,
        )

    async def fetch_channels(self: abc.StateSnowflake) -> list[Channel]:
        """
        Fetch all of the channels from a guild.

        Returns
        -------
        list[novus.Channel]
            A list of channels from the guild.
        """

        channels = await self.state.guild.get_guild_channels(self.id)
        return channels

    async def create_channel(
            self: abc.StateSnowflake,
            *,
            name: str,
            type: int = MISSING,
            topic: str = MISSING,
            bitrate: int = MISSING,
            user_limit: int = MISSING,
            rate_limit_per_user: int = MISSING,
            position: int = MISSING,
            permission_overwrites: list[PermissionOverwrite] = MISSING,
            parent: AnySnowflake = MISSING,
            nsfw: bool = MISSING,
            default_auto_archive_duration: int = MISSING,
            default_reaction_emoji: Reaction = MISSING,
            available_tags: list[ForumTag] = MISSING,
            reason: str = MISSING) -> Channel:
        """
        Create a channel within the guild.

        Parameters
        ----------
        name : str
            The name of the channel.
        type : int
            The type of the channel.

            .. seealso:: `novus.ChannelType`
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
        parent : int | str | novus.abc.Snowflake
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
        reason : str
            The reason to be shown in the audit log.

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
        if topic is not MISSING:
            update["topic"] = topic
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

        channel = await self.state.guild.create_guild_channel(self.id, **update, reason=reason)
        return channel

    async def move_channels(self: abc.StateSnowflake) -> None:
        raise NotImplementedError()

    async def fetch_active_threads(self: abc.StateSnowflake) -> list[Channel]:
        """
        Get the active threads from inside the guild.

        Returns
        -------
        list[novus.Channel]
            A list of threads.
        """

        threads = await self.state.guild.get_active_guild_threads(self.id)
        return threads

    async def fetch_emoji(self: abc.StateSnowflake, id: int) -> Emoji:
        """
        List all of the emojis for the guild.

        .. seealso:: :func:`novus.Emoji.fetch`

        Returns
        -------
        list[novus.Emoji]
            A list of the guild's emojis.
        """

        emoji = await self.state.emoji.get_emoji(self.id, id)
        return emoji

    async def fetch_all_emojis(
            self: abc.StateSnowflake) -> list[Emoji]:
        """
        List all of the emojis for the guild.

        .. seealso:: :func:`novus.Emoji.fetch_all_for_guild`

        Returns
        -------
        list[novus.Emoji]
            A list of the guild's emojis.
        """

        emojis = await self.state.emoji.list_guild_emojis(self.id)
        return emojis

    async def create_emoji(
            self: abc.StateSnowflake,
            *,
            name: str,
            image: FileT,
            roles: list[AnySnowflake] | None = None,
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

        return await self.state.emoji.create_guild_emoji(
            self.id,
            reason=reason,
            name=name,
            image=image,
            roles=roles or list(),
        )

    async def fetch_roles(
            self: abc.StateSnowflake) -> list[Role]:
        """
        Get a list of roles for the guild.

        Returns
        -------
        list[novus.model.Role]
            A list of roles in the guild.
        """

        roles = await self.state.guild.get_guild_roles(self.id)
        return roles

    async def create_role(
            self: abc.StateSnowflake,
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

        role = await self.state.guild.create_guild_role(
            self.id,
            reason=reason,
            **update,
        )
        return role

    async def move_roles(self) -> NoReturn:
        raise NotImplementedError()

    async def edit_role(
            self: abc.StateSnowflake,
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

        role = await self.state.guild.modify_guild_role(
            self.id,
            role_id,
            reason=reason,
            **update,
        )
        return role

    async def delete_role(
            self: abc.StateSnowflake,
            role: AnySnowflake,
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

        await self.state.guild.delete_guild_role(
            self.id,
            try_id(role),
            reason=reason,
        )
        return None

    async def fetch_scheduled_events(
            self: abc.StateSnowflake,
            *,
            with_user_count: bool = False) -> list[ScheduledEvent]:
        """
        Get a list of all of the scheduled events for a guild.

        .. seealso:: :func:`novus.ScheduledEvent.fetch_all_for_guild`

        Parameters
        ----------
        with_user_count : bool
            Whether or not to include the event's user count.

        Returns
        -------
        list[novus.ScheduledEvent]
            The scheduled events for the guild.
        """

        return await self.state.guild_scheduled_event.list_scheduled_events_for_guild(
            self.id,
            with_user_count=with_user_count,
        )

    async def create_scheduled_event(
            self: abc.StateSnowflake,
            *,
            name: str,
            start_time: DiscordDatetime,
            entity_type: int,
            privacy_level: int,
            reason: str | None = None,
            channel: AnySnowflake | None = MISSING,
            location: str = MISSING,
            end_time: DiscordDatetime = MISSING,
            description: str | None = MISSING,
            status: int = MISSING,
            image: FileT | None = MISSING) -> ScheduledEvent:
        """
        Create a new scheduled event.

        .. seealso:: :func:`novus.ScheduledEvent.create`

        Parameters
        ----------
        name : str
            The name of the event.
        start_time : datetime.datetime
            The time to schedule the event start.
        entity_type : int
            The type of the event.

            .. seealso: `novus.EventEntityType`
        privacy_level : int
            The privacy level of the event.

            .. seealso:: `novus.EventPrivacyLevel`
        channel : int | Snowflake | None
            The channel of the scheduled event. Set to ``None`` if the event
            type is being set to external.
        location : str
            The location of the event.
        end_time : datetime.datetime
            The time to schedule the event end.
        description : str | None
            The description of the event.
        status : int
            The status of the event.

            .. seealso:: `novus.EventStatus`
        image : str | bytes | io.IOBase | None
            The cover image of the scheduled event.
        reason : str | None
            The reason shown in the audit log.

        Returns
        -------
        novus.ScheduledEvent
            The new scheduled event.
        """

        update: dict[str, Any] = {}
        if channel is not MISSING:
            update['channel'] = channel
        if location is not MISSING:
            update['location'] = location
        if name is not MISSING:
            update['name'] = name
        if privacy_level is not MISSING:
            update['privacy_level'] = privacy_level
        if start_time is not MISSING:
            update['start_time'] = start_time
        if end_time is not MISSING:
            update['end_time'] = end_time
        if description is not MISSING:
            update['description'] = description
        if entity_type is not MISSING:
            update['entity_type'] = entity_type
        if status is not MISSING:
            update['status'] = status
        if image is not MISSING:
            update['image'] = image

        return await self.state.guild_scheduled_event.create_guild_scheduled_event(
            self.id,
            **update,
            reason=reason,
        )

    async def fetch_sticker(
            self: abc.StateSnowflake,
            id: AnySnowflake) -> Sticker:
        """
        Get an individual sticker associated with the guild via its ID.

        .. seealso:: :func:`novus.Sticker.fetch`

        Parameters
        ----------
        id : str
            The ID of the sticker.

        Returns
        -------
        novus.Sticker
            The associated sticker instance.
        """

        sticker = await self.state.sticker.get_guild_sticker(self.id, try_id(id))
        return sticker

    async def fetch_all_stickers(self: abc.StateSnowflake) -> list[Sticker]:
        """
        List all stickers associated with the guild.

        .. seealso:: :func:`novus.Sticker.fetch_all_for_guild`

        Returns
        -------
        list[novus.Sticker]
            The stickers associated with the guild.
        """

        stickers = await self.state.sticker.list_guild_stickers(self.id)
        return stickers

    async def create_sticker(
            self: abc.StateSnowflake,
            *,
            reason: str | None = None,
            name: str,
            description: str | None = None,
            tags: str,
            image: File) -> Sticker:
        """
        Create a new sticker.

        .. seealso:: :func:`novus.Sticker.create`

        Parameters
        ----------
        name : str
            The name of the sticker.
        tags : str
            Autocomplete/suggestion tags for the sitcker.
        description : str | None
            Description of the sticker.
        image : novus.File
            The image to be uploaded. All aside from the data itself is
            discarded - the name and description are taken from the other
            parameters.
        reason : str | None
            The reason shown in the audit log.

        Reutrns
        -------
        novus.Sticker
            The created sticker instance.
        """

        return await self.state.sticker.create_guild_sticker(
            self.id,
            reason=reason,
            **{
                "name": name,
                "description": description,
                "tags": tags,
                "file": image.data,
            },
        )

    async def fetch_me(
            self: abc.StateSnowflake) -> GuildMember:
        """
        Get the member object associated with the current guild and the current
        connection.

        .. note::

            Only usable via Oauth with the ``guilds.members.read`` scope.
            This is not usable as a bot.

        .. seealso:: :func:`novus.GuildMember.fetch_me`

        Returns
        -------
        novus.GuildMember
            The member object for the current user.
        """

        member = await self.state.user.get_current_user_guild_member(self.id)
        return member

    async def leave(
            self: abc.StateSnowflake) -> None:
        """
        Leave the current guild.
        """

        await self.state.user.leave_guild(self.id)

    async def fetch_member(
            self: abc.StateSnowflake,
            member_id: int) -> GuildMember:
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
        return member

    async def fetch_members(
            self: abc.StateSnowflake,
            *,
            limit: int = 1_000,
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
        return members

    async def search_members(
            self: abc.StateSnowflake,
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
        return members

    async def add_member(
            self: abc.OauthStateSnowflake,
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
            The ID of the user that you want to add. The user ID must match the
            ID of the oauth token.
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
        return member

    async def edit_member(
            self: abc.StateSnowflake,
            user: AnySnowflake,
            *,
            reason: str | None = None,
            nick: str | None = MISSING,
            roles: list[AnySnowflake] = MISSING,
            mute: bool = MISSING,
            deaf: bool = MISSING,
            voice_channel: AnySnowflake | None = MISSING,
            timeout_until: DiscordDatetime | None = MISSING) -> GuildMember:
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
        return member

    async def add_member_role(
            self: abc.StateSnowflake,
            user: AnySnowflake,
            role: AnySnowflake,
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
            self: abc.StateSnowflake,
            user: AnySnowflake,
            role: AnySnowflake,
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
            self: abc.StateSnowflake,
            user: AnySnowflake,
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
            self: abc.StateSnowflake,
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
            self: abc.StateSnowflake,
            user: AnySnowflake) -> GuildBan:
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
            self: abc.StateSnowflake,
            user: AnySnowflake,
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
            updates["delete_message_seconds"] = delete_message_seconds

        await self.state.guild.create_guild_ban(
            self.id,
            try_id(user),
            reason=reason,
            **updates
        )
        return

    async def unban(
            self: abc.StateSnowflake,
            user: AnySnowflake,
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


class PartialGuild(BaseGuild):
    """
    A model for a partial guild object, such as one retrieved from an invite
    link.

    This model still implements the normal guild API methods, though does not
    contain all of the data a guild would (see attributes).

    Attributes
    ----------
    id : int
        The ID of the guild.
    name : str
        The name of the guild.
    splash_hash : str | None
        The splash hash of the guild.
    splash : novus.Asset | None
        The splash asset for the guild.
    banner_hash : str | None
        The banner hash of the guild.
    banner : novus.Asset | None
        The banner asset for the guild.
    description : str | None
        A description of the guild.
    icon_hash : str | None
        The icon hash for the guild.
    icon : novus.Asset | None
        An icon asset for the guild.
    features : list[str]
        A list of features the guild implements.
    verification_level : int
        The guild's verification level.
    vainity_url_code : str | None
        The guild's vainity URL code.
    nsfw_level : int
        The guild's NSFW level.

        .. seealso:: `novus.NSFWLevel`
    premium_subscription_count : int
        The number of nitro boosts the guild has.
    """

    __slots__ = (
        'state',
        'id',
        'name',
        'splash_hash',
        'banner_hash',
        'description',
        'icon_hash',
        'features',
        'verification_level',
        'vainity_url_code',
        'nsfw_level',
        'premium_subscription_count',

        '_cs_splash',
        '_cs_banner',
        '_cs_icon',
    )

    def __init__(self, *, state: HTTPConnection, data: payloads.Guild):
        self.state = state
        self.id: int = try_snowflake(data['id'])
        self.name: str = data['name']
        self.splash_hash: str | None = data.get('splash')
        self.banner_hash: str | None = data.get('banner')
        self.description: str | None = data.get('description')
        self.icon_hash: str | None = data.get('icon')
        self.features: list[str] = data['features']  # pyright: ignore
        self.verification_level: int = data.get('verification_level', 0)
        self.vainity_url_code: str | None = data.get('vainity_url_code')
        self.nsfw_level: int = int(data.get('nsfw_level', 0))
        self.premium_subscription_count: int = data.get('premium_subscription_count', 0)

    __repr__ = generate_repr(('id', 'name',))

    @cached_slot_property('_cs_icon')
    def icon(self) -> Asset | None:
        if self.icon_hash is None:
            return None
        return Asset.from_guild_icon(self)

    @cached_slot_property('_cs_splash')
    def splash(self) -> Asset | None:
        if self.splash_hash is None:
            return None
        return Asset.from_guild_splash(self)

    @cached_slot_property('_cs_banner')
    def banner(self) -> Asset | None:
        if self.banner_hash is None:
            return None
        return Asset.from_guild_banner(self)


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
    user : novus.User
        The user that was banned.
    """

    reason: str | None
    user: User


class Guild(Hashable, BaseGuild):
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
    icon : novus.Asset | None
        The asset associated with the guild's icon hash.
    splash_hash : str | None
        The hash associated with the guild's splash.
    splash : novus.Asset | None
        The asset associated with the guild's splash hash.
    discovery_splash_hash : str | None
        The hash associated with the guild's discovery splash.
    discovery_splash : novus.Asset | None
        The asset associated with the guild's discovery splash hash.
    owner_id : int
        The ID of the user that owns the guild.
    afk_channel_id : int | None
        The ID of the guild's AFK channel, if one is set.
    widget_enabled : bool
        Whether or not the widget for the guild is enabled.
    widget_channel_id : int | None
        If the widget is enabled, this will be the ID of the widget's channel.
    verification_level : int
        The verification level required for the guild.

        .. seealso:: `novus.VerificationLevel`
    default_message_notifications : int
        The default message notification level.

        .. seealso:: `novus.NotificationLevel`
    explicit_content_filter : int
        The explicit content filter level.

        .. seealso:: `novus.guild.ContentFilterLevel`
    roles : list[novus.Role]
        The roles associated with the guild, as returned from the cache.
    emojis : list[novus.Emoji]
        The emojis associated with the guild, as returned from the cache.
    features : list[str]
        A list of guild features.
    mfa_level : int
        The required MFA level for the guild.

        .. seealso:: `novus.MFALevel`
    application_id : int | None
        The application ID of the guild creator, if the guild is bot-created.
    system_channel_id: int | None
        The ID of the channel where guild notices (such as welcome messages
        and boost events) are posted.
    system_channel_flags : novus.SystemChannelFlags
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
    banner : novus.Asset | None
        The asset associated with the guild's banner splash hash.
    premium_tier : int
        The premium tier of the guild.

        .. seealso:: `novus.PremiumTier`
    premium_subscription_count : int
        The number of boosts the guild currently has.
    preferred_locale : str
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
    welcome_screen : novus.WelcomeScreen | None
        The welcome screen of a community guild.
    nsfw_level : int
        The guild NSFW level.

        .. seealso:: `novus.NSFWLevel`
    stickers : list[novus.Sticker]
        The list of stickers added to the guild.
    premium_progress_bar_enabled : bool
        Whether or not the progress bar is enabled.
    """

    __slots__ = (
        'state',
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

        '_emojis',
        '_stickers',
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

    state: HTTPConnection
    id: int
    name: str
    icon_hash: str | None
    splash_hash: str | None
    discovery_splash_hash: str | None
    owner_id: int
    afk_channel_id: int | None
    afk_timeout: int | None
    verification_level: int
    default_message_notifications: int
    explicit_content_filter: int
    features: list[str]
    mfa_level: int
    application_id: int | None
    system_channel_id: int | None
    system_channel_flags: SystemChannelFlags
    rules_channel_id: int | None
    vanity_url_code: str | None
    description: str | None
    banner_hash: str | None
    premium_tier: int
    preferred_locale: str
    public_updates_channel_id: int | None
    nsfw_level: int
    premium_progress_bar_enabled: bool

    widget_enabled: bool
    widget_channel_id: int | None
    max_presences: int | None
    max_members: int | None
    premium_subscription_count: int
    max_video_channel_users: int | None
    approximate_member_count: int | None
    welcome_screen: WelcomeScreen | None

    def __init__(self, *, state: HTTPConnection, data: payloads.Guild | payloads.GatewayGuild):
        self.state = state
        self.id = try_snowflake(data['id'])
        self._emojis: dict[int, Emoji] = {}
        self._stickers: dict[int, Sticker] = {}
        self._roles: dict[int, Role] = {}
        self._members: dict[int, GuildMember] = {}
        self._guild_scheduled_events: dict[int, ScheduledEvent] = {}
        self._threads: dict[int, Channel] = {}
        self._voice_states: dict[int, VoiceState] = {}
        self._channels: dict[int, Channel] = {}
        self._update(data)

    def _update(self, data: payloads.Guild | payloads.GatewayGuild) -> Self:
        self.name = data['name']
        self.icon_hash = data['icon'] or data.get('icon_hash')
        self.splash_hash = data['splash']
        self.discovery_splash_hash = data['discovery_splash']
        self.owner_id = try_snowflake(data['owner_id'])
        self.afk_channel_id = try_snowflake(data['afk_channel_id'])
        self.afk_timeout = data['afk_timeout']
        self.verification_level = data['verification_level']
        self.default_message_notifications = data['default_message_notifications']
        self.explicit_content_filter = data['explicit_content_filter']
        self.features = data['features']
        self.mfa_level = int(data['mfa_level'])
        self.application_id = try_snowflake(data['application_id'])
        self.system_channel_id = try_snowflake(data['system_channel_id'])
        self.system_channel_flags = SystemChannelFlags(data['system_channel_flags'])
        self.rules_channel_id = try_snowflake(data['rules_channel_id'])
        self.vanity_url_code = data['vanity_url_code']
        self.description = data['description']
        self.banner_hash = data['banner']
        self.premium_tier = int(data['premium_tier'])
        self.preferred_locale = data['preferred_locale']
        self.public_updates_channel_id = try_snowflake(data['public_updates_channel_id'])
        self.nsfw_level = int(data.get('nsfw_level', 0))
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

        return self

    @property
    def emojis(self) -> list[Emoji]:
        return list(self._emojis.values())

    @property
    def stickers(self) -> list[Sticker]:
        return list(self._stickers.values())

    @property
    def roles(self) -> list[Role]:
        return list(self._roles.values())

    @property
    def members(self) -> list[GuildMember]:
        return list(self._members.values())

    @property
    def guild_scheduled_events(self) -> list[ScheduledEvent]:
        return list(self._guild_scheduled_events.values())

    @property
    def threads(self) -> list[Channel]:
        return list(self._threads.values())

    @property
    def voice_states(self) -> list[VoiceState]:
        return list(self._voice_states.values())

    @property
    def channels(self) -> list[Channel]:
        return list(self._channels.values())

    def _add_emoji(
            self,
            emoji: payloads.Emoji | Emoji,
            new_cache: dict[int, Any] | None = None) -> Emoji | None:
        """
        Add an emoji to the guild's cache, updating the state cache
        at the same time.
        """

        # Use created object
        if isinstance(emoji, Emoji):
            created = emoji

        # Update cached object if possible
        else:
            if emoji.get("id") is None or emoji["id"] is None:
                return None
            cached = self.state.cache.get_emoji(emoji["id"])
            if cached:
                created = cached._update(emoji)
            else:
                created = Emoji(state=self.state, data=emoji, guild=self)

        # Store in given cache
        assert created.id
        self.state.cache.add_emojis(created)
        (new_cache or self._emojis)[created.id] = created
        return created

    def _add_sticker(
            self,
            sticker: payloads.Sticker | Sticker,
            new_cache: dict[int, Any] | None = None) -> Sticker:
        """
        Add a sticker to the guild's cache, updating the state cache at the same
        time.
        """

        if isinstance(sticker, Sticker):
            created = sticker
        else:
            cached = self.state.cache.get_sticker(sticker["id"])
            if cached:
                created = cached._update(sticker)
            else:
                created = Sticker(state=self.state, data=sticker)
        self.state.cache.add_stickers(created)
        (new_cache or self._stickers)[created.id] = created
        return created

    def _add_role(
            self,
            role: payloads.Role | Role,
            new_cache: dict[int, Any] | None = None) -> Role:
        """
        Add a role to the guild's cache.
        """

        if isinstance(role, Role):
            created = role
        else:
            cached = self._roles.get(int(role["id"]))
            if cached:
                created = cached._update(role)
            else:
                created = Role(state=self.state, data=role, guild=self)
        (new_cache or self._roles)[created.id] = created
        return created

    def _add_member(
            self,
            member: payloads.GuildMember | GuildMember,
            new_cache: dict[int, Any] | None = None) -> GuildMember:
        """
        Add a guild member to the guild's cache, updating the state cache at
        the same time.
        """

        if isinstance(member, GuildMember):
            created = member
        else:
            cached = self._members.get(int(member["user"]["id"]))
            if cached:
                created = cached._update(member)
            else:
                created = GuildMember(state=self.state, data=member, guild_id=self.id)
                self.state.cache.add_users(created._user)
        (new_cache or self._members)[created.id] = created
        return created

    def _add_guild_scheduled_event(
            self,
            event: payloads.GuildScheduledEvent,
            new_cache: dict[int, Any] | None = None) -> ScheduledEvent:
        """
        Add a scheduled event to the guild's cache, updating the state cache at
        the same time.
        """

        cached = self.state.cache.get_event(event["id"])
        if cached:
            created = cached._update(event)
        else:
            created = ScheduledEvent(state=self.state, data=event)
        self.state.cache.add_events(created)
        (new_cache or self._guild_scheduled_events)[created.id] = created
        return created

    def _add_thread(
            self,
            thread: payloads.Channel | Channel,
            new_cache: dict[int, Any] | None = None) -> Channel:
        """
        Add a thread to the guild's cache, updating the state cache at the same
        time.
        """

        if isinstance(thread, Channel):
            created = thread
        else:
            cached: Channel | None
            cached = self.state.cache.get_channel(thread["id"])  # pyright: ignore
            if cached:
                created = cached._update(thread)
            else:
                created = Channel(state=self.state, data=thread)
        self.state.cache.add_channels(created)
        (new_cache or self._threads)[created.id] = created
        return created

    def _add_voice_state(
            self,
            voice_state: payloads.VoiceState | VoiceState,
            new_cache: dict[int, Any] | None = None) -> VoiceState:
        """
        Add a voice state to the guild's cache.
        """

        if isinstance(voice_state, VoiceState):
            created = voice_state
        else:
            cached = self._voice_states.get(int(voice_state["user_id"]))
            if cached:
                created = cached._update(voice_state)
            else:
                created = VoiceState(state=self.state, data=voice_state, guild_id=self.id)
        try:
            (new_cache or self._voice_states)[created.user.id] = created
        except AttributeError:
            log.warning(f"Voice state {created} does not have an attached user")
        return created

    def _add_channel(
            self,
            channel: payloads.Channel | Channel,
            new_cache: dict[int, Any] | None = None) -> Channel:
        """
        Add a channel to the guild's cache, updating the state cache at the same
        time.
        """

        if isinstance(channel, dict):
            cached = self.state.cache.get_channel(channel["id"])
            if cached:
                created = cached._update(channel)
            else:
                created = Channel(
                    state=self.state,
                    data=channel,
                    guild_id=self.id,
                )
        else:
            created = channel
        self.state.cache.add_channels(created)
        (new_cache or self._channels)[created.id] = created
        return created

    async def _sync(self, data: payloads.GuildSyncable) -> Self:
        """
        Sync the gateway-specific values into the guild.

        This method was made specifically for gateway updates, as this method
        has no need to be called for models received via the API.
        """

        new_cache: dict[int, Any]

        # These update methods all have an `asyncio.sleep(0)` in them.
        # This is so that the bot doesn't get stuck processing one guild/emoji
        # for a long time, and is able to suspend these into background tasks
        # in order to keep processing other things.
        # Really, these should all happen concurrently, as there's no need for
        # them to be queued, but that can come later on :)

        if "emojis" in data:
            new_cache = {}
            for d in data["emojis"]:
                new = self._add_emoji(d, new_cache)
                if new is not None:
                    new_cache[new.id] = new
                await asyncio.sleep(0)
            self._emojis = new_cache

        if "stickers" in data:
            new_cache = {}
            for d in data["stickers"]:
                new = self._add_sticker(d, new_cache)
                new_cache[new.id] = new
                await asyncio.sleep(0)
            self._stickers = new_cache

        if "roles" in data:
            new_cache = {}
            for d in data["roles"]:
                new = self._add_role(d, new_cache)
                new_cache[new.id] = new
                await asyncio.sleep(0)
            self._roles = new_cache

        if "members" in data:
            new_cache = {}
            for d in data["members"]:
                new = self._add_member(d, new_cache)
                new_cache[new.id] = new
                await asyncio.sleep(0)
            self._members = new_cache

        if "guild_scheduled_events" in data:
            new_cache = {}
            for d in data["guild_scheduled_events"]:
                new = self._add_guild_scheduled_event(d, new_cache)
                new_cache[new.id] = new
                await asyncio.sleep(0)
            self._guild_scheduled_events = new_cache

        if "threads" in data:
            new_cache = {}
            for d in data["threads"]:
                new = self._add_thread(d, new_cache)
                new_cache[new.id] = new
                await asyncio.sleep(0)
            self._threads = new_cache

        if "voice_states" in data:
            new_cache = {}
            for d in data["voice_states"]:
                new = self._add_voice_state(d, new_cache)
                new_cache[new.user.id] = new
                await asyncio.sleep(0)
            self._voice_states = new_cache

        if "channels" in data:
            new_cache = {}
            for d in data["channels"]:
                new = self._add_channel(d, new_cache)
                new_cache[new.id] = new
                await asyncio.sleep(0)
            self._channels = new_cache

        return self

    __repr__ = generate_repr(
        ('id', 'name',),
        ('channels', 'stickers', 'roles', 'members',),
    )

    def get_sticker(self, id: AnySnowflake) -> Sticker | None:
        """
        Get a sticker from cache.

        Parameters
        ----------
        id : int | str | novus.abc.Snowflake
            The identifier for the sticker we want to get.

        Returns
        -------
        novus.Sticker | None
            A sticker object, if one was cached.
        """

        return self._stickers.get(try_id(id))

    def get_member(self, id: AnySnowflake) -> GuildMember | None:
        """
        Get a guild member from cache.

        Parameters
        ----------
        id : int | str | novus.abc.Snowflake
            The identifier for the user we want to get.

        Returns
        -------
        novus.GuildMember | None
            A guild member object, if one was cached.
        """

        return self._members.get(try_id(id))

    def get_role(self, id: AnySnowflake) -> Role | None:
        """
        Get a role from cache.

        Parameters
        ----------
        id : int | str | novus.abc.Snowflake
            The identifier for the role we want to get.

        Returns
        -------
        novus.GuildMember | None
            A role object, if one was cached.
        """

        return self._roles.get(try_id(id))

    def get_event(self, id: AnySnowflake) -> ScheduledEvent | None:
        """
        Get a scheduled event from cache.

        Parameters
        ----------
        id : int | str | novus.abc.Snowflake
            The identifier for the event we want to get.

        Returns
        -------
        novus.ScheduledEvent | None
            A scheduled event object, if one was cached.
        """

        return self._guild_scheduled_events.get(try_id(id))

    def get_thread(self, id: AnySnowflake) -> Channel | None:
        """
        Get a thread from cache.

        Parameters
        ----------
        id : int | str | novus.abc.Snowflake
            The identifier for the thread we want to get.

        Returns
        -------
        novus.Channel | None
            A thread object, if one was cached.
        """

        return self._threads.get(try_id(id))

    def get_channel(self, id: AnySnowflake) -> Channel | None:
        """
        Get a channel from cache.

        Parameters
        ----------
        id : int | str | novus.abc.Snowflake
            The identifier for the channel we want to get.

        Returns
        -------
        novus.Channel | None
            A channel object, if one was cached.
        """

        return self._channels.get(try_id(id))

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


class OauthGuild(BaseGuild):
    """
    A model for a Discord guild when fetched by an authenticated user through
    the API.

    Attributes
    ----------
    id : int
        The ID of the guild.
    name : str
        The name of the guild.
    icon_hash : str | None
        The hash for the guild's icon.
    icon : novus.Asset | None
        A model for the guild's icon.
    owner : bool
        Whether the authenticated user owns the guild.
    permissions : novus.Permissions
        The authenticated user's permissions in the guild.
    """

    __slots__ = (
        'state',
        'id',
        'name',
        'icon_hash',
        'owner',
        'permissions',
        '_cs_icon',
    )

    def __init__(self, *, state: HTTPConnection, data: payloads.Guild) -> None:
        self.state: HTTPConnection = state
        self.id: int = try_snowflake(data['id'])
        self.name: str = data['name']
        self.icon_hash: str | None = data['icon'] or data.get('icon_hash')
        self.owner: bool = data.get('owner', False)
        self.permissions: Permissions = Permissions(int(data.get('permissions', 0)))

    __repr__ = generate_repr(('id', 'name', 'owner', 'permissions',))

    @cached_slot_property('_cs_icon')
    def icon(self) -> Asset:
        return Asset.from_guild_icon(self)

    async def fetch_full_guild(self) -> Guild:
        """
        Return the full guild associated with this partial one.

        Returns
        -------
        novus.Guild
            The full guild object.
        """

        return await Guild.fetch(self.state, self.id)


class GuildPreview(BaseGuild):
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
    icon : novus.Asset | None
        The icon asset associated with the guild.
    splash_hash : str | None
        The splash hash for the guild.
    splash : novus.Asset | None
        The splash asset associated with the guild.
    discovery_splash_hash : str | None
        The discovery splash hash for the guild.
    discovery_splash : novus.Asset | None
        The discovery splash asset associated with the guild.
    emojis : list[novus.Emoji]
        A list of emojis in the guild.
    features : list[str]
        A list of features that the guild has.
    approximate_member_count : int
        The approximate member count for the guild.
    approximate_presence_count : int
        The approximate online member count for the guild.
    description : str
        The description of the guild.
    stickers : list[novus.Sticker]
        A list of the stickers in the guild.
    """

    __slots__ = (
        'state',
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

    def __init__(self, *, state: HTTPConnection, data: payloads.GuildPreview):
        self.state = state
        self.id = try_snowflake(data['id'])
        self.name = data['name']
        self.icon_hash = data.get('icon')
        self.splash_hash = data.get('splash')
        self.discovery_splash_hash = data.get('discovery_splash')
        self.emojis = [
            Emoji(state=self.state, data=i, guild=self)
            for i in data.get('emojis', list())
        ]
        self.features = data.get('features', list())
        self.approximate_member_count = data['approximate_member_count']
        self.approximate_presence_count = data['approximate_presence_count']
        self.description = data.get('description')
        self.stickers = [
            Sticker(state=self.state, data=i)
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
