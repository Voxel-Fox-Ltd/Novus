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

from typing import TYPE_CHECKING, Optional, TypedDict

if TYPE_CHECKING:
    from ._util import Snowflake, Timestamp
    from .user import GuildMember

__all__ = (
    'VoiceState',
    'VoiceRegion',
)


class VoiceRegion(TypedDict):
    id: str
    name: str
    optional: bool
    deprecated: bool
    custom: bool


class _VoiceStateOptional(TypedDict, total=False):
    guild_id: Snowflake
    member: GuildMember
    self_stream: bool


class VoiceState(_VoiceStateOptional):
    channel_id: Optional[Snowflake]
    user_id: Snowflake
    session_id: str
    deaf: bool
    mute: bool
    self_deaf: bool
    self_mute: bool
    self_video: bool
    suppress: bool
    request_to_speak_timestamp: Optional[Timestamp]
