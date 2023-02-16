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

import asyncio
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, TypeAlias

from ..enums import (
    ContentFilterLevel,
    Locale,
    MFALevel,
    NotificationLevel,
    NSFWLevel,
    PremiumTier,
    VerificationLevel,
)
from ..flags import Permissions, SystemChannelFlags
from ..models.channel import channel_builder
from ..utils import cached_slot_property, generate_repr, try_id, try_snowflake
from .api_mixins.guild import GuildAPIMixin
from .asset import Asset
from .channel import Channel, Thread
from .emoji import Emoji
from .guild_member import GuildMember
from .mixins import Hashable
from .role import Role
from .scheduled_event import ScheduledEvent
from .sticker import Sticker
from .user import User
from .welcome_screen import WelcomeScreen

if TYPE_CHECKING:
    import io

    from .. import payloads
    from ..api import HTTPConnection
    from .abc import Snowflake

    FileT: TypeAlias = str | bytes | io.IOBase

__all__ = (
    'GuildBan',
    'Guild',
    'PartialGuild',
    'OauthGuild',
    'GuildPreview',
)


log = logging.getLogger("novus.guild")


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
    verification_level : novus.VerificationLevel
        The verification level required for the guild.
    default_message_notifications : novus.NotificationLevel
        The default message notification level.
    explicit_content_filter : novus.ContentFilterLevel
        The explicit content filter level.
    roles : list[novus.Role]
        The roles associated with the guild, as returned from the cache.
    emojis : list[novus.Emoji]
        The emojis associated with the guild, as returned from the cache.
    features : list[str]
        A list of guild features.
    mfa_level : novus.MFALevel
        The required MFA level for the guild.
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
    premium_tier : novus.PremiumTier
        The premium tier of the guild.
    premium_subscription_count : int
        The number of boosts the guild currently has.
    preferred_locale : novus.Locale
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
    nsfw_level : novus.NSFWLevel
        The guild NSFW level.
    stickers : list[novus.Sticker]
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

    def __init__(self, *, state: HTTPConnection, data: payloads.Guild):
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

        # Gateway attributes
        self._emojis: dict[int, Emoji] = {}
        self._stickers: dict[int, Sticker] = {}
        self._roles: dict[int, Role] = {}
        self._members: dict[int, GuildMember] = {}
        self._guild_scheduled_events: dict[int, ScheduledEvent] = {}
        self._threads: dict[int, Thread] = {}
        self._voice_states: dict[int, None] = {}
        self._channels: dict[int, Channel] = {}

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
    def threads(self) -> list[Thread]:
        return list(self._threads.values())

    @property
    def voice_states(self) -> list[Any]:
        return list(self._voice_states.values())

    @property
    def channels(self) -> list[Channel]:
        return list(self._channels.values())

    def _add_emoji(self, emoji: payloads.Emoji | Emoji) -> Emoji | None:
        if isinstance(emoji, Emoji):
            created = emoji
        else:
            if emoji.get("id") is None:
                return None
            created = Emoji(state=self._state, data=emoji, guild=self)
        assert created.id
        created.guild = self
        self._state.cache.add_emojis(created)
        self._emojis[created.id] = created
        return created

    def _add_sticker(self, sticker: payloads.Sticker | Sticker) -> Sticker:
        if isinstance(sticker, Sticker):
            created = sticker
        else:
            created = Sticker(state=self._state, data=sticker, guild=self)
        self._state.cache.add_stickers(created)
        self._stickers[created.id] = created
        return created

    def _add_role(self, role: payloads.Role | Role) -> Role:
        if isinstance(role, Role):
            created = role
            created.guild = self
        else:
            created = Role(state=self._state, data=role, guild=self)
        self._roles[created.id] = created
        return created

    def _add_member(self, member: payloads.GuildMember | GuildMember) -> GuildMember:
        """Add member to cache. Will cache/update the user object as well."""
        if isinstance(member, GuildMember):
            created = member
        else:
            created = GuildMember(state=self._state, data=member, guild=self)
        created.guild = self
        user = self._state.cache.get_user(created.id)  # get cached user
        self._state.cache.add_users(created._user)  # add new user
        if user is not None and isinstance(user, User):
            created._user._guilds.update(user._guilds)  # update guild ids
        created._user._guilds.add(self.id)
        self._members[created.id] = created
        return created

    def _add_guild_scheduled_event(self, event: payloads.GuildScheduledEvent) -> ScheduledEvent:
        created = ScheduledEvent(state=self._state, data=event, guild=self)
        self._state.cache.add_events(created)
        self._guild_scheduled_events[created.id] = created
        return created

    def _add_thread(self, thread: payloads.Channel) -> Thread:
        created = Thread(state=self._state, data=thread, guild=self)
        self._state.cache.add_channels(created)
        self._threads[created.id] = created
        return created

    def _add_voice_state(self, voice_state: Any) -> None:
        pass

    def _add_channel(self, channel: payloads.Channel) -> Channel:
        try:
            created = channel_builder(
                state=self._state,
                data=channel,
                guild=self,
            )
        except ValueError as e:
            log.error(
                "Error building channel in guild %s" % self.id,
                exc_info=e,
            )
            raise
        else:
            self._state.cache.add_channels(created)
            self._channels[created.id] = created
            return created

    async def _sync(self, *, data: payloads.GatewayGuild) -> None:
        """
        Sync the cached state with the given gateway payload.
        """

        d: Any
        if 'emojis' in data:
            for d in data['emojis']:
                self._add_emoji(d)
                await asyncio.sleep(0)
        if 'stickers' in data:
            for d in data['stickers']:
                self._add_sticker(d)
                await asyncio.sleep(0)
        if 'roles' in data:
            for d in data['roles']:
                self._add_role(d)
                await asyncio.sleep(0)
        if 'members' in data:
            for d in data.get('members', ()):
                self._add_member(d)
                await asyncio.sleep(0)
        if 'guild_scheduled_events' in data:
            for d in data.get('guild_scheduled_events', ()):
                self._add_guild_scheduled_event(d)
                await asyncio.sleep(0)
        if 'threads' in data:
            for d in data.get('threads', ()):
                self._add_thread(d)
                await asyncio.sleep(0)
        if 'voice_states' in data:
            for d in data.get('voice_states', ()):
                self._add_voice_state(d)
                await asyncio.sleep(0)
        if 'channels' in data:
            for d in data.get('channels', ()):
                self._add_channel(d)
                await asyncio.sleep(0)

    __repr__ = generate_repr(
        ('id', 'name',),
        ('channels', 'stickers', 'roles', 'members',),
    )

    def sticker(self, id: int | Snowflake) -> Sticker | None:
        """
        Get a sticker from cache.

        Parameters
        ----------
        id : int | novus.abc.Snowflake
            The identifier for the sticker we want to get.

        Returns
        -------
        novus.Sticker | None
            A sticker object, if one was cached.
        """

        return self._stickers.get(try_id(id))

    def get_member(self, id: int | Snowflake) -> GuildMember | None:
        """
        Get a guild member from cache.

        Parameters
        ----------
        id : int | novus.abc.Snowflake
            The identifier for the user we want to get.

        Returns
        -------
        novus.GuildMember | None
            A guild member object, if one was cached.
        """

        return self._members.get(try_id(id))

    def get_role(self, id: int | Snowflake) -> Role | None:
        """
        Get a role from cache.

        Parameters
        ----------
        id : int | novus.abc.Snowflake
            The identifier for the role we want to get.

        Returns
        -------
        novus.GuildMember | None
            A role object, if one was cached.
        """

        return self._roles.get(try_id(id))

    def get_event(self, id: int | Snowflake) -> ScheduledEvent | None:
        """
        Get a scheduled event from cache.

        Parameters
        ----------
        id : int | novus.abc.Snowflake
            The identifier for the event we want to get.

        Returns
        -------
        novus.ScheduledEvent | None
            A scheduled event object, if one was cached.
        """

        return self._guild_scheduled_events.get(try_id(id))

    def get_thread(self, id: int | Snowflake) -> Thread | None:
        """
        Get a thread from cache.

        Parameters
        ----------
        id : int | novus.abc.Snowflake
            The identifier for the thread we want to get.

        Returns
        -------
        novus.Thread | None
            A thread object, if one was cached.
        """

        return self._threads.get(try_id(id))

    def get_channel(self, id: int | Snowflake) -> Channel | None:
        """
        Get a channel from cache.

        Parameters
        ----------
        id : int | novus.abc.Snowflake
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


class OauthGuild(GuildAPIMixin):
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
        '_state',
        'id',
        'name',
        'icon_hash',
        'owner',
        'permissions',
        '_cs_icon',
    )

    def __init__(self, *, state: HTTPConnection, data: payloads.Guild) -> None:
        self._state: HTTPConnection = state
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

        return await Guild.fetch(self._state, self.id)


class PartialGuild(GuildAPIMixin):
    """
    A model for a partial guild object, such as one retrieved from an invite
    link.

    This model still implements the normal guild API methods, though does not
    contain all of the data a guild would (see the attributes).

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
    verification_level : novus.VerificationLevel
        The guild's verification level.
    vainity_url_code : str | None
        The guild's vainity URL code.
    nsfw_level : novus.NSFWLevel
        The guild's NSFW level.
    premium_subscription_count : int
        The number of nitro boosts the guild has.
    """

    __slots__ = (
        '_state',
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
        self._state = state
        self.id: int = try_snowflake(data['id'])
        self.name: str = data['name']
        self.splash_hash: str | None = data.get('splash')
        self.banner_hash: str | None = data.get('banner')
        self.description: str | None = data.get('description')
        self.icon_hash: str | None = data.get('icon')
        self.features: list[str] = data['features']
        self.verification_level: VerificationLevel = VerificationLevel(data.get('verification_level', 0))
        self.vainity_url_code: str | None = data.get('vainity_url_code')
        self.nsfw_level: NSFWLevel = NSFWLevel(data.get('nsfw_level', 0))
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

    def __init__(self, *, state: HTTPConnection, data: payloads.GuildPreview):
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
