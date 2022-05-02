from __future__ import annotations

from typing import Dict, List, Literal, Optional, TypedDict


__all__ = (
    "_EventWebhookEvents",
    "_EventWebhook",
    "_Intents",
    "_BotListingApiKeys",
    "_CommandData",
    "_BotInfoLinks",
    "_BotInfo",
    "_Oauth",
    "_Database",
    "_Redis",
    "_ShardManager",
    "_EmbedAuthor",
    "_EmbedFooter",
    "_Embed",
    "_PresenceStreaming",
    "_Presence",
    "_UpgradeChat",
    "_Statsd",
    "BotConfig",
)


class _EventWebhookEvents(TypedDict):
    guild_join: bool
    guild_remove: bool
    shard_connect: bool
    shard_disconnect: bool
    shard_ready: bool
    bot_ready: bool
    unhandled_error: bool


class _EventWebhook(TypedDict):
    event_webhook_url: str
    events: _EventWebhookEvents


class _Intents(TypedDict):
    guilds: bool
    members: bool
    bans: bool
    emojis: bool
    integrations: bool
    webhooks: bool
    invites: bool
    voice_states: bool
    presences: bool
    guild_messages: bool
    dm_messages: bool
    guild_reactions: bool
    dm_reactions: bool
    guild_typing: bool
    dm_typing: bool


class _BotListingApiKeys(TypedDict):
    topgg_token: str
    discordbotlist_token: str


class _CommandData(TypedDict):
    guild_invite: str
    donate_link: str
    website_link: str


class _BotInfoLinks(TypedDict):
    url: str
    emoji: Optional[str]


class _BotInfo(TypedDict):
    enabled: bool
    content: str
    thumbnail: str
    image: str
    links: Dict[str, _BotInfoLinks]


class _Oauth(TypedDict):
    enabled: bool
    response_type: str
    redirect_uri: str
    client_id: str
    scope: str
    permissions: List[str]


class _Database(TypedDict):
    type: Literal["postgres", "sqlite", "mysql"]
    enabled: bool
    user: str
    password: str
    database: str
    host: str
    port: int


class _Redis(TypedDict):
    enabled: bool
    host: str
    port: int
    db: int


class _ShardManager(TypedDict):
    enabled: bool
    host: str
    port: int


class _EmbedAuthor(TypedDict):
    enabled: bool
    name: str
    url: str


class _EmbedFooter(TypedDict):
    text: str
    amount: int


class _Embed(TypedDict):
    enabled: bool
    content: str
    colour: int
    author: _EmbedAuthor
    footer: List[_EmbedFooter]


class _PresenceStreaming(TypedDict):
    twitch_usernames: List[str]
    twitch_client_id: str
    twitch_client_secret: str


class _Presence(TypedDict):
    activity_type: str
    text: str
    status: str
    include_shard_id: bool
    streaming: _PresenceStreaming


class _UpgradeChat(TypedDict):
    client_id: str
    client_secret: str


class _Statsd(TypedDict):
    host: str
    port: int
    constant_tags: Dict[str, str]


class BotConfig(TypedDict):
    token: str
    pubkey: str
    owners: List[int]
    dm_uncaught_errors: bool
    user_agent: str
    guild_settings_prefix_column: str
    ephemeral_error_messages: bool
    owners_ignore_check_failures: bool

    default_prefix: str
    cached_messages: int

    support_guild_id: int
    bot_support_role_id: int

    event_webhook: _EventWebhook
    intents: _Intents
    bot_listing_api_keys: _BotListingApiKeys
    command_data: _CommandData
    bot_into: _BotInfo
    oauth: _Oauth
    database: _Database
    reids: _Redis
    shard_manager: _ShardManager
    embed: _Embed
    presence: _Presence
    upgrade_chat: _UpgradeChat
    statsd: _Statsd
