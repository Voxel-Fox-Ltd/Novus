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

__all__ = (
    'ChannelType',
    'PermissionOverwriteType',
    'ForumSortOrder',
    'ForumLayout',
)


class ChannelType(Enum):
    guild_text = 0
    dm = 1
    guild_voice = 2
    group_dm = 3
    guild_category = 4
    guild_announcement = 5
    announcement_thread = 10
    public_thread = 11
    private_thread = 12
    guild_stage_voice = 13
    guild_directory = 14
    guild_forum = 15


class PermissionOverwriteType(Enum):
    role = 0
    member = 1


class ForumSortOrder(Enum):
    latest_activity = 0
    creation_date = 1


class ForumLayout(Enum):
    not_set = 0
    list_view = 1
    gallery_view = 2
