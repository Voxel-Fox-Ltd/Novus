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

from typing import TYPE_CHECKING, Literal, Optional, TypedDict

if TYPE_CHECKING:
    from ._util import Snowflake, Timestamp
    from .user import GuildMember, User

__all__ = (
    'Channel',
    'ChannelType',
    'ChannelOverwrite',
    'ThreadMetadata',
    'ThreadMember',
)


class ChannelOverwrite(TypedDict):
    id: Snowflake
    type: Literal[0, 1]
    allow: str
    deny: str


class _ThreadMetadataOptional(TypedDict, total=False):
    invitable: bool
    create_timestamp: Optional[Timestamp]  # Only for creation after 2022-01-09


class ThreadMetadata(_ThreadMetadataOptional):
    archived: bool
    auto_archive_duration: Literal[60, 1440, 4320, 10080]
    archive_timestamp: Timestamp  # Timestamp of when archive status was last changed
    locked: bool


class _ThreadMemberOptional(TypedDict, total=False):
    id: Snowflake
    user_id: Snowflake
    member: GuildMember


class ThreadMember(_ThreadMemberOptional):
    join_timestamp: Timestamp
    flags: int


class ForumDefaultReaction(TypedDict):
    emoji_id: Optional[Snowflake]
    emoji_name: Optional[str]


class ForumTag(TypedDict):
    id: Snowflake
    name: str
    moderated: bool
    emoji_id: Optional[Snowflake]
    emoji_name: Optional[str]


class _ChannelOptional(TypedDict, total=False):
    guild_id: Snowflake
    position: int
    permission_overwrites: list[ChannelOverwrite]
    name: str
    topic: str
    nsfw: bool
    last_message_id: Optional[Snowflake]
    bitrate: int
    user_limit: int
    rate_limit_per_user: int
    recipients: list[User]
    icon: Optional[str]
    owner_id: Snowflake
    application_id: Snowflake
    parent_id: Optional[Snowflake]
    last_pin_timestamp: Optional[Timestamp]
    rtc_region: Optional[str]
    video_quality_mode: Literal[1, 2]
    message_count: int
    member_count: int
    thread_metadata: ThreadMetadata
    member: ThreadMember
    default_auto_archive_duration: int
    permissions: str
    flags: Literal[0b10, 0b10000]
    total_message_sent: int
    available_tags: list[ForumTag]
    applied_tags: list[Snowflake]
    default_reaction_emoji: Optional[ForumDefaultReaction]
    defatul_thread_rate_limit_per_user: int
    default_sort_order: Literal[0, 1]
    default_forum_layout: Literal[0, 1, 2]


ChannelType = Literal[
    0,  # GUILD_TEXT
    1,  # DM
    2,  # GUILD_VOICE
    3,  # GROUP_DM
    4,  # GUILD_CATEGORY
    5,  # GUILD_ANNOUNCEMENT
    10,  # ANNOUNCEMENT_THREAD
    11,  # PUBLIC_THREAD
    12,  # PRIVATE_THREAD
    13,  # GUILD_STAGE_VOICE
    14,  # GUILD_DIRECTOR
    15,  # GUILD_FORUM
]


class Channel(_ChannelOptional):
    id: Snowflake
    type: ChannelType
