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

from typing import TYPE_CHECKING, TypedDict, Optional, Literal

if TYPE_CHECKING:
    from ._snowflake import Snowflake, Timestamp
    from .locale import Locale

__all__ = (
    'PartialUser',
    'User',
    'GuildMember',
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
    user: User
    nick: Optional[str]
    avatar: Optional[str]
    premium_since: Optional[Timestamp]
    pending: bool
    permissions: str
    communication_disabled_until: Optional[Timestamp]


class GuildMember(_GuildMemberOptional):
    roles: list[Snowflake]
    joined_at: Timestamp
    deaf: bool
    mute: bool
