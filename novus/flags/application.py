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
    'ApplicationFlags',
)


class ApplicationFlags(Flags):

    if TYPE_CHECKING:

        def __init__(self, value: int = 0, **kwargs) -> None:
            ...

        gateway_presence: bool
        gateway_presence_limited: bool
        gateway_guild_members: bool
        gateway_guild_members_limited: bool
        verification_pending_guild_limit: bool
        embedded: bool
        gateway_message_content: bool
        gateway_message_content_limited: bool
        application_command_badge: bool

    CREATE_FLAGS = {
        "gateway_presence": 1 << 12,
        "gateway_presence_limited": 1 << 13,
        "gateway_guild_members": 1 << 14,
        "gateway_guild_members_limited": 1 << 15,
        "verification_pending_guild_limit": 1 << 16,
        "embedded": 1 << 17,
        "gateway_message_content": 1 << 18,
        "gateway_message_content_limited": 1 << 19,
        "application_command_badge": 1 << 23,
    }
