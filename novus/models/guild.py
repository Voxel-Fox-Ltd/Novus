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
from ..utils import cached_slot_property, generate_repr, try_snowflake
from .api_mixins.guild import GuildAPIMixin
from .asset import Asset
from .channel import Channel
from .emoji import Emoji
from .mixins import Hashable
from .role import Role
from .sticker import Sticker
from .welcome_screen import WelcomeScreen

if TYPE_CHECKING:
    import io

    from ..api import HTTPConnection
    from ..payloads import GatewayGuild as GatewayGuildPayload
    from ..payloads import Guild as APIGuildPayload
    from ..payloads import GuildPreview as GuildPreviewPayload
    from .user import GuildMember, User

    FileT: TypeAlias = str | bytes | io.IOBase

__all__ = (
    'GuildBan',
    'Guild',
    'OauthGuild',
    'GuildPreview',
)


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

        # Gateway attributes
        self._emojis: dict[int, Emoji] = {}
        self._stickers: dict[int, Sticker] = {}
        self._roles: dict[int, Role] = {}
        self._members: dict[int, GuildMember] = {}
        self._guild_scheduled_events: dict[int, None] = {}
        self._threads: dict[int, None] = {}
        self._voice_states: dict[int, None] = {}
        self._channels: dict[int, Channel] = {}
        self._sync(data=data)  # type: ignore

    def _sync(self, *, data: GatewayGuildPayload) -> None:
        """
        Sync the cached state with the given gateway payload.
        """

        d: Any
        if 'emojis' in data:
            for d in data['emojis']:
                if d['id'] is None:
                    continue
                id = int(d['id'])
                self._emojis[id] = Emoji(state=self._state, data=d, guild=self)
        if 'stickers' in data:
            for d in data['stickers']:
                id = int(d['id'])
                self._stickers[id] = Sticker(state=self._state, data=d, guild=self)
        if 'roles' in data:
            for d in data['roles']:
                id = int(d['id'])
                self._roles[id] = Role(
                    state=self._state,
                    data=d,
                    guild=self,
                )
        if 'members' in data:
            for d in data.get('members', ()):
                id = int(d['user']['id'])
                self._members[id] = GuildMember(
                    state=self._state,
                    data=d,
                    guild=self,
                )
        if 'guild_scheduled_events' in data:
            for d in data.get('guild_scheduled_events', ()):
                id = int(d['id'])
                self._guild_scheduled_events[id] = None
        if 'threads' in data:
            for d in data.get('threads', ()):
                id = int(d['id'])
                self._threads[id] = None
        if 'voice_states' in data:
            for d in data.get('voice_states', ()):
                id = int(d['user_id'])
                self._voice_states[id] = None
        if 'channels' in data:
            for d in data.get('channels', ()):
                id = int(d['id'])
                self._channels[id] = c = Channel._from_data(
                    state=self._state,
                    data=d,
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
    icon : novus.models.Asset | None
        A model for the guild's icon.
    owner : bool
        Whether the authenticated user owns the guild.
    permissions : novus.flags.Permissions
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

    def __init__(self, *, state: HTTPConnection, data: APIGuildPayload) -> None:
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
        novus.models.Guild
            The full guild object.
        """

        return await Guild.fetch(self._state, self.id)


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
