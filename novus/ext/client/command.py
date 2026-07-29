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
from typing import TYPE_CHECKING, Any, Awaitable, Type, TypeAlias, Union, cast

from typing_extensions import Self, TypeVarTuple, override

import novus as n

from .errors import CommandError

if TYPE_CHECKING:
    Ts = TypeVarTuple('Ts')
    AnyCoro: TypeAlias = Union[Coroutine[Any, Any, Any], Awaitable[Any]]
    # CommandCallback: TypeAlias = Union[
    #     Callable[
    #         [Any, n.types.CommandI, Unpack[Ts]],
    #         AnyCoro
    #     ],
    #     Callable[
    #         [Any, n.types.CommandI],
    #         AnyCoro
    #     ],
    #     Callable[
    #         [Any, n.types.CommandGI, Unpack[Ts]],
    #         AnyCoro
    #     ],
    #     Callable[
    #         [Any, n.types.CommandGI],
    #         AnyCoro
    #     ],
    #     Callable[
    #         [n.types.CommandI, Unpack[Ts]],
    #         AnyCoro
    #     ],
    #     Callable[
    #         [n.types.CommandI],
    #         AnyCoro
    #     ],
    #     Callable[
    #         [n.types.CommandGI, Unpack[Ts]],
    #         AnyCoro
    #     ],
    #     Callable[
    #         [n.types.CommandGI],
    #         AnyCoro
    #     ],
    # ]
    CommandCallback: TypeAlias = Callable[..., AnyCoro]
    AutocompleteCallback: TypeAlias = Union[
        Callable[
            [
                Any,
                n.Interaction[n.ApplicationCommandData],
                dict[str, n.InteractionOption],
            ],
            Coroutine[Any, Any, list[n.ApplicationCommandChoice] | None],
        ],
        Callable[
            [
                Any,
                n.Interaction[n.ApplicationCommandData],
            ],
            Coroutine[Any, Any, list[n.ApplicationCommandChoice] | None],
        ],
    ]

    LocType: TypeAlias = dict[str, str] | n.utils.Localization | None


__all__ = (
    'Command',
    'CommandGroup',
    'CommandDescription',
    'command',
)


log = logging.getLogger("novus.ext.client.command")


class Command:
    """
    A command object for Novus command handling.

    Parameters
    ----------
    name: str
        The name of the command
    type : int
        The type of the command.

        .. seealso:: `novus.ApplicationCommandType`
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
    type : int
        The type of the command.

        .. seealso:: `novus.ApplicationCommandType`
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
    type: int
    callback: CommandCallback
    application_command: n.PartialApplicationCommand
    guild_ids: list[int]
    command_ids: dict[int, int]  # guild_id, command_id
    is_subcommand: bool

    def __init__(
            self,
            name: str,
            type: int,
            application_command: n.PartialApplicationCommand,
            callback: CommandCallback,
            guild_ids: list[int]):
        self.name = name
        self.type = type
        self.callback = callback
        self.application_command = application_command
        self.guild_ids = guild_ids
        self.command_ids = {}
        self.is_subcommand = (
            self.type == n.ApplicationCommandType.CHAT_INPUT
            and " " in self.name
        )
        self.owner: Any = None
        self._autocomplete: AutocompleteCallback | None = None

        # Make sure our callback and app command have similar options
        if self.type == n.ApplicationCommandType.CHAT_INPUT:
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
                if option.name.replace("-", "_") != pname:
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
            description=self.application_command.description,  # pyright: ignore
            type=n.ApplicationOptionType.SUB_COMMAND,
            name_localizations=self.application_command.name_localizations,
            description_localizations=self.application_command.description_localizations,
            options=self.application_command.options,
        )

    __repr__ = n.utils.generate_repr(('name',))

    def add_id(self, guild_id: int | None, id: int) -> None:
        """
        Add an ID to the command. This means that any interaction invokations
        with the given command ID will be routed to this command instance.

        Parameters
        ----------
        id : int
            The ID that you want to add.
        """

        self.command_ids[guild_id or 0] = id

    @property
    def mention(self) -> str:
        return self.get_mention()

    def get_mention(self, guild_id: int | None = None) -> str:
        """
        Get a mention for the given command.

        Parameters
        ----------
        guild_id : int | None
            The ID of the guild that the command exists in.

        Returns
        -------
        str
            A mention for the command.
        """

        if guild_id is None:
            id = self.command_ids[0]
        else:
            id = self.command_ids[guild_id]
        return f"</{self.name}:{id}>"

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

        # See if we got options for the interaction
        if options is None:
            try:
                options = interaction.data.options  # pyright: ignore
            except AttributeError:
                options = []
        assert options is not None

        # Go through each and make sure we have a real value for it
        for option in options:
            data: Any = option.value
            if option.type == n.ApplicationOptionType.CHANNEL:
                data_id = int(data)
                data = interaction.data.resolved.channels.get(data_id)
            elif option.type == n.ApplicationOptionType.ATTACHMENT:
                data_id = int(data)
                data = interaction.data.resolved.attachments.get(data_id)
            elif option.type == n.ApplicationOptionType.USER:
                data_id = int(data)
                data = interaction.data.resolved.members.get(data_id)
                if data is None:
                    data = interaction.data.resolved.users.get(data_id)
            elif option.type == n.ApplicationOptionType.ROLE:
                data_id = int(data)
                data = interaction.data.resolved.roles.get(data_id)
            elif option.type == n.ApplicationOptionType.MENIONABLE:
                data_id = int(data)
                data = interaction.data.resolved.roles.get(data_id)
                if data is None:
                    data = interaction.data.resolved.members.get(data_id)
                if data is None:
                    data = interaction.data.resolved.users.get(data_id)
            kwargs[option.name.replace("-", "_")] = data

        # See if we have any "special" values
        ignore: int = 2
        sig = inspect.signature(self.callback)
        for k, v in sig.parameters.items():
            if ignore > 0:
                ignore -= 1
                continue
            if k in kwargs:
                continue
            if v.default is n.utils.CommandDefault.AUTHOR:
                kwargs[k] = interaction.user
            elif v.default is n.utils.CommandDefault.CHANNEL:
                kwargs[k] = interaction.channel

        log.info("Command invoked, %s %s", self, interaction)
        partial = functools.partial(self.callback, self.owner, interaction)
        match self.application_command.type:
            case n.ApplicationCommandType.USER | n.ApplicationCommandType.MESSAGE:
                await partial(interaction.data.target)  # pyright: ignore
            case _:
                await partial(**kwargs)

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return await self.callback(self.owner, *args, **kwargs)

    def autocomplete(self, func: AutocompleteCallback) -> AutocompleteCallback:
        """
        Add an autocomplete to this command.

        Examples
        --------

        .. code-block::

            @client.command(...)
            async def echo(self, ctx: novus.Interaction, text: str):
                ...

            @echo.autocomplete
            async def echo_autocomplete(self, ctx: novus.Interaction):
                return [
                    novus.ApplicationCommandChoice("name", "value"),
                    novus.ApplicationCommandChoice("name2", "value2"),
                    novus.ApplicationCommandChoice("name3", "value3"),
                ]
        """

        self._autocomplete = func
        return func

    async def run_autocomplete(
            self,
            interaction: n.Interaction[n.ApplicationCommandData],
            options: list[n.InteractionOption] | None = None) -> None:
        """
        This interaction has been triggered to autocomplete! Work out what
        parameter needs autocompleting, and then run that :)

        Parameters
        ----------
        interaction : novus.Interaction
            The interaction that needs completing.
        """

        if self._autocomplete is None:
            return
        options = options or interaction.data.options
        if hasattr(self._autocomplete, "_param_count"):
            param_count = self._autocomplete._param_count
        else:
            param_count = len(inspect.signature(self._autocomplete).parameters)
            self._autocomplete._param_count = param_count  # type: ignore
        if param_count == 3:
            data = await self._autocomplete(  # type: ignore
                self.owner,
                interaction,
                {i.name: i for i in options},  # pyright: ignore
            )
        else:
            data = await self._autocomplete(  # type: ignore
                self.owner,
                interaction,
            )  # pyright: ignore
        if data is None:
            return await interaction.send_autocomplete([])
        return await interaction.send_autocomplete(data)

    def get_parsed_command(
            self,
            interaction: n.Interaction[n.ApplicationCommandData]
            ) -> tuple[Command, n.InteractionOption | None]:
        """
        Fold down a command into its qualified subcommand given an interaction invokation.

        Parameters
        ----------
        interaction : novus.Interaction
            The interaction that was invoked.

        Returns
        -------
        tuple[novus.Command, novus.InteractionOption | None]
            A tuple of the command that will be run, and the option inside of the interaction that
            the subcommand corresponds to (or ``None`` if the invoked command is not a subcommand).
        """

        return self, None


class CommandGroup(Command):
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
        self.command_ids = {}
        self.commands: dict[str, Command] = {
            i.name: i
            for i in commands
        }
        for c in self.commands.values():
            c.command_ids = self.command_ids

    __repr__ = n.utils.generate_repr(('name',))

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
            self.guild_ids = d.guild_ids  # type: ignore

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
            if d.integration_types is not n.utils.MISSING:
                app.integration_types = d.integration_types
            if d.contexts is not n.utils.MISSING:
                app.contexts = d.contexts
        for option in app.options:
            if option.name in d.children:
                cls._add_description(option, d.children[option.name])

    @classmethod
    def from_commands(
            cls,
            commands: set[Command] | list[Command] | tuple[Command],
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
            raise CommandError("Cannot have multiple base names for group (command %s)" % names[0])

        # Do the same again for the translations
        t_names: dict[str, dict[int, set[str]]]
        t_names = collections.defaultdict(lambda: collections.defaultdict(set))  # depth: name
        for comm in commands:
            for language, comm_name in comm.application_command.name_localizations.items():
                name_split = comm_name.split(" ")
                for depth, name_segment in enumerate(name_split):
                    t_names[language][depth].add(name_segment)
        for lang in t_names:
            if len(t_names[lang][0]) > 1:
                raise CommandError(
                    "Cannot have multiple base names for group (command %s) (language %s)"
                    % (t_names[lang][0], lang)
                )

        # Do some other validity checks
        permission_set = None
        dm_permission_set = None
        nsfw_set = None
        guild_ids_set = None
        integration_set = None
        contexts_set = None
        if run_checks:
            permission_set = set(
                i.application_command.default_member_permissions
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
            integration_set = set(
                tuple(i.application_command.integration_types or ())
                for i in command_map.values()
            )
            if len(integration_set) > 1:
                raise CommandError("Cannot have different integration types for group")
            contexts_set = set(
                tuple(i.application_command.contexts or ())
                for i in command_map.values()
            )
            if len(contexts_set) > 1:
                raise CommandError("Cannot have different guild IDs for group")
        for i in commands:  # make this a loop but get the first item only by breaking
            permission_final = i.application_command.default_member_permissions
            dm_permission_final = i.application_command.dm_permission
            nsfw_final = i.application_command.nsfw
            integration_final = i.application_command.integration_types
            contexts_final = i.application_command.contexts
            guild_ids_final = i.guild_ids
            break
        else:
            raise CommandError("No commands provided to group")

        # Make up a place for our options to go after we've built them
        built_options: dict[tuple[str, ...], n.ApplicationCommandOption] = {}
        first_command = list(commands)[0]
        app = n.PartialApplicationCommand(
            name=list(names[0])[0],
            description="...",
            type=n.ApplicationCommandType.CHAT_INPUT,
            default_member_permissions=permission_final,
            dm_permission=dm_permission_final,
            nsfw=nsfw_final,
            integration_types=integration_final,
            contexts=contexts_final,
            name_localizations={
                lang: name.split(" ")[0]
                for lang, name in first_command.application_command.name_localizations.items()
            },
        )
        built_options[()] = app  # pyright: ignore

        # Build up the subcommand groups
        for (_, *group, _), command in command_map.items():
            group_tuple = ()
            for group_index, group_name in enumerate(group, start=1):
                group_tuple = tuple(group[:group_index])  # type: ignore
                if group_tuple not in built_options:
                    built_options[group_tuple] = new = n.ApplicationCommandOption(
                        name=group_name,
                        description="...",
                        type=n.ApplicationOptionType.SUB_COMMAND_GROUP,
                    )
                    parent_group = tuple(group[:group_index - 1])
                    built_options[parent_group].add_option(new)
            original_localizations = command.application_command.name_localizations
            command.application_command.name_localizations = n.utils.Localization({
                lang: name.split(" ", 1)[1]
                for lang, name in original_localizations.items()
            })
            built_options[group_tuple].add_option(command.to_application_command_option())

        return cls(
            app,
            commands,
            guild_ids_final,
        )

    @override
    async def run(  # type: ignore
            self,
            interaction: n.Interaction[n.ApplicationCommandData]) -> None:
        """
        Run the command with the given interaction.

        Parameters
        ----------
        interaction : novus.Interaction
            The interaction that invoked the command.
        """

        command, option = self.get_parsed_command(interaction)
        assert option is not None, "Impossible state for a CommandGroup with a real Interaction"
        return await command.run(interaction, option.options)

    @override
    async def run_autocomplete(  # type: ignore
            self,
            interaction: n.Interaction[n.ApplicationCommandData]) -> None:
        """
        Run the autocomplete for the given command with the given options.

        Parameters
        ----------
        interaction : novus.Interaction
            The interaction that invoked the autocomplete.
        """

        command, option = self.get_parsed_command(interaction)
        assert option is not None, "Impossible state for a CommandGroup with a real Interaction"
        return await command.run_autocomplete(interaction, option.options)

    def get_parsed_command(
            self,
            interaction: n.Interaction[n.ApplicationCommandData]
            ) -> tuple[Command, n.InteractionOption | None]:
        """
        Fold down a command into its qualified subcommand given an interaction invokation.

        Parameters
        ----------
        interaction : novus.Interaction
            The interaction that was invoked.

        Returns
        -------
        tuple[novus.Command, novus.InteractionOption | None]
            A tuple of the command that will be run, and the option inside of the interaction that
            the subcommand corresponds to (or ``None`` if the invoked command is not a subcommand).
        """

        command_name_parts = [self.name]
        option = interaction.data.options[0]
        while option.type == n.ApplicationOptionType.SUB_COMMAND_GROUP:
            command_name_parts.append(option.name)
            option = option.options[0]
        command = self.commands[" ".join([*command_name_parts, option.name])]
        return command, option


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
            children: dict[str, CommandDescription] | None = None,
            integration_types: list[int] | None = n.utils.MISSING,
            contexts: list[int] | None = n.utils.MISSING) -> None:
        self.description = description
        self.name_localizations = n.utils.flatten_localization(name_localizations)
        self.description_localizations = n.utils.flatten_localization(description_localizations)
        self.default_member_permissions = default_member_permissions
        self.dm_permission = dm_permission
        self.nsfw = nsfw
        self.guild_ids = guild_ids
        self.children: dict[str, CommandDescription] = children or {}
        self.integration_types = integration_types
        self.contexts = contexts

    __repr__ = n.utils.generate_repr(('description',))


def command(
        name: str | None = None,
        description: str | None = None,
        type: int = n.ApplicationCommandType.CHAT_INPUT,
        *,
        options: list[n.ApplicationCommandOption] | None = None,
        default_member_permissions: n.Permissions | None = None,
        dm_permission: bool = True,
        nsfw: bool = False,
        integration_types: list[int] | None = None,
        contexts: list[int] | None = None,
        guild_ids: list[int] | None = None,
        cls: Type[Command] = Command,
        **kwargs: Any) -> Callable[[CommandCallback], Command]:
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
    type : int
        The type of the command that you want to create.

        .. seealso:: `novus.ApplicationCommandType`
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
    integration_types : list[int] | None
        The integration types that the command will be added to.

        .. seealso:: `novus.ApplicationIntegrationType`
    contexts : list[int] | None
        The contexts in which this command can be run.

        .. seealso:: `novus.ApplicationCommandContext`
    guild_ids : list[int]
        The guilds that the command will be added to. If not set, then the
        command will be added globally.

    Raises
    ------
    ValueError
        The command is missing a description.
    Exception
        The command's parameters and the options don't match up.

    Examples
    --------

    .. code-block::

        @client.command()
        async def ping(self, ctx):
            '''Command description goes here.'''
            await ctx.send("Pong")

    .. code-block::

        @client.command(
            options=[
                novus.ApplicationCommandOption(
                    name="user",
                    type=novus.ApplicationOptionType.USER,
                    description="The user you want to mention.",
                )
            ]
        )
        async def mention(self, ctx, user):
            '''Command description goes here.'''
            await ctx.send(user.mention)
    """

    def wrapper(func: CommandCallback) -> Command:
        cname = name or func.__name__
        dname = description or func.__doc__ or ""
        if type != n.ApplicationCommandType.CHAT_INPUT:
            dname = None  # type: ignore
        else:
            dname = dname.strip()
        return cls(
            name=cname,
            type=type,
            application_command=n.PartialApplicationCommand(
                name=cname,
                description=dname,
                type=type,
                options=options or [],
                default_member_permissions=default_member_permissions,
                dm_permission=dm_permission,
                nsfw=nsfw,
                integration_types=integration_types,
                contexts=contexts,
                **kwargs
            ),
            guild_ids=guild_ids or [],
            callback=func,
        )
    return wrapper
