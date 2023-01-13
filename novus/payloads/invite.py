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

from typing import TYPE_CHECKING, Optional, TypedDict, Literal

if TYPE_CHECKING:
    from ._snowflake import Timestamp
    from .user import User
    from .guild import Guild
    from .guild_scheduled_event import GuildScheduledEvent
    from .application import Application
    from .channel import Channel

__all__ = (
    'Invite',
    'InviteWithMetadata',
)


class _InviteOptional(TypedDict, total=False):
    guild: Guild
    inviter: User
    target_type: Literal[1, 2]
    target_user: User
    target_application: Application
    approximate_presence_count: int
    approximate_member_count: int
    expires_at: Optional[Timestamp]
    # stage_instance: InviteStageInstance - documented but deprecated
    guild_scheduled_event: GuildScheduledEvent


class Invite(_InviteOptional):
    code: str
    channel: Optional[Channel]


class InviteWithMetadata(Invite):
    uses: int
    max_uses: int
    max_age: int
    temporary: bool
    created_at: Timestamp
