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
import functools
import inspect
import logging
from collections.abc import Callable, Coroutine, Iterable
from typing import TYPE_CHECKING, Any, Type, Union, cast

from typing_extensions import Self, TypeVarTuple

import novus as n

from .errors import CommandError

if TYPE_CHECKING:
    Ts = TypeVarTuple('Ts')
    CommandInteraction = Union[
        n.Interaction[n.ApplicationCommandData],
        n.Interaction[n.ContextComandData],
    ]
    CommandCallback = Union[
        Callable[
            [Any, CommandInteraction, *Ts],
            Coroutine[Any, Any, None],
        ],
        Callable[
            [Any, CommandInteraction],
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


log = logging.getLogger("novus.ext.bot.command")


class Command:
    """
    A command object for Novus command handling.

    Parameters
    ----------
    name: str
        The name of the command
    type : novus.ApplicationCommandType
        The type of the command.
    callback
        The function that acts as the command.
    application_command: novus.PartialApplicationCommand
        The application command used to generate the command.
    guild_ids: list[int]
        A list of guild IDs that the command is present in.

    Attributes
    ----------
    name: str
        The name of the command
    type : novus.ApplicationCommandType
        The type of the command.
    callback
        The function that acts as the command.
    application_command: novus.PartialApplicationCommand
        The application command used to generate the command.
    guild_ids: list[int]
        A list of guild IDs that the command is present in.
    command_ids: set[int]
        A list of IDs that refer to the command.
    is_subcommand: bool
        Whether or not the command is implemented as a subcommand.
    """

    name: str
    type: n.ApplicationCommandType
    callback: CommandCallback
    application_command: n.PartialApplicationCommand
    guild_ids: list[int]
    command_ids: set[int]
    is_subcommand: bool

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
        self.is_subcommand = (
            self.type == n.ApplicationCommandType.chat_input
            and " " in self.name
        )
        self.owner: Any = None

        # Make sure our callback and app command have similar options
        if self.type == n.ApplicationCommandType.chat_input:
            sig = inspect.signature(self.callback)
            skip = 2
            option_iter = iter(self.application_command.options)
            for pname, _ in sig.parameters.items():
                if skip > 0:
                    skip -= 1
                    continue
                try:
                    option = next(option_iter)
                except StopIteration:
                    raise Exception(f"Missing option {pname} in command {self.name}")
                if option.name != pname:
                    raise Exception(f"Missing option {pname} in command {self.name}")
            try:
                next(option_iter)
                raise Exception(f"Too many options in command {self.name}")
            except StopIteration:
                pass

    def to_application_command_option(self) -> n.ApplicationCommandOption:
        """
        Convert this instance of the command into a command option. This should
        only be used on subcommands.

        Returns
        -------
        novus.ApplicationCommandOption
            Although the command was generated as an application command, this
            will convert that application command into an option.
        """

        return n.ApplicationCommandOption(
            name=self.name.split(" ")[-1],
            description=self.application_command.description,
            type=n.ApplicationOptionType.sub_command,
            name_localizations=self.application_command.name_localizations,
            description_localizations=self.application_command.description_localizations,
            options=self.application_command.options,
        )

    __repr__ = n.utils.generate_repr(('name',))

    def add_id(self, id: int) -> None:
        """
        Add an ID to the command. This means that any interaction invokations
        with the given command ID will be routed to this command instance.

        Parameters
        ----------
        id : int
            The ID that you want to add.
        """

        self.command_ids.add(id)

    async def run(
            self,
            interaction: n.Interaction[n.ApplicationCommandData] | n.Interaction[n.ContextComandData],
            options: list[n.InteractionOption] | None = None) -> None:
        """
        Run the command with the given interaction.

        Parameters
        ----------
        interaction : novus.Interaction
            The interaction that invoked the command.
        options : list[novus.InteractionOption] | None
            The list of options that the command is to be called with. If not
            provided, then the options are taken from the interaction itself.
            This is primarily used as a helper for subcommands.
        """

        kwargs = {}
        if options is None:
            try:
                options = interaction.data.options  # pyright: ignore
            except AttributeError:
                options = []
        assert options is not None
        for option in options:
            data: Any = option.value
            if option.type == n.ApplicationOptionType.channel:
                data_id = int(data)
                data = interaction.data.resolved.channels.get(data_id)
            elif option.type == n.ApplicationOptionType.attachment:
                data_id = int(data)
                data = interaction.data.resolved.attachments.get(data_id)
            elif option.type == n.ApplicationOptionType.user:
                data_id = int(data)
                data = interaction.data.resolved.members.get(data_id)
                if data is None:
                    data = interaction.data.resolved.users.get(data_id)
            elif option.type == n.ApplicationOptionType.role:
                data_id = int(data)
                data = interaction.data.resolved.roles.get(data_id)
            elif option.type == n.ApplicationOptionType.menionable:
                data_id = int(data)
                data = interaction.data.resolved.roles.get(data_id)
                if data is None:
                    data = interaction.data.resolved.members.get(data_id)
                if data is None:
                    data = interaction.data.resolved.users.get(data_id)
            kwargs[option.name] = data

        log.info("Command invoked, %s %s", self, interaction)
        partial = functools.partial(self.callback, self.owner, interaction)
        match self.application_command.type:
            case n.ApplicationCommandType.user | n.ApplicationCommandType.message:
                await partial(interaction.data.target)  # pyright: ignore
            case _:
                await partial(**kwargs)

    def __call__(self) -> CommandCallback:
        return functools.partial(self.callback, self.owner)

    async def run_autocomplete(self, interaction: n.Interaction[n.ApplicationCommandData]) -> None:
        pass


class CommandGroup:
    """
    A group of commands and subcommands.

    Attributes
    ----------
    name : str
        The name of the command.
    application_command : novus.PartialApplicationCommand
        The application command that builds the command.
    guild_ids : list[int]
        The IDs of the guilds that the command is set to.
    command_ids : list[int]
        A list of command IDs that are associated with this command.
    commands : dict[str, novus.ext.client.Command]
        A dict of names and command objects that make up the child commands of
        this command group.
    """

    is_subcommand: bool = False

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

    __repr__ = n.utils.generate_repr(('name',))

    def add_id(self, id: int) -> None:
        """
        Add an ID to the command. This means that any interaction invokations
        with the given command ID will be routed to this command instance.

        Parameters
        ----------
        id : int
            The ID that you want to add.
        """

        self.command_ids.add(id)

    def add_description(self, d: CommandDescription) -> None:
        """
        Add a description to the command group.

        Parameters
        ----------
        d : novus.ext.client.CommandDescription
            The description that you want to add to the command group.
        """
        self._add_description(self, d)
        if d.guild_ids is not n.utils.MISSING:
            self.guild_ids = d.guild_ids

    @classmethod
    def _add_description(
            cls,
            c: Command | CommandGroup | n.ApplicationCommand | n.ApplicationCommandOption,
            d: CommandDescription) -> None:
        """
        Add a description to a command.

        Parameters
        ----------
        c
            The command that the description should be added to.
        d
            The description of the command.
        """

        if isinstance(c, (n.ApplicationCommand, n.ApplicationCommandOption)):
            app = c
        else:
            app = c.application_command
        if d.description is not n.utils.MISSING:
            app.description = d.description
        if d.name_localizations is not n.utils.MISSING:
            app.name_localizations = d.name_localizations
        if d.description_localizations is not n.utils.MISSING:
            app.description_localizations = d.description_localizations
        if isinstance(c, (Command, CommandGroup)):
            app = cast(n.ApplicationCommand, app)
            if d.default_member_permissions is not n.utils.MISSING:
                app.default_member_permissions = d.default_member_permissions
            if d.dm_permission is not n.utils.MISSING:
                app.dm_permission = d.dm_permission
            if d.nsfw is not n.utils.MISSING:
                app.nsfw = d.nsfw
        for option in app.options:
            if option.name in d.children:
                cls._add_description(option, d.children[option.name])

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

        return cls(
            app,
            commands,
            list(list(guild_ids_set)[0])
        )

    async def run(
            self,
            interaction: n.Interaction[n.ApplicationCommandData]) -> None:
        """
        Run the command with the given interaction.

        Parameters
        ----------
        interaction : novus.Interaction
            The interaction that invoked the command.
        """

        command_name_parts = [self.name]
        option = interaction.data.options[0]
        while option.type == n.ApplicationOptionType.sub_command_group:
            command_name_parts.append(option.name)
            option = option.options[0]
        command = self.commands[" ".join([*command_name_parts, option.name])]
        await command.run(interaction, option.options)

    async def run_autocomplete(self, interaction: n.Interaction[n.ApplicationCommandData]) -> None:
        pass


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
            guild_ids: list[int] | None = n.utils.MISSING,
            children: dict[str, CommandDescription] | None = None):
        self.description = description
        self.name_localizations = n.utils.flatten_localization(name_localizations)
        self.description_localizations = n.utils.flatten_localization(description_localizations)
        self.default_member_permissions = default_member_permissions
        self.dm_permission = dm_permission
        self.nsfw = nsfw
        self.guild_ids = guild_ids
        self.children: dict[str, CommandDescription] = children or {}

    __repr__ = n.utils.generate_repr(('description',))


def command(
        name: str | None = None,
        description: str | None = None,
        type: n.ApplicationCommandType = n.ApplicationCommandType.chat_input,
        *,
        options: list[n.ApplicationCommandOption] | None = None,
        default_member_permissions: n.Permissions | None = None,
        dm_permission: bool = True,
        nsfw: bool = False,
        guild_ids: list[int] | None = None,
        cls: Type[Command] = Command,
        **kwargs: Any):
    """
    Wrap a function in a command.

    Parameters
    ----------
    name : str | None
        The name of the command.
        If not provided, the name of the function is used.
        If a name with spaces is given, then it is automatically implemented
        with subcommands (unless it is not a ``chat_input`` type).
    description : str | None
        The description associated with the command. If not provided, the
        docstring for the function is used.
        If the command is built as a subcommand, you can give descriptions and
        localizations using the :class:`novus.ext.client.CommandDescription`
        class.
    type : novus.ApplicationCommandType
        The type of the command that you want to create.
    options : list[novus.ApplicationCommandOption]
        A list of options to be added to the slash command.
        If the option names and the function parameter names don't match up, an
        error will be raised.
    default_member_permissions : novus.Permissions
        The permissions that are required (by default) to run this command.
        These can be changed by server admins.
    dm_permission : bool
        Whether the command can be run in DMs.
    nsfw : bool
        Whether the comamnd is set to only work in NSFW channels or not.
    guild_ids : list[int]
        The guilds that the command will be added to. If not set, then the
        command will be added globally.

    Raises
    ------
    ValueError
        The command is missing a description.
    Exception
        The command's parameters and the options don't match up.
    """

    def wrapper(func: CommandCallback) -> Command:
        cname = name or func.__name__
        dname = description or func.__doc__ or ""
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
