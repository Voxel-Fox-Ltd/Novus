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

from typing import TYPE_CHECKING, TypedDict

from typing_extensions import NotRequired

if TYPE_CHECKING:
    from . import Emoji, GuildMember, PartialEmoji, Role, Sticker, ThreadMember, Presence
    from ._util import Snowflake, Timestamp

__all__ = (
    'GatewayBot',
    'TypingStart',
    'ReactionAddRemove',
    'ChannelPinsUpdate',
    'RoleCreateUpdate',
    'RoleDelete',
    'GuildEmojisUpdate',
    'ThreadMemberListUpdate',
)


class SessionStartLimit(TypedDict):
    total: int
    remaining: int
    reset_after: int
    max_concurrency: int


class GatewayBot(TypedDict):
    url: str
    shards: int
    session_start_limit: SessionStartLimit


class Gateway(TypedDict):
    url: str


class TypingStart(TypedDict):
    channel_id: Snowflake
    timestamp: Timestamp
    user_id: Snowflake
    guild_id: NotRequired[Snowflake]
    member: NotRequired[GuildMember]


class ReactionAddRemove(TypedDict):
    user_id: Snowflake
    message_id: Snowflake
    emoji: PartialEmoji
    channel_id: Snowflake
    burst: bool
    member: NotRequired[GuildMember]
    guild_id: NotRequired[Snowflake]


class ChannelPinsUpdate(TypedDict):
    channel_id: Snowflake
    guild_id: NotRequired[Snowflake]
    last_pin_timestamp: Timestamp


class RoleCreateUpdate(TypedDict):
    guild_id: Snowflake
    role: Role


class RoleDelete(TypedDict):
    guild_id: Snowflake
    role_id: Snowflake


class GuildEmojisUpdate(TypedDict):
    emojis: list[Emoji]
    guild_id: Snowflake


class GuildStickersUpdate(TypedDict):
    stickers: list[Sticker]
    guild_id: Snowflake


class ThreadMemberListUpdate(TypedDict):
    member_count: int
    id: Snowflake
    guild_id: Snowflake
    added_members: NotRequired[list[ThreadMember]]
    removed_member_ids: NotRequired[list[Snowflake]]


class GuildMemberChunk(TypedDict):
    guild_id: Snowflake
    members: list[GuildMember]
    chunk_index: int
    chunk_count: int
    not_found: NotRequired[list]
    presences: NotRequired[list[Presence]]
    nonce: NotRequired[str]
