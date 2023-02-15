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

from typing import TYPE_CHECKING

from vfflags import Flags

__all__ = (
    'Intents',
)


class Intents(Flags):
    """
    Gateway intents so as to connect to Discord's gateway.
    """

    if TYPE_CHECKING:

        def __init__(self, value: int = 0, **kwargs: bool) -> None:
            ...

        guilds: bool
        guild_members: bool
        guild_moderation: bool
        guild_emojis_and_stickers: bool
        guild_integrations: bool
        guild_webhooks: bool
        guild_invites: bool
        guild_voice_states: bool
        guild_presences: bool
        guild_messages: bool
        guild_message_reactions: bool
        guild_message_typing: bool
        direct_messages: bool
        direct_message_reactions: bool
        direct_message_typing: bool
        message_content: bool
        guild_scheduled_events: bool
        auto_moderation_configuration: bool
        auto_moderation_execution: bool

        messages: bool
        reactions: bool
        typing: bool
        privileged: bool

    CREATE_FLAGS = {
        "guilds": 1 << 0,
        "guild_members": 1 << 1,
        "guild_moderation": 1 << 2,
        "guild_emojis_and_stickers": 1 << 3,
        "guild_integrations": 1 << 4,
        "guild_webhooks": 1 << 5,
        "guild_invites": 1 << 6,
        "guild_voice_states": 1 << 7,
        "guild_presences": 1 << 8,
        "guild_messages": 1 << 9,
        "guild_message_reactions": 1 << 10,
        "guild_message_typing": 1 << 11,
        "direct_messages": 1 << 12,
        "direct_message_reactions": 1 << 13,
        "direct_message_typing": 1 << 14,
        "message_content": 1 << 15,
        "guild_scheduled_events": 1 << 16,
        "auto_moderation_configuration": 1 << 20,
        "auto_moderation_execution": 1 << 21,

        "messages": 1 << 9 | 1 << 12,
        "reactions": 1 << 10 | 1 << 13,
        "typing": 1 << 11 | 1 << 14,
        "privileged": 1 << 8 | 1 << 15,
    }
