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

from typing import TYPE_CHECKING

from vfflags import Flags

__all__ = (
    'Permissions',
)


class Permissions(Flags):

    if TYPE_CHECKING:
        create_instant_invite: bool
        kick_members: bool
        ban_members: bool
        administrator: bool
        manage_channels: bool
        manage_guild: bool
        add_reactions: bool
        view_audit_log: bool
        priority_speaker: bool
        stream: bool
        view_channel: bool
        send_messages: bool
        send_tts_messages: bool
        manage_messages: bool
        embed_links: bool
        attach_files: bool
        read_message_history: bool
        mention_everyone: bool
        use_external_emojis: bool
        view_guild_insights: bool
        connect: bool
        speak: bool
        mute_members: bool
        deafen_members: bool
        move_members: bool
        use_vad: bool
        change_nickname: bool
        manage_nicknames: bool
        manage_roles: bool
        manage_webhooks: bool
        manage_emojis_and_stickers: bool
        use_application_commands: bool
        request_to_speak: bool
        manage_events: bool
        manage_threads: bool
        create_public_threads: bool
        create_private_threads: bool
        use_external_stickers: bool
        send_messages_in_threads: bool
        use_embedded_activites: bool
        moderate_members: bool
        view_creator_monetization_analytics: bool
        use_soundboard: bool
        create_guild_expressions: bool
        create_events: bool
        use_external_sounds: bool
        send_voice_messages: bool
        send_polls: bool

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
        "view_creator_monetization_analytics": 1 << 41,
        "use_soundboard": 1 << 42,
        "create_guild_expressions": 1 << 43,
        "create_events": 1 << 44,
        "use_external_sounds": 1 << 45,
        "send_voice_messages": 1 << 46,
        "send_polls": 1 << 49
    }
