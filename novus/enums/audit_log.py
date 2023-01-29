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

__all__ = ("AuditLogEventType",)


class AuditLogEventType(Enum):
    guild_update = 1

    channel_create = 10
    channel_update = 11
    channel_delete = 12
    channel_overwrite_create = 13
    channel_overwrite_update = 14
    channel_overwrite_delete = 15

    member_kick = 20
    member_prune = 21
    member_ban_add = 22
    member_ban_remove = 23
    member_update = 24
    member_role_update = 25
    member_move = 26
    member_disconnect = 27
    bot_add = 28

    role_create = 30
    role_update = 31
    role_delete = 32

    invite_create = 40
    invite_update = 41
    invite_delete = 42

    webhook_create = 50
    webhook_update = 51
    webhook_delete = 52

    emoji_create = 60
    emoji_update = 61
    emoji_delete = 62

    message_delete = 72
    message_bulk_delete = 73
    message_pin = 74
    message_unpin = 75

    integration_create = 80
    integration_update = 81
    integration_delete = 82

    stage_instance_create = 83
    stage_instance_update = 84
    stage_instance_delete = 85

    sticker_create = 90
    sticker_update = 91
    sticker_delete = 92

    guild_scheduled_event_create = 100
    guild_scheduled_event_update = 101
    guild_scheduled_event_delete = 102

    thread_create = 110
    thread_update = 111
    thread_delete = 112

    application_command_permission_update = 121

    auto_moderation_rule_create = 140
    auto_moderation_rule_update = 141
    auto_moderation_rule_delete = 142
    auto_moderation_block_message = 143
    auto_moderation_flag_to_channel = 144
    auto_moderation_user_communication_disabled = 145
