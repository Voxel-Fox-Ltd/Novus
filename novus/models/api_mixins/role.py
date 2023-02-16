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

from typing import TYPE_CHECKING, Any

from ...utils import MISSING

if TYPE_CHECKING:
    from ...api import HTTPConnection
    from ...flags import Permissions
    from ...models import api_mixins as amix
    from .. import File, Guild, Role
    from ..abc import StateSnowflakeWithGuild

__all__ = (
    'RoleAPIMixin',
)


class RoleAPIMixin:

    id: int
    _state: HTTPConnection
    guild: Guild | amix.GuildAPIMixin

    async def delete(
            self: StateSnowflakeWithGuild,
            *,
            reason: str | None = None) -> None:
        """
        Delete the role from the guild.

        Parameters
        ----------
        reason : str | None
            The reason shown in the audit log.
        """

        await self._state.guild.delete_guild_role(
            self.guild.id,
            self.id,
            reason=reason,
        )
        return None

    async def edit(
            self: StateSnowflakeWithGuild,
            *,
            reason: str | None = None,
            name: str = MISSING,
            permissions: Permissions = MISSING,
            color: int = MISSING,
            hoist: bool = MISSING,
            icon: File | None = MISSING,
            unicode_emoji: str | None = MISSING,
            mentionable: bool = MISSING) -> Role:
        """
        Edit a role.

        Parameters
        ----------
        name : str
            The new name of the role.
        permissions : novus.Permissions
            The permissions to be applied to the role.
        color : int
            The color to apply to the role.
        hoist : bool
            If the role should be displayed seperately in the sidebar.
        icon : discord.File | None
            The role's icon image. Only usable if the guild has the
            ``ROLE_ICONS`` feature. All aside from the data itself is
            discarded.
        unicode_emoji : str | None
            The role's unicode emoji. Only usable if the guild has the
            ``ROLE_ICONS`` feature.
        mentionable : bool
            If the role is mentionable.
        reason : str | None
            The reason to be shown in the audit log.
        """

        update: dict[str, Any] = {}

        if name is not MISSING:
            update['name'] = name
        if permissions is not MISSING:
            update['permissions'] = permissions
        if color is not MISSING:
            update['color'] = color
        if hoist is not MISSING:
            update['hoist'] = hoist
        if icon is not MISSING:
            update['icon'] = None
            if icon is not None:
                update['icon'] = icon.data
        if unicode_emoji is not MISSING:
            update['unicode_emoji'] = unicode_emoji
        if mentionable is not MISSING:
            update['mentionable'] = mentionable

        return await self._state.guild.modify_guild_role(
            self.guild.id,
            self.id,
            reason=reason,
            **update,
        )
