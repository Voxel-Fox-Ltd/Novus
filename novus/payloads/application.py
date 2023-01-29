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

from typing import TYPE_CHECKING, Literal, Optional, TypedDict

if TYPE_CHECKING:
    from ._util import Snowflake
    from .locale import Locale
    from .user import PartialUser

__all__ = (
    'ApplicationTeamMember',
    'ApplicationTeam',
    'InstallParams',
    'Application',
)


class ApplicationTeamMember(TypedDict):
    team_id: Snowflake
    membership_state: int
    permissions: list[str]
    user: PartialUser


class ApplicationTeam(TypedDict):
    id: Snowflake
    icon: Optional[str]
    members: list[ApplicationTeamMember]


class InstallParams(TypedDict):
    permissions: str
    scopes: list[str]


class _ApplicationOptional(TypedDict, total=False):
    terms_of_service_url: str
    privacy_policy_url: str
    owner: PartialUser
    guild_id: Snowflake
    primary_sku_id: str
    slug: str
    cover_image: str
    flags: int  # Added as novus.flags.ApplicationFlags
    install_params: InstallParams
    custom_install_url: str
    role_connections_verification_url: str


class Application(_ApplicationOptional):
    id: Snowflake
    name: str
    icon: Optional[str]
    description: str
    rpc_origins: list[str]
    bot_public: bool
    bot_require_code_grant: bool
    verify_key: str
    team: Optional[ApplicationTeam]


ApplicationRoleConnectionMetadataType = Literal[
    1,  # INTEGER_LESS_THAN_OR_EQUAL
    2,  # INTEGER_GREATER_THAN_OR_EQUAL
    3,  # INTEGER_EQUAL
    4,  # INTEGER_NOT_EQUAL
    5,  # DATETIME_LESS_THAN_OR_EQUAL
    6,  # DATETIME_GREATER_THAN_OR_EQUAL
    7,  # BOOLEAN_EQUAL
    8,  # BOOLEAN_NOT_EQUAL
]


class _ApplicationRoleCommandMetadataOptional(TypedDict, total=False):
    name_localizations: dict[Locale, str]
    description_localizations: dict[Locale, str]


class ApplicationRoleCommandMetadata(_ApplicationRoleCommandMetadataOptional):
    type: ApplicationRoleConnectionMetadataType
    key: str
    name: str
    description: str
