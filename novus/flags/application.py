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

from flags import Flags

__all__ = (
    'ApplicationFlags',
)


class ApplicationFlags(Flags):
    """
    The public flags for an application.

    Attributes
    ----------
    application_command_badge : bool
        Indicates if an app has registered global application commands.
    embedded : bool
        Indicates if an app is embedded within the Discord client (currently
        unavailable publicly).
    gateway_guild_members : bool
        Intent required for bots in 100 or more servers to receive
        member-related events like ``guild_member_add``.
    gateway_guild_members_limited : bool
        Intent required for bots in under 100 servers to receive member-related
        events like ``guild_member_add``.
    gateway_message_content : bool
        Intent required for bots in 100 or more servers to receive message
        content.
    gateway_message_content_limited : bool
        Intent required for bots in under 100 servers to receive message
        content.
    gateway_presence : bool
        Intent required for bots in 100 or more servers to receive
        ``presence_update`` events.
    gateway_presence_limited : bool
        Intent required for bots in under 100 servers to receive
        ``presence_update`` events.
    verification_pending_guild_limit : bool
        Indicates unusual growth of an app that prevents verification.
    """

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
