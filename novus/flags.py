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
    'Permissions',
    'ApplicationFlags',
)


class Permissions(Flags):
    """
    A permission set from Discord's API.
    """

    CREATE_FLAGS = {
        "create_instant_invite": 1 << 0,
        "kick_members": 1 << 1,
        "ban_members": 1 << 2,
        "administrator": 1 << 3,
        "manage_channels": 1 << 4,
        "manage_guild": 1 << 5,
        "add_reactions": 1 << 6,
        "view_audit_log": 1 << 7,
        "priority_speaker": 1 << 8,
        "stream": 1 << 9,
        "view_channel": 1 << 10,
        "send_messages": 1 << 11,
        "send_tts_messages": 1 << 12,
        "manage_messages": 1 << 13,
        "embed_links": 1 << 14,
        "attach_files": 1 << 15,
        "read_message_history": 1 << 16,
        "mention_everyone": 1 << 17,
        "use_external_emojis": 1 << 18,
        "view_guild_insights": 1 << 19,
        "connect": 1 << 20,
        "speak": 1 << 21,
        "mute_members": 1 << 22,
        "deafen_members": 1 << 23,
        "move_members": 1 << 24,
        "use_vad": 1 << 25,
        "change_nickname": 1 << 26,
        "manage_nicknames": 1 << 27,
        "manage_roles": 1 << 28,
        "manage_webhooks": 1 << 29,
        "manage_emojis_and_stickers": 1 << 30,
        "use_application_commands": 1 << 31,
        "request_to_speak": 1 << 32,
        "manage_events": 1 << 33,
        "manage_threads": 1 << 34,
        "create_public_threads": 1 << 35,
        "create_private_threads": 1 << 36,
        "use_external_stickers": 1 << 37,
        "send_messages_in_threads": 1 << 38,
        "use_embedded_activites": 1 << 39,
        "moderate_members": 1 << 40,
    }


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
