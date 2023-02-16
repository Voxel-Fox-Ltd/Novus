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
    'MessageFlags',
)


class MessageFlags(Flags):

    if TYPE_CHECKING:
        crossposted: bool
        is_crosspost: bool
        suppress_embeds: bool
        source_message_Deleted: bool
        urgent: bool
        has_thread: bool
        ephemeral: bool
        loading: bool
        failed_to_mention_some_roled_in_thread: bool

    CREATE_FLAGS = {
        "crossposted": 1 << 0,
        "is_crosspost": 1 << 1,
        "suppress_embeds": 1 << 2,
        "source_message_Deleted": 1 << 3,
        "urgent": 1 << 4,
        "has_thread": 1 << 5,
        "ephemeral": 1 << 6,
        "loading": 1 << 7,
        "failed_to_mention_some_roled_in_thread": 1 << 8,
    }
