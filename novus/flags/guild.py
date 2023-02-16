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

from typing import TYPE_CHECKING

from vfflags import Flags

__all__ = (
    'SystemChannelFlags',
)


class SystemChannelFlags(Flags):

    if TYPE_CHECKING:
        suppress_join_notifications: bool
        suppress_premium_subscriptions: bool
        suppress_guild_reminder_notifications: bool
        suppress_join_notification_replies: bool

    CREATE_FLAGS = {
        "suppress_join_notifications": 1 << 0,
        "suppress_premium_subscriptions": 1 << 1,
        "suppress_guild_reminder_notifications": 1 << 2,
        "suppress_join_notification_replies": 1 << 3,
    }
