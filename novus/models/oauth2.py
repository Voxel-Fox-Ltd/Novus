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

from typing import TYPE_CHECKING

from ..flags import ApplicationFlags, Permissions
from ..utils import cached_slot_property, try_snowflake
from .asset import Asset
from .user import User

if TYPE_CHECKING:
    from .. import payloads
    from ..api import HTTPConnection

__all__ = (
    'TeamMember',
    'Team',
    'Application',
)


class TeamMember:
    """
    A user within a team.

    Attributes
    ----------
    accepted : bool
        If the user has accepted the team invite.
    permissions : list[str]
        The permissions that the team member has within the team.
    team_id : int
        The ID of the team that the user is part of.
    user : novus.User
        The team member. A partial object.
    """

    __slots__ = (
        'state',
        'accepted',
        'permissions',
        'team_id',
        'user',
    )

    accepted: bool
    permissions: list[str]
    team_id: int
    user: User

    def __init__(self, *, state: HTTPConnection, data: payloads.ApplicationTeamMember):
        self.state = state
        self.accepted = data["membership_state"] == 2
        self.permissions = data["permissions"]
        self.team_id = try_snowflake(data["team_id"])
        user = self.state.cache.get_user(data["user"]["id"])
        if user is None:
            user = User(state=self.state, data=data["user"])
        self.user = user


class Team:
    """
    A team associated with an application.

    Attributes
    ----------
    id : int
        The ID of the team.
    icon_hash : str | None
        The icon hash for the team icon.
    icon : novus.Asset | None
        An asset for the team icon.
    members : list[novus.TeamMember]
        A list of team members.
    name : str
        The name of the team.
    owner_user_id : int
        The ID of the owner of the team.
    """

    __slots__ = (
        'state',
        'icon_hash',
        'id',
        'members',
        'name',
        'owner_user_id',
        '_cs_icon'
    )

    if TYPE_CHECKING:
        icon_hash: str | None
        id: int
        members: list[TeamMember]
        name: str
        owner_user_id: int

    def __init__(self, *, state: HTTPConnection, data: payloads.ApplicationTeam):
        self.state = state
        self.id = try_snowflake(data["id"])
        self.icon_hash = data["icon"]
        self.members = [
            TeamMember(state=self.state, data=d)
            for d in data["members"]
        ]
        self.name = data["name"]
        self.owner_user_id = try_snowflake(data["owner_user_id"])

    @cached_slot_property("_cs_icon")
    def icon(self) -> Asset | None:
        return Asset.from_team(self)


class Application:
    """
    A model containing data about an application.

    Attributes
    ----------
    id : int
        The ID of the application.
    name : str
        The name of the team.
    icon_hash : str | None
        A hash for the application icon.
    icon : novus.Asset | None
        An asset for the application icon.
    description : str
        A description for the application.
    rpc_origins : list[str]
        An array of RPC origin URLs.
    bot_public : bool
        Whether the bot associated with the application is set to public.
    bot_require_code_grant : bool
        Whether or not the bot requires a code grant.
    terms_of_service_url : str | None
        The ToS URL for the application.
    privacy_policy_url : str | None
        The privacy policy URL for the application.
    owner : novus.User
        The user who owns the application.
    verify_key : str
        The hex encoded key for verification in interactions.
    team : novus.Team | None
        The team associated with the application.
    guild_id : int | None
        The guild ID associated with the game sold via the application.
    primary_sku_id : int | None
        The ID of the game SKU for the application.
    slug : str | None
        The URL slug that links to the store page.
    cover_image_hash : str | None
        The hash for the cover image.
    cover_image : novus.Asset | None
        The cover image asset for the application.
    flags : novus.ApplicationFlags
        The flags assocaiated with the application.
    tags : list[str]
        A list of tags describing the content and functionality of the
        application.
    install_scopes : list[str]
        The scopes used in the in-app authorization link.
    install_permissions : novus.Permissions
        The permissions used in the in-app authorization link.
    custom_install_url : str | None
        The application's custom authorization link.
    role_connections_verification_url : str | None
        The role connection verification entry point URL.
    """

    __slots__ = (
        'state',
        'id',
        'name',
        'icon_hash',
        'description',
        'rpc_origins',
        'bot_public',
        'bot_require_code_grant',
        'terms_of_service_url',
        'privacy_policy_url',
        'owner',
        'verify_key',
        'team',
        'guild_id',
        'primary_sku_id',
        'slug',
        'cover_image_hash',
        'flags',
        'tags',
        'install_scopes',
        'install_permissions',
        'custom_install_url',
        'role_connections_verification_url',
        '_cs_icon',
        '_cs_cover_image',
    )

    if TYPE_CHECKING:
        id: int
        name: str
        icon_hash: str | None
        description: str
        rpc_origins: list[str]
        bot_public: bool
        bot_require_code_grant: bool
        terms_of_service_url: str | None
        privacy_policy_url: str | None
        owner: User
        verify_key: str
        team: Team | None
        guild_id: int | None
        primary_sku_id: int | None
        slug: str | None
        cover_image_hash: str | None
        flags: ApplicationFlags
        tags: list[str]
        install_scopes: list[str]
        install_permissions: Permissions
        custom_install_url: str | None
        role_connections_verification_url: str | None

    def __init__(self, *, state: HTTPConnection, data: payloads.Application):
        self.state = state
        self.id = try_snowflake(data["id"])
        self.name = data["name"]
        self.icon_hash = data["icon"]
        self.description = data["description"]
        self.rpc_origins = data.get("rpc_origins", [])
        self.bot_public = data["bot_public"]
        self.bot_require_code_grant = data["bot_require_code_grant"]
        self.terms_of_service_url = data.get("terms_of_service_url")
        self.privacy_policy_url = data.get("privacy_policy_url")
        if "owner" in data:
            owner = self.state.cache.get_user(data["owner"]["id"])
            if owner is None:
                owner = User(state=self.state, data=data["owner"])
            self.owner = owner
        self.verify_key = data["verify_key"]
        self.team = None
        if "team" in data and data["team"]:
            self.team = Team(state=self.state, data=data["team"])
        self.guild_id = try_snowflake(data.get("guild_id"))
        self.primary_sku_id = try_snowflake(data.get("primary_sku_id"))
        self.slug = data.get("slug")
        self.cover_image_hash = data.get("cover_image")
        self.flags = ApplicationFlags(data.get("flags", 0))
        self.tags = data.get("tags", [])
        self.install_scopes = data.get("install_params", {}).get("scopes", [])
        permissions = Permissions(int(data.get("install_params", {}).get("permissions", 0)))
        self.install_permissions = permissions
        self.custom_install_url = data.get("custom_install_url")
        self.role_connections_verification_url = data.get("role_connections_verification_url")

    @cached_slot_property("_cs_icon")
    def icon(self) -> Asset | None:
        return Asset.from_application(self)

    @cached_slot_property("_cs_cover_image")
    def cover_image(self) -> Asset | None:
        return Asset.from_application_cover_image(self)
