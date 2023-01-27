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

from typing import TYPE_CHECKING, TypedDict, Literal, Any, Optional

if TYPE_CHECKING:
    from ._util import Snowflake
    from .user import User
    from .auto_moderation import AutoModerationRule
    from .channel import Channel
    from .guild import Integration
    from .guild_scheduled_event import GuildScheduledEvent
    from .webhook import Webhook

__all__ = (
    'AuditLogEvent',
    'AuditEntryInfo',
    'AuditLogChange',
    'AuditLogEntry',
    'AuditLog',
)


AuditLogEvent = Literal[
    1,  # Server settings were updated
    10,  # Channel was created
    11,  # Channel settings were updated
    12,  # Channel was deleted
    13,  # Permission overwrite was added to a channel
    14,  # Permission overwrite was updated for a channel
    15,  # Permission overwrite was deleted from a channel
    20,  # Member was removed from server
    21,  # Members were pruned from server
    22,  # Member was banned from server
    23,  # Server ban was lifted for a member
    24,  # Member was updated in server
    25,  # Member was added or removed from a role
    26,  # Member was moved to a different voice channel
    27,  # Member was disconnected from a voice channel
    28,  # Bot user was added to server
    30,  # Role was created
    31,  # Role was edited
    32,  # Role was deleted
    40,  # Server invite was created
    41,  # Server invite was updated
    42,  # Server invite was deleted
    50,  # Webhook was created Webhook
    51,  # Webhook properties or channel were updated
    52,  # Webhook was deleted
    60,  # Emoji was created
    61,  # Emoji name was updated
    62,  # Emoji was deleted
    72,  # Single message was deleted
    73,  # Multiple messages were deleted
    74,  # Message was pinned to a channel
    75,  # Message was unpinned from a channel
    80,  # App was added to server
    81,  # App was updated
    82,  # App was removed from server
    83,  # Stage instance was created
    84,  # Stage instance details were updated
    85,  # Stage instance was deleted
    90,  # Sticker was created
    91,  # Sticker details were updated
    92,  # Sticker was deleted
    100,  # Event was created
    101,  # Event was updated
    102,  # Event was cancelled
    110,  # Thread was created in a channel
    111,  # Thread was updated
    112,  # Thread was deleted
    121,  # Permissions were updated for a command
    140,  # Auto Moderation rule was created
    141,  # Auto Moderation rule was updated
    142,  # Auto Moderation rule was deleted
    143,  # Message was blocked by auto moderation
    144,  # Message was flagged by auto moderation
    145,  # Member was timed out by auto moderation
]


class AuditEntryInfo(TypedDict):
    application_id: Snowflake
    auto_moderation_rule_name: str
    auto_moderation_rule_trigger_type: str
    channel_id: Snowflake
    count: str
    delete_member_days: str
    id: Snowflake
    members_removed: str
    message_id: Snowflake
    role_name: str
    type: Literal["0", "1"]


class _AuditLogChangeOptional(TypedDict, total=False):
    new_value: Any
    old_value: Any


class AuditLogChange(_AuditLogChangeOptional):
    key: str


class _AuditLogEntryOptional(TypedDict, total=False):
    changes: list[AuditLogChange]
    options: AuditEntryInfo
    reason: str


class AuditLogEntry(_AuditLogEntryOptional):
    id: Snowflake
    target_id: Snowflake
    user_id: Optional[Snowflake]
    action_type: AuditLogEvent


# TODO needs proper typing
class AuditLog(TypedDict):
    application_commands: list
    audit_log_entries: list[AuditLogEntry]
    auto_moderation_rules: list[AutoModerationRule]
    guild_scheduled_events: list[GuildScheduledEvent]
    integrations: list[Integration]
    threads: list[Channel]
    users: list[User]
    webhooks: list[Webhook]
