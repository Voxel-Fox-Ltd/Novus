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
    icon: Optional[str]
    id: Snowflake
    members: list[ApplicationTeamMember]
    name: str
    owner_user_id: Snowflake


class InstallParams(TypedDict):
    permissions: str
    scopes: list[str]


class Application(TypedDict):
    id: Snowflake
    name: str
    icon: Optional[str]
    description: str
    rpc_origins: NotRequired[list[str]]
    bot_public: bool
    bot_require_code_grant: bool
    verify_key: str
    team: Optional[ApplicationTeam]
    terms_of_service_url: NotRequired[str]
    privacy_policy_url: NotRequired[str]
    owner: NotRequired[PartialUser]
    guild_id: NotRequired[Snowflake]
    primary_sku_id: NotRequired[str]
    slug: NotRequired[str]
    cover_image: NotRequired[str]
    tags: NotRequired[list[str]]
    flags: NotRequired[int]
    install_params: NotRequired[InstallParams]
    custom_install_url: NotRequired[str]
    role_connections_verification_url: NotRequired[str]


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
