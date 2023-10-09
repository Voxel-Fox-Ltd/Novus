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

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Optional, TypedDict

from typing_extensions import NotRequired

from ._util import HasLocalizations

if TYPE_CHECKING:
    from ._util import Snowflake, Timestamp
    from .components import Button
    from .emoji import PartialEmoji
    from .guild import Integration
    from .locale import Locale

__all__ = (
    'PartialUser',
    'User',
    'GuildMember',
    'GuildMemberRemove',
    'UserConnection',
    'ApplicationRoleConnectionMetadata',
    'ApplicationRoleConnection',
    'Activity',
    'Presence',
)


class PartialUser(TypedDict):
    id: Snowflake
    avatar: Optional[str]
    discriminator: int
    flags: int
    username: str


class _UserOptional(TypedDict, total=False):
    bot: bool
    system: bool
    mfa_enabled: bool
    banner: Optional[str]
    accent_color: Optional[int]
    locale: Locale
    verified: bool
    email: Optional[str]
    flags: int
    premium_type: Literal[0, 1, 2, 3]
    public_flags: int


class User(_UserOptional):
    id: Snowflake
    username: str
    discriminator: int
    avatar: Optional[str]


class _GuildMemberOptional(TypedDict, total=False):
    nick: Optional[str]
    avatar: Optional[str]
    premium_since: Optional[Timestamp]
    pending: bool
    permissions: str
    communication_disabled_until: Optional[Timestamp]


class GuildMemberRemove(TypedDict):
    user: User
    guild_id: Snowflake


class GuildMember(_GuildMemberOptional):
    user: User  # Not actually required! Not sent with message payloads.
    roles: list[Snowflake]
    joined_at: Timestamp
    deaf: bool
    mute: bool
    guild_id: Snowflake


class _UserConnectionOptional(TypedDict, total=False):
    revoked: bool
    integrations: list[Integration]


class UserConnection(_UserConnectionOptional):
    id: str  # Probably a snowflake, but typed as a string in the docs
    name: str
    type: str
    verified: bool
    friend_sync: bool
    show_activity: bool
    two_way_link: bool
    visibility: Literal[0, 1]


class ApplicationRoleConnectionMetadata(HasLocalizations):
    type: Literal[1, 2, 3, 4, 5, 6, 7, 8]
    key: str
    name: str
    description: str


class ApplicationRoleConnection(TypedDict):
    platform_name: Optional[str]
    platform_username: Optional[str]
    metadata: dict


class ActivityTimestamps(TypedDict):
    start: NotRequired[Timestamp]
    end: NotRequired[Timestamp]


class Party(TypedDict):
    id: NotRequired[str]
    size: NotRequired[tuple[int, int]]


class Assets(TypedDict):
    large_image: NotRequired[str]
    large_text: NotRequired[str]
    small_image: NotRequired[str]
    small_text: NotRequired[str]


class Secrets(TypedDict):
    join: NotRequired[str]
    spectate: NotRequired[str]
    match: NotRequired[str]


class _ActivityOptional(TypedDict, total=False):
    url: Optional[str]
    timestamps: ActivityTimestamps
    application_id: Snowflake
    details: Optional[str]
    state: Optional[str]
    emoji: Optional[PartialEmoji]
    party: Party
    assets: Assets
    secrets: Secrets
    instance: bool
    flags: int
    buttons: list[Button]


class Activity(_ActivityOptional):
    name: str
    type: Literal[0, 1, 2, 3, 4, 5]
    created_at: Timestamp


class _PresenceUser(TypedDict):
    id: Snowflake


class Presence(TypedDict):
    user: _PresenceUser
    guild_id: Snowflake
    status: Literal["idle", "dnd", "online", "offline"]
    activities: list[Activity]
