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
    from ._snowflake import Snowflake, Timestamp
    from .user import User, GuildMember

__all__ = (
    'GuildScheduledEvent',
    'GuildScheduledEventEntityMetadata',
    'GuildScheduledEventUser',
)


class _GuildScheduledEventOptional(TypedDict, total=False):
    creator_id: Optional[Snowflake]
    description: Optional[str]
    creator: User
    image: Optional[str]


class GuildScheduledEventEntityMetadata(TypedDict, total=False):
    location: str


class GuildScheduledEvent(_GuildScheduledEventOptional):
    id: Snowflake
    guild_id: Snowflake
    channel_id: Optional[Snowflake]
    name: str
    scheduled_start_time: Timestamp
    scheduled_end_time: Optional[Timestamp]
    privacy_level: Literal[2]
    status: Literal[1, 2, 3, 4]
    entity_type: Literal[1, 2, 3]
    entity_id: Optional[Snowflake]
    entity_metadata: Optional[GuildScheduledEventEntityMetadata]


class _GuildScheduledEventUserOptional(TypedDict, total=False):
    member: GuildMember


class GuildScheduledEventUser(_GuildScheduledEventUserOptional):
    guild_scheduled_event_id: Snowflake
    user: User
