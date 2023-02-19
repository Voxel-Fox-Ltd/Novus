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

if TYPE_CHECKING:
    from ._util import Snowflake

__all__ = (
    'AutoModerationTriggerType',
    'AutoModerationKeywordPresetType',
    'AutoModeratorEventType',
    'AutoModerationActionType',
    'AutoModerationActionMetadata',
    'AutoModerationTriggerMetadata',
    'AutoModerationAction',
    'AutoModerationRule',
)


AutoModerationTriggerType = Literal[
    1,  # Keyword
    3,  # Spam
    4,  # Keyword preset
    5,  # Mention spam
]


AutoModerationKeywordPresetType = Literal[
    1,  # Profanity
    2,  # Sexual content
    3,  # Slurs
]


AutoModeratorEventType = Literal[
    1,  # Message send
]


AutoModerationActionType = Literal[
    1,  # Block message
    2,  # Send alert message
    3,  # Timeout
]


class AutoModerationActionMetadata(TypedDict):
    channel_id: Optional[Snowflake]
    duration_seconds: Optional[int]


class AutoModerationTriggerMetadata(TypedDict, total=False):
    keyword_filter: list[str]
    regex_patterns: list[str]
    presets: list[AutoModerationKeywordPresetType]
    allow_list: list[str]
    mention_total_limit: int


class _AutoModerationActionOptional(TypedDict, total=False):
    metadata: AutoModerationActionMetadata


class AutoModerationAction(_AutoModerationActionOptional):
    type: AutoModerationActionType


class AutoModerationRule(TypedDict):
    id: Snowflake
    guild_id: Snowflake
    name: str
    creator_id: Snowflake
    event_type: AutoModeratorEventType
    trigger_type: AutoModerationTriggerType
    trigger_metadata: AutoModerationTriggerMetadata
    actions: list[AutoModerationAction]
    enabled: bool
    exempt_roles: list[Snowflake]
    exempt_channels: list[Snowflake]
