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

from .audit_log import *
from .auto_moderation import *
from .channel import *
from .emoji import *
from .guild import *
from .invite import *
from .message import *
from .role import *
from .scheduled_event import *
from .stage_instance import *
from .sticker import *
from .user import *
from .webhook import *

__all__: tuple[str, ...] = (
    'AnnouncementChannelAPIMixin',
    'AuditLogAPIMixin',
    'AutoModerationAPIMixin',
    'ChannelAPIMixin',
    'EmojiAPIMixin',
    'ForumChannelAPIMixin',
    'GuildAPIMixin',
    'GuildMemberAPIMixin',
    'InviteAPIMixin',
    'MessageAPIMixin',
    'RoleAPIMixin',
    'ScheduledEventAPIMixin',
    'StageInstanceAPIMixin',
    'StickerAPIMixin',
    'TextChannelAPIMixin',
    'UserAPIMixin',
    'WebhookAPIMixin',
)
