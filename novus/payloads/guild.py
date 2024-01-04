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

from typing import TYPE_CHECKING, Literal, Optional, TypedDict

from typing_extensions import NotRequired

from novus.payloads.stage_instance import StageInstance

if TYPE_CHECKING:
    from ._util import Snowflake, Timestamp
    from .channel import Channel
    from .emoji import Emoji
    from .guild_scheduled_event import GuildScheduledEvent
    from .sticker import Sticker
    from .user import GuildMember, Presence, User
    from .voice import VoiceState

__all__ = (
    'RoleTags',
    'Role',
    'GuildWidget',
    'GuildPreview',
    'GuildSyncable',
    'UnavailableGuild',
    'GuildWelcomeScreenChannel',
    'GuildWelcomeScreen',
    'GuildFeature',
    'Guild',
    'GatewayGuild',
    'IntegrationApplication',
    'IntegrationAccount',
    'Integration',
    'Ban',
)


class RoleTags(TypedDict, total=False):
    bot_id: Snowflake
    integration_id: Snowflake
    premium_subscriber: Literal[None]
    subscription_listing_id: Snowflake
    available_for_purchase: Literal[None]
    guild_connections: Literal[None]


class _RoleOptional(TypedDict, total=False):
    icon: str
    unicode_emoji: str
    tags: RoleTags


class Role(_RoleOptional):
    id: Snowflake
    name: str
    color: int
    hoist: bool
    position: int
    permissions: str
    managed: bool
    mentionable: bool


class GuildWidget(TypedDict):
    enabled: bool
    channel_id: Optional[Snowflake]


class GuildPreview(TypedDict):
    id: Snowflake
    name: str
    icon: Optional[str]
    splash: Optional[str]
    discovery_splash: Optional[str]
    emojis: list[Emoji]
    features: list[GuildFeature]
    approximate_member_count: int
    approximate_presence_count: int
    description: Optional[str]
    stickers: list[Sticker]


class UnavailableGuild(TypedDict):
    id: Snowflake
    unavailable: Literal[True]


class GuildWelcomeScreenChannel(TypedDict):
    channel_id: Snowflake
    description: str
    emoji_id: Optional[Snowflake]
    emoji_name: Optional[str]


class GuildWelcomeScreen(TypedDict):
    description: Optional[str]
    welcome_channels: list[GuildWelcomeScreenChannel]


class _GuildOptional(TypedDict, total=False):
    icon_hash: Optional[str]
    owner: bool
    permissions: str
    widget_enabled: bool
    widget_channel_id: Optional[Snowflake]
    max_presences: Optional[int]
    max_members: int
    premium_subscription_count: int
    max_video_channel_users: int
    approximate_member_count: int
    welcome_screen: GuildWelcomeScreen
    stickers: list[Sticker]


GuildFeature = Literal[
    "ANIMATED_BANNER",
    "ANIMATED_ICON",
    "APPLICATION_COMMAND_PERMISSIONS_V2",
    "AUTO_MODERATION",
    "BANNER",
    "COMMUNITY",
    "CREATOR_MONETIZABLE_PROVISIONAL",
    "CREATOR_STORE_PAGE",
    "DEVELOPER_SUPPORT_SERVER",
    "DISCOVERABLE",
    "FEATURABLE",
    "INVITES_DISABLED",
    "INVITE_SPLASH",
    "MEMBER_VERIFICATION_GATE_ENABLED",
    "MORE_STICKERS",
    "NEWS",
    "PARTNERED",
    "PREVIEW_ENABLED",
    "ROLE_ICONS",
    "ROLE_SUBSCRIPTIONS_AVAILABLE_FOR_PURCHASE",
    "ROLE_SUBSCRIPTIONS_ENABLED",
    "TICKETED_EVENTS_ENABLED",
    "VANITY_URL",
    "VERIFIED",
    "VIP_REGIONS",
    "WELCOME_SCREEN_ENABLED",
]


class Guild(_GuildOptional):
    id: Snowflake
    name: str
    icon: Optional[str]
    splash: Optional[str]
    discovery_splash: Optional[str]
    owner_id: Snowflake
    afk_channel_id: Optional[Snowflake]
    afk_timeout: Literal[60, 300, 900, 1800, 3600]
    verification_level: Literal[0, 1, 2, 3, 4]
    default_message_notifications: Literal[0, 1]
    explicit_content_filter: Literal[0, 1, 2]
    roles: list[Role]
    emojis: list[Emoji]
    features: list[GuildFeature]
    mfa_level: Literal[0, 1]
    application_id: Optional[Snowflake]
    system_channel_id: Optional[Snowflake]
    system_channel_flags: int
    rules_channel_id: Optional[Snowflake]
    vanity_url_code: Optional[str]
    description: Optional[str]
    banner: Optional[str]
    premium_tier: Literal[0, 1, 2, 3]
    preferred_locale: str
    public_updates_channel_id: Optional[Snowflake]
    nsfw_level: Literal[0, 1, 2, 3]
    premium_progress_bar_enabled: bool


class _GatewayGuildOptional(TypedDict, total=False):
    unavailable: bool


class GuildSyncable(TypedDict):
    emojis: NotRequired[list[Emoji]]
    stickers: NotRequired[list[Sticker]]
    roles: NotRequired[list[Role]]
    voice_states: NotRequired[list[VoiceState]]
    members: NotRequired[list[GuildMember]]
    channels: NotRequired[list[Channel]]
    threads: NotRequired[list[Channel]]
    presences: NotRequired[list[Presence]]
    stage_instances: NotRequired[list[StageInstance]]
    guild_scheduled_events: NotRequired[list[GuildScheduledEvent]]


class GatewayGuild(Guild, GuildSyncable, _GatewayGuildOptional):  # type: ignore
    joined_at: Timestamp
    large: bool
    member_count: int


class _IntegrationApplicationOptional(TypedDict, total=False):
    bot: User


class IntegrationApplication(_IntegrationApplicationOptional):
    id: Snowflake
    name: str
    icon: Optional[str]
    description: str


class _IntegrationOptional(TypedDict, total=False):
    syncing: bool
    role_id: Snowflake
    enable_emoticons: bool
    expire_behavior: Literal[0, 1]
    expire_grace_period: int
    user: User
    synced_at: str
    subscriber_count: int
    revoked: bool
    application: IntegrationApplication
    scopes: list[str]


class IntegrationAccount(TypedDict):
    id: str  # Probably a snowflake, but typed as a string in the docs
    name: str


class Integration(_IntegrationOptional):
    id: Snowflake
    name: str
    type: Literal["twitch", "youtube", "discord", "guild_subscription"]
    enabled: bool
    account: IntegrationAccount


class Ban(TypedDict):
    reason: Optional[str]
    user: User
