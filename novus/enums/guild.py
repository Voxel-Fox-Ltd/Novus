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

from enum import Enum

__all__ = (
    'NSFWLevel',
    'PremiumTier',
    'MFALevel',
    'ContentFilterLevel',
    'VerificationLevel',
    'NotificationLevel',
)


class NSFWLevel(Enum):
    default = 0
    explicit = 1
    safe = 2
    age_restricted = 3


class PremiumTier(Enum):
    none = 0
    tier_1 = 1
    tier_2 = 2
    tier_3 = 3


class MFALevel(Enum):
    none = 0
    elevated = 1


class ContentFilterLevel(Enum):
    disabled = 0
    members_without_roles = 1
    all_members = 2


class VerificationLevel(Enum):
    none = 0
    low = 1
    medium = 2
    high = 3
    very_high = 4


class NotificationLevel(Enum):
    all_messages = 0
    only_mentions = 1
