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

from .audit_log import GuildAuditAPI
from .auto_moderation import GuildAutomodAPI
from .channel import GuildChannelAPI
from .emoji import GuildEmojiAPI
from .guild import GuildAPI
from .role import GuildRoleAPI
from .scheduled_event import GuildEventAPI
from .sticker import GuildStickerAPI
from .user import GuildUserAPI

if TYPE_CHECKING:
    from ....api import HTTPConnection

__all__ = (
    'GuildAPIMixin',
)


class GuildAPIMixin(
        GuildAuditAPI,
        GuildAutomodAPI,
        GuildChannelAPI,
        GuildEmojiAPI,
        GuildAPI,
        GuildRoleAPI,
        GuildEventAPI,
        GuildStickerAPI,
        GuildUserAPI):
    id: int
    _state: HTTPConnection
