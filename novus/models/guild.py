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

from typing import TYPE_CHECKING, Any, TypeAlias
import functools

from .abc import Snowflake
from .mixins import Hashable
from .role import Role
from .asset import Asset
from .emoji import Emoji
from .welcome_screen import WelcomeScreen
from .sticker import Sticker
from ..flags import Permissions, guild as guild_flags
from ..enums import Locale, guild as guild_enums
from ..utils import MISSING, try_snowflake, generate_repr

if TYPE_CHECKING:
    import io

    from ..api import HTTPConnection
    from ..payloads import (
        Guild as GuildPayload,
        GuildPreview as GuildPreviewPayload,
    )

    File: TypeAlias = str | bytes | io.IOBase

__all__ = (
    'Guild',
    'OauthGuild',
    'GuildPreview',
)


class Guild(Hashable):
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
    verification_level : novus.enums.guild.VerificationLevel
        The verification level required for the guild.
    default_message_notifications : novus.enums.guild.NotificationLevel
        The default message notification level.
    explicit_content_filter : novus.enums.guild.ContentFilterLevel
        The explicit content filter level.
    roles : list[novus.Role]
        The roles associated with the guild, as returned from the cache.
    emojis : list[novus.Emoji]
        The emojis associated with the guild, as returned from the cache.
    features : list[str]
        A list of guild features.
    mfa_level : novus.enums.guild.MFALevel
        The required MFA level for the guild.
    application_id : int | None
        The application ID of the guild creator, if the guild is bot-created.
    system_channel_id: int | None
        The ID of the channel where guild notices (such as welcome messages
        and boost events) are posted.
    system_channel_flags : novus.flags.guild.SystemChannelFlags
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
    premium_tier : novus.enums.guild.PremiumTier
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
    nsfw_level : novus.enums.guild.NSFWLevel
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
        '_roles',
        '_emojis',
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
        '_welcome_screen',
        '_stickers',
    )

    def __init__(self, *, state: HTTPConnection, data: GuildPayload):
        self._state = state
        self.id = try_snowflake(data['id'])
        self.name = data['name']
        self.icon_hash = data['icon'] or data.get('icon_hash')
        self.splash_hash = data['splash']
        self.discovery_splash_hash = data['discovery_splash']
        self.owner_id = try_snowflake(data['owner_id'])
        self.afk_channel_id = try_snowflake(data['afk_channel_id'])
        self.afk_timeout = data['afk_timeout']
        self.verification_level = guild_enums.VerificationLevel(data['verification_level'])
        self.default_message_notifications = guild_enums.NotificationLevel(data['default_message_notifications'])
        self.explicit_content_filter = guild_enums.ContentFilterLevel(data['explicit_content_filter'])
        self._roles = {
            d['id']: Role(state=self._state, data=d)
            for d in data['roles']
        }
        self._emojis = {
            d['id']: Emoji(state=self._state, data=d)
            for d in data['emojis']
        }
        self.features = data['features']
        self.mfa_level = guild_enums.MFALevel(data['mfa_level'])
        self.application_id = try_snowflake(data['application_id'])
        self.system_channel_id = try_snowflake(data['system_channel_id'])
        self.system_channel_flags = guild_flags.SystemChannelFlags(data['system_channel_flags'])
        self.rules_channel_id = try_snowflake(data['rules_channel_id'])
        self.vanity_url_code = data['vanity_url_code']
        self.description = data['description']
        self.banner_hash = data['banner']
        self.premium_tier = guild_enums.PremiumTier(data['premium_tier'])
        self.preferred_locale = Locale(data['preferred_locale'])
        self.public_updates_channel_id = try_snowflake(data['public_updates_channel_id'])
        self.nsfw_level = guild_enums.NSFWLevel(data.get('nsfw_level', 0))
        self.premium_progress_bar_enabled = data.get('premium_progress_bar_enabled', False)

        # Now onto the optional attrs
        self.widget_enabled = data.get('widget_enabled', False)
        self.widget_channel_id = try_snowflake(data.get('widget_channel_id'))
        self.max_presences = data.get('max_presences')
        self.max_members = data.get('max_members')
        self.premium_subscription_count = data.get('premium_subscription_count', 0)
        self.max_video_channel_users = data.get('max_video_channel_users')
        self.approximate_member_count = data.get('approximate_member_count')
        self._welcome_screen = data.get('welcome_screen')
        self._stickers = {
            d['id']: Sticker(state=self._state, data=d)
            for d in data.get('stickers', list())
        }

    __repr__ = generate_repr(('id', 'name',))

    @property
    @functools.cache
    def icon(self) -> Asset:
        return Asset.from_guild_icon(self)

    @property
    @functools.cache
    def splash(self) -> Asset:
        return Asset.from_guild_splash(self)

    @property
    @functools.cache
    def discovery_splash(self) -> Asset:
        return Asset.from_guild_discovery_splash(self)

    @property
    @functools.cache
    def banner(self) -> Asset:
        return Asset.from_guild_banner(self)

    @property
    @functools.cache
    def roles(self) -> list[Role]:
        return [
            i
            for i in
            self._roles.values()
        ]

    @property
    @functools.cache
    def emojis(self) -> list[Emoji]:
        return [
            i
            for i in
            self._emojis.values()
        ]

    @property
    @functools.cache
    def welcome_screen(self) -> WelcomeScreen | None:
        raise NotImplementedError()

    @property
    @functools.cache
    def stickers(self) -> list[Sticker]:
        return [
            i
            for i in
            self._stickers.values()
        ]

    @classmethod
    async def fetch(cls, state: HTTPConnection, id: int) -> Guild:
        """
        Get an instance of a guild.

        Parameters
        ----------
        state : HTTPConnection
            The API connection.
        id : int
            The ID associated with the guild you want to get.

        Returns
        -------
        novus.Guild
            The guild associated with the given ID.
        """

        return await state.guild.get_guild(id)

    async def edit(
            self,
            *,
            name: str = MISSING,
            verification_level: guild_enums.VerificationLevel | None = MISSING,
            default_message_notifications: guild_enums.NotificationLevel | None = MISSING,
            explicit_content_filter: guild_enums.ContentFilterLevel | None = MISSING,
            afk_channel: Snowflake | None = MISSING,
            icon: File | None = MISSING,
            owner: Snowflake = MISSING,
            splash: File | None = MISSING,
            discovery_splash: File | None = MISSING,
            banner: File | None = MISSING,
            system_channel: Snowflake | None = MISSING,
            system_channel_flags: guild_flags.SystemChannelFlags | None = MISSING,
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
        afk_channel : novus.abc.Snowflake | None
            The channel you want to set as the guild's AFK channel.
        icon : str | bytes | io.IOBase | None
            The icon that you want to set for the guild. Can be its bytes, a
            file path, or a file object.
        owner : novus.abc.Snowflake
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
        system_channel : novus.abc.Snowflake | None
            The system channel you want to set for the guild.
        system_channel_flags : novus.flags.guild.SystemChannelFlags | None
            The system channel flags you want to set.
        rules_channel : novus.abc.Snowflake | None
            The channel you want to set as the rules channel.
        preferred_locale : Locale | None
            The locale you want to set as the guild's preferred.
        public_updates_channel : novus.abc.Snowflake
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
        if not updates:
            return self
        return await self._state.guild.modify_guild(
            self.id,
            reason=reason,
            **updates,
        )

    async def delete(self) -> None:
        """
        Delete the current guild permanently. You must be the owner of the
        guild to run this successfully.
        """

        await self._state.guild.delete_guild(self.id)
        return None


class OauthGuild(Guild):
    """
    A model for a Discord guild when fetched by an authenticated user through
    the API.

    Attributes
    ----------
    owner : bool
        Whether the authenticated user owns the guild.
    permissions : novus.Permissions
        The authenticated user's permissions in the guild.
    """

    def __init__(self, *, state, data: GuildPayload):
        self.owner: bool = data.get('owner', False)
        self.permissions: Permissions = Permissions(int(data.get('permissions', 0)))
        super().__init__(state=state, data=data)


class GuildPreview(Hashable):
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
    )

    def __init__(self, *, state: HTTPConnection, data: GuildPreviewPayload):
        self._state = state
        self.id = try_snowflake(data['id'])
        self.name = data['name']
        self.icon_hash = data.get('icon')
        self.splash_hash = data.get('splash')
        self.discovery_splash_hash = data.get('discovery_splash')
        self.emojis = [
            Emoji(state=self._state, data=i)
            for i in data.get('emojis', list())
        ]
        self.features = data.get('features', list())
        self.approximate_member_count = data['approximate_member_count']
        self.approximate_presence_count = data['approximate_presence_count']
        self.description = data.get('description')
        self.stickers = [
            Sticker(state=self._state, data=i)
            for i in data.get('stickers', list())
        ]

    @property
    def icon(self) -> Asset:
        return Asset.from_guild_icon(self)

    @property
    def splash(self) -> Asset:
        return Asset.from_guild_splash(self)

    @property
    def discovery_splash(self) -> Asset:
        return Asset.from_guild_discovery_splash(self)
