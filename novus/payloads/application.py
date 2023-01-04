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

from typing import TYPE_CHECKING, TypedDict, Optional

if TYPE_CHECKING:
    from .user import PartialUser

__all__ = (
    'ApplicationTeamMember',
    'ApplicationTeam',
    'InstallParams',
    'Application',
)


class ApplicationTeamMember(TypedDict):
    membership_state: int
    permissions: list[str]
    team_id: str
    user: PartialUser


class ApplicationTeam(TypedDict):
    icon: Optional[str]
    id: str
    members: list[ApplicationTeamMember]


class InstallParams(TypedDict):
    permissions: str
    scopes: list[str]


class Application(TypedDict):
    id: str
    name: str
    icon: str
    description: str
    rpc_origins: list[str]
    bot_public: bool
    bot_require_code_grant: bool
    terms_of_service_url: Optional[str]
    privacy_policy_url: Optional[str]
    owner: PartialUser
    verify_key: str
    team: ApplicationTeam
    guild_id: Optional[str]
    primary_sku_id: Optional[str]
    slug: Optional[str]
    cover_image: Optional[str]
    flags: Optional[int]
    install_params: Optional[InstallParams]
    custom_install_url: Optional[str]
    role_connections_verification_url: Optional[str]
