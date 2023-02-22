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

from collections.abc import Callable, Coroutine
from typing import TYPE_CHECKING, Any, Type, TypeVarTuple, Union

import novus as n

if TYPE_CHECKING:

    Ts = TypeVarTuple('Ts')
    CommandCallback = Union[
        Callable[
            [Any, n.Interaction[n.ApplicationCommandData], *Ts],
            Coroutine[Any, Any, None],
        ],
        Callable[
            [Any, n.Interaction[n.ApplicationCommandData]],
            Coroutine[Any, Any, None],
        ],
    ]


__all__ = (
    'Command',
    'command',
)


class Command:
    """
    A command object for Novus command handling.
    """

    name: str
    callback: CommandCallback
    application_command: n.PartialApplicationCommand
    guild_ids: list[int]
    command_ids: set[int]

    def __init__(
            self,
            name: str,
            application_command: n.PartialApplicationCommand,
            callback: CommandCallback,
            guild_ids: list[int]):
        self.name = name
        self.callback = callback
        self.application_command = application_command
        self.guild_ids = guild_ids
        self.command_ids = set()
        self.owner: Any = None

    __repr__ = n.utils.generate_repr(('name', 'application_command', 'guild_ids', 'command_ids',))

    def add_id(self, id: int) -> None:
        self.command_ids.add(id)

    async def run(self, interaction: n.Interaction[n.ApplicationCommandData]) -> None:
        await self.callback(self.owner, interaction)

    async def run_autocomplete(self, interaction: n.Interaction[n.ApplicationCommandData]) -> None:
        pass


def command(
        name: str | None = None,
        description: str | None = None,
        *,
        options: list[n.ApplicationCommandOption] | None = None,
        default_member_permissions: n.Permissions = n.Permissions(0),
        dm_permission: bool = True,
        nsfw: bool = False,
        guild_ids: list[int] | None = None,
        cls: Type[Command] = Command,
        **kwargs: Any):
    def wrapper(func: CommandCallback) -> Command:
        cname = name or func.__name__
        dname = description or func.__doc__
        if dname is None:
            raise ValueError("Missing description for command %s" % cname)
        return cls(
            name=cname,
            application_command=n.PartialApplicationCommand(
                name=cname,
                description=dname.strip(),
                type=n.ApplicationCommandType.chat_input,
                options=options or [],
                default_member_permissions=default_member_permissions,
                dm_permission=dm_permission,
                nsfw=nsfw,
                **kwargs
            ),
            guild_ids=guild_ids or [],
            callback=func,
        )
    return wrapper
