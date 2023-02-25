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

import collections
from collections.abc import Callable, Coroutine, Iterable
from typing import TYPE_CHECKING, Any, Type, TypeVarTuple, Union

from typing_extensions import Self

import novus as n

from .errors import CommandError

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

    LocType = dict[str, str] | dict[n.Locale, str] | n.utils.Localization | None


__all__ = (
    'Command',
    'CommandGroup',
    'CommandDescription',
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
            type: n.ApplicationCommandType,
            application_command: n.PartialApplicationCommand,
            callback: CommandCallback,
            guild_ids: list[int]):
        self.name = name
        self.type = type
        self.callback = callback
        self.application_command = application_command
        self.guild_ids = guild_ids
        self.command_ids = set()
        self.owner: Any = None

    def to_application_command_option(self) -> n.ApplicationCommandOption:
        """
        Convert this instance of the command into a command option. This should
        only be used on subcommands.
        """

        return n.ApplicationCommandOption(
            name=self.name.split(" ")[-1],
            description=self.application_command.description,
            type=n.ApplicationOptionType.sub_command,
            name_localizations=self.application_command.name_localizations,
            description_localizations=self.application_command.description_localizations,
            options=self.application_command.options,
        )

    __repr__ = n.utils.generate_repr(('name', 'application_command', 'guild_ids', 'command_ids',))

    def add_id(self, id: int) -> None:
        self.command_ids.add(id)

    async def run(self, interaction: n.Interaction[n.ApplicationCommandData]) -> None:
        await self.callback(self.owner, interaction)

    async def run_autocomplete(self, interaction: n.Interaction[n.ApplicationCommandData]) -> None:
        pass


class CommandGroup:
    """
    A group of commands all piled into one place.
    """

    def __init__(
            self,
            application_command: n.PartialApplicationCommand,
            commands: Iterable[Command],
            guild_ids: list[int]):
        self.name = application_command.name
        self.application_command = application_command
        self.guild_ids = guild_ids
        self.command_ids = set()
        self.commands: dict[str, Command] = {
            i.name: i
            for i in commands
        }

    __repr__ = n.utils.generate_repr(('name', 'application_command', 'guild_ids', 'command_ids',))

    def add_id(self, id: int) -> None:
        self.command_ids.add(id)

    def add_description(self, d: CommandDescription) -> None:
        app = self.application_command
        if d.description is not n.utils.MISSING:
            app.description = d.description
        if d.name_localizations is not n.utils.MISSING:
            app.name_localizations = d.name_localizations
        if d.description_localizations is not n.utils.MISSING:
            app.description_localizations = d.description_localizations
        if d.default_member_permissions is not n.utils.MISSING:
            app.default_member_permissions = d.default_member_permissions
        if d.dm_permission is not n.utils.MISSING:
            app.dm_permission = d.dm_permission
        if d.nsfw is not n.utils.MISSING:
            app.nsfw = d.nsfw
        if d.guild_ids is not n.utils.MISSING:
            self.guild_ids = d.guild_ids

    @classmethod
    def from_commands(
            cls,
            commands: Iterable[Command],
            run_checks: bool = True) -> Self:
        """
        Generate a group from a list of commands.

        Parameters
        ----------
        commands : Iterable[novus.ext.client.Command]
            The commands that will make up the group.
        run_checks : bool
            Whether to check that all implemented commands have the same basic
            attributes (dm_permission, NSFW, etc).

        Raises
        ------
        novus.ext.client.CommandError
            An error was encountered trying to group the commands together.
        """

        command_map: dict[tuple[str, ...], Command] = {
            tuple(i.name.split(" ")): i
            for i in commands
        }

        # Split up the subcommands into something that could loosley be called
        # different depths of command name
        # eg: "handle message", "handle user", and "handle channel" would be
        # split into `{0: {"handle"}, 1: {"message", "user", "channel"}}`
        names: dict[int, set[str]] = collections.defaultdict(set)  # depth: name
        for comm in commands:
            name_split = comm.name.split(" ")
            for depth, name_segment in enumerate(name_split):
                names[depth].add(name_segment)

        # Make sure we only have one base name
        if len(names[0]) > 1:
            raise CommandError("Cannot have multiple base names for group")

        # Do some other validity checks
        permission_set = None
        dm_permission_set = None
        nsfw_set = None
        guild_ids_set = None
        if run_checks:
            permission_set = set(
                i.application_command.default_member_permissions.value
                for i in command_map.values()
            )
            if len(permission_set) > 1:
                raise CommandError("Cannot have multiple permission sets for group")
            nsfw_set = set(
                i.application_command.nsfw
                for i in command_map.values()
            )
            if len(nsfw_set) > 1:
                raise CommandError("Cannot have multiple different NSFW flags for group")
            dm_permission_set = set(
                i.application_command.dm_permission
                for i in command_map.values()
            )
            if len(dm_permission_set) > 1:
                raise CommandError("Cannot have different DM permission flags for group")
            guild_ids_set = set(
                tuple(i.guild_ids)
                for i in command_map.values()
            )
            if len(guild_ids_set) > 1:
                raise CommandError("Cannot have different guild IDs for group")
        else:
            for i in commands:
                permission_set = [i.application_command.default_member_permissions.value]
                dm_permission_set = [i.application_command.dm_permission]
                nsfw_set = [i.application_command.nsfw]
                guild_ids_set = [i.guild_ids]
                break
        assert permission_set is not None
        assert dm_permission_set is not None
        assert nsfw_set is not None
        assert guild_ids_set is not None

        # Make up a place for our options to go after we've built them
        built_options: dict[tuple[str, ...], n.ApplicationCommandOption] = {}
        app = n.PartialApplicationCommand(
            name=list(names[0])[0],
            description="...",
            type=n.ApplicationCommandType.chat_input,
            default_member_permissions=n.Permissions(list(permission_set)[0]),
            dm_permission=list(dm_permission_set)[0],
            nsfw=list(nsfw_set)[0],
        )
        built_options[()] = app  # pyright: ignore

        # Build up the subcommand groups
        for (_, *group, _), command in command_map.items():
            group_tuple = ()
            for group_index, group_name in enumerate(group, start=1):
                group_tuple = tuple(group[:group_index])
                if group_tuple not in built_options:
                    built_options[group_tuple] = new = n.ApplicationCommandOption(
                        name=group_name,
                        description="...",
                        type=n.ApplicationOptionType.sub_command_group,
                    )
                    parent_group = tuple(group[:group_index - 1])
                    built_options[parent_group].add_option(new)
            built_options[group_tuple].add_option(command.to_application_command_option())

        print(app)

        return cls(
            app,
            commands,
            list(list(guild_ids_set)[0])
        )


class CommandDescription:
    """
    A description class to wrap around command groups.
    """

    def __init__(
            self,
            description: str = n.utils.MISSING,
            *,
            name_localizations: LocType = n.utils.MISSING,
            description_localizations: LocType = n.utils.MISSING,
            default_member_permissions: n.Permissions = n.utils.MISSING,
            dm_permission: bool = n.utils.MISSING,
            nsfw: bool = n.utils.MISSING,
            guild_ids: list[int] | None = n.utils.MISSING):
        self.description = description
        self.name_localizations = n.utils.flatten_localization(name_localizations)
        self.description_localizations = n.utils.flatten_localization(description_localizations)
        self.default_member_permissions = default_member_permissions
        self.dm_permission = dm_permission
        self.nsfw = nsfw
        self.guild_ids = guild_ids


def command(
        name: str | None = None,
        description: str | None = None,
        type: n.ApplicationCommandType = n.ApplicationCommandType.chat_input,
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
            type=type,
            application_command=n.PartialApplicationCommand(
                name=cname,
                description=dname.strip(),
                type=type,
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
