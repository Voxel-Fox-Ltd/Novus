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

from .utils import Enum

__all__ = (
    "AutoModerationKeywordPresetType",
    "AutoModerationTriggerType",
    "AutoModerationEventType",
    "AutoModerationActionType",
)


class AutoModerationKeywordPresetType(Enum):
    profanity = 1
    sexual_content = 2
    slurs = 3


class AutoModerationTriggerType(Enum):
    keyword = 1
    spam = 3
    keyword_preset = 4
    mention_spam = 5


class AutoModerationEventType(Enum):
    message_send = 1


class AutoModerationActionType(Enum):
    block_message = 1
    send_alert_message = 2
    timeout = 3
