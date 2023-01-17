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

from typing import TYPE_CHECKING
import functools

from .asset import Asset
from ..utils import try_snowflake
from ..flags import Permissions

if TYPE_CHECKING:
    from ..api import HTTPConnection
    from ..payloads import Role as RolePayload

__all__ = (
    'Role',
)


class Role:
    """
    A model for a guild role.

    Attributes
    ----------
    id : int
        The ID associated with the role.
    name : str
        The name associated with the role.
    color : int
        The colour associated with the role, as a hex code.
    hoist : bool
        Whether the role is pinned in the user listing.
    icon_hash : str | None
        The hash associated with the role icon.
    icon : novus.Asset | None
        The asset associated with the role icon.
    unicode_emoji : str | None
        The role unicode emoji.
    position : int
        The position of the role.

        .. note::

            The position of the role is calculated as a pair of the role's
            position attribute and it's ID attribute. Positions in a guild can
            be shared by multiple roles, or skipped entirely.
    permissions : novus.Permissions
        The permissions for the role.
    managed : bool
        Whether the role is managed by an integration.
    mentionable : bool
        Whether the role is mentionable.
    tags : list[dict]
        The tags associated with the role.
    """

    __slots__ = (
        '_state',
        'id',
        'name',
        'color',
        'hoist',
        'icon_hash',
        'unicode_emoji',
        'position',
        'permissions',
        'managed',
        'mentionable',
        'tags',
    )

    def __init__(self, *, state: HTTPConnection, data: RolePayload):
        self._state = state
        self.id = try_snowflake(data['id'])
        self.name = data['name']
        self.color = data['color']
        self.hoist = data['hoist']
        self.icon_hash = data.get('icon')
        self.unicode_emoji = data.get('unicode_emoji')
        self.position = data['position']
        self.permissions = Permissions(int(data['permissions']))
        self.managed = data['managed']
        self.mentionable = data['mentionable']
        self.tags = data.get('role_tags', list())

    @property
    @functools.cache
    def icon(self) -> Asset | None:
        if self.icon_hash is None:
            return None
        return Asset.from_role(self)
