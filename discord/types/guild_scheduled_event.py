"""
The MIT License (MIT)

Copyright (c) 2015-2021 Rapptz

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from __future__ import annotations

from typing import Optional, TypedDict, Literal
from .snowflake import Snowflake
from .user import User


GuildScheduledEventPrivacyLevel = Literal[2]
GuildScheduledEventStatus = Literal[1, 2, 3, 4]
GuildScheduledEventEntityType = Literal[1, 2, 3]


class GuildScheduledEventEntityMetadata(TypedDict):
    location: Optional[str]


class _GuildScheduledEventOptional(TypedDict, total=False):
    channel_id: Snowflake
    creator_id: Snowflake
    description: str
    scheduled_end_time: str
    entity_id: Snowflake
    entity_metadata: GuildScheduledEventEntityMetadata
    creator: User
    user_count: int


class GuildScheduledEvent(_GuildScheduledEventOptional):
    id: Snowflake
    guild_id: Snowflake
    name: str
    scheduled_start_time: str
    privacy_level: GuildScheduledEventPrivacyLevel
    status: GuildScheduledEventStatus
    entity_type: GuildScheduledEventEntityType
