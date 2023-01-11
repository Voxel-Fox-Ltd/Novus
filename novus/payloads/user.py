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

from typing import TYPE_CHECKING, TypedDict, Optional

if TYPE_CHECKING:
    from ._snowflake import Snowflake

__all__ = (
    'PartialUser',
    'User',
)


class PartialUser(TypedDict):
    id: Snowflake
    avatar: Optional[str]
    discriminator: int
    flags: int
    username: str


class User(PartialUser):
    # id: str
    # username: str
    # discriminator: int
    # avatar: Optional[str]
    # bot: bool
    # system: bool
    # mfa_enabled: bool
    # locale: str
    # verified: bool
    # email: str
    # flags: int
    # premium_type: int
    # public_flags: int
    ...
