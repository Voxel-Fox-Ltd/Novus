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

from typing import TYPE_CHECKING, Any, NoReturn, TypeAlias

from ....utils import MISSING, try_id

if TYPE_CHECKING:
    import io

    from ....flags import Permissions
    from ... import Role
    from ...abc import Snowflake, StateSnowflake

    FileT: TypeAlias = str | bytes | io.IOBase


class GuildRoleAPI:

    async def fetch_roles(self: StateSnowflake) -> list[Role]:
        """
        Get a list of roles for the guild.

        Returns
        -------
        list[novus.model.Role]
            A list of roles in the guild.
        """

        roles = await self.state.guild.get_guild_roles(self.id)
        for r in roles:
            r.guild = self
        return roles

    async def create_role(
            self: StateSnowflake,
            *,
            reason: str | None = None,
            name: str = MISSING,
            permissions: Permissions = MISSING,
            color: int = MISSING,
            hoist: bool = MISSING,
            icon: FileT = MISSING,
            unicode_emoji: str = MISSING,
            mentionable: bool = MISSING) -> Role:
        """
        Create a role within the guild.

        Parameters
        ----------
        name : str
            The name of the role.
        permissions : novus.Permissions
            The permissions attached to the role.
        color : int
            The color of the role.
        hoist : bool
            Whether the role is displayed seperately in the sidebar.
        icon : str | bytes | io.IOBase | None
            The role icon image. Only usable if the guild has the
            ``ROLE_ICONS`` feature.
        unicode_emoji : str
            The role's unicode emoji. Only usable if the guild has the
            ``ROLE_ICONS`` feature.
        mentionable : bool
            Whether the role should be mentionable.
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
            update['icon'] = icon
        if unicode_emoji is not MISSING:
            update['unicode_emoji'] = unicode_emoji
        if mentionable is not MISSING:
            update['mentionable'] = mentionable

        role = await self.state.guild.create_guild_role(
            self.id,
            reason=reason,
            **update,
        )
        role.guild = self
        return role

    async def move_roles(self) -> NoReturn:
        raise NotImplementedError()

    async def edit_role(
            self: StateSnowflake,
            role_id: int,
            *,
            reason: str | None = None,
            name: str = MISSING,
            permissions: Permissions = MISSING,
            color: int = MISSING,
            hoist: bool = MISSING,
            icon: FileT = MISSING,
            unicode_emoji: str = MISSING,
            mentionable: bool = MISSING) -> Role:
        """
        Edit a role.

        Parameters
        ----------
        role_id : int
            The ID of the role to be edited.
        name : str
            The new name of the role.
        permissions : novus.Permissions
            The permissions to be applied to the role.
        color : int
            The color to apply to the role.
        hoist : bool
            If the role should be displayed seperately in the sidebar.
        icon : str | bytes | io.IOBase | None
            The role's icon image. Only usable if the guild has the
            ``ROLE_ICONS`` feature.
        unicode_emoji : str
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
            update['icon'] = icon
        if unicode_emoji is not MISSING:
            update['unicode_emoji'] = unicode_emoji
        if mentionable is not MISSING:
            update['mentionable'] = mentionable

        role = await self.state.guild.modify_guild_role(
            self.id,
            role_id,
            reason=reason,
            **update,
        )
        role.guild = self
        return role

    async def delete_role(
            self: StateSnowflake,
            role: int | Snowflake,
            *,
            reason: str | None = None) -> None:
        """
        A role to delete.

        Parameters
        ----------
        role : int | novus.abc.Snowflake
            The ID of the role to delete.
        reason : str | None
            The reason to be shown in the audit log.
        """

        await self.state.guild.delete_guild_role(
            self.id,
            try_id(role),
            reason=reason,
        )
        return None
