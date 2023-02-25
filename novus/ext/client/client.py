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

import asyncio
import logging
from collections import defaultdict
from functools import partial
from typing import TYPE_CHECKING, Any, Type, cast

import novus as n

if TYPE_CHECKING:
    from .command import Command, CommandGroup
    from .config import Config
    from .plugin import Plugin

__all__ = (
    'Client',
)


log = logging.getLogger("novus.ext.bot.client")


class Client:
    """
    A gateway and API connection into Discord.
    """

    def __init__(self, config: Config) -> None:
        self.config = config
        self.state = n.api.HTTPConnection(self.config.token)
        self.state.dispatch = self.dispatch

        self.plugins: set[Plugin] = set()
        self._commands: dict[tuple[int | None, str], Command] = {}
        self._commands_by_id: dict[int, Command] = {}

    @property
    def commands(self):
        return set(self._commands.values())

    def add_command(self, command: Command) -> None:
        """
        Add a command to the bot's internal cache.

        Parameters
        ----------
        command : novus.ext.client.Command
            The command you want to add.

        Raises
        ------
        NameError
            You have tried to add a command with a duplicate name (and guild
            status) as an already cached command.
        """

        if command.guild_ids:
            for gid in command.guild_ids:
                key = (gid, command.name,)
                if key in self._commands:
                    raise NameError("Command with duplicate name %s guild ID %s" % key)
                self._commands[key] = command
        else:
            key = (None, command.name,)
            if key in self._commands:
                raise NameError("Command with duplicate name %s" % command.name)
            self._commands[key] = command

    def get_command(
            self,
            name: str,
            guild_id: int | None = None) -> Command | CommandGroup | None:
        """
        Get a command that's been loaded into the bot from the cache.

        Parameters
        ----------
        name : str
            The name of the command thaty ou want to get.
        guild_id : int | None
            The ID of the guild where the command is registered.

        Returns
        -------
        novus.ext.client.Command | novus.ext.client.CommandGroup
            The command from the command cache.
        """

        return self._commands.get((guild_id, name,))

    def add_plugin(self, plugin: Type[Plugin]) -> None:
        """
        Load a plugin into the bot.
        """

        try:
            created: Plugin = plugin(self)
        except Exception as e:
            log.error(f"Failed to load plugin {plugin} via __init__", exc_info=e)
            return
        log.info(f"Added plugin {created} to client instance")
        self.plugins.add(created)
        for c in created._commands:
            self.add_command(c)

        # Run ``.on_load()`` if we've started the event loop.
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            pass
        else:
            asyncio.create_task(
                self._add_plugin_load(created),
                name=f"{plugin.__name__}.on_load()",
            )

    async def _add_plugin_load(self, plugin: Plugin) -> None:
        """
        Run a plugin's ``on_load``, removing it if it failed.
        """

        try:
            await plugin.on_load()
        except Exception as e:
            self.plugins.remove(plugin)
            log.error(f"Failed to load plugin {plugin} via on_load", exc_info=e)

    async def load_plugins(self) -> None:
        """
        Load all of the plugins that have been added to the bot.
        """

        log.info(f"Loading {len(self.plugins)} plugins")
        tasks = []
        for p in self.plugins:
            t = asyncio.create_task(
                self._add_plugin_load(p),
                name=f"{p.__class__.__name__}.on_load()",
            )
            tasks.append(t)
        await asyncio.gather(*tasks)

    def dispatch(self, event_name: str, *args: Any, **kwargs: Any) -> None:
        """
        Dispatch an event to all loaded plugins.
        """

        if event_name == "INTERACTION_CREATE":
            interaction: n.Interaction = args[0]
            if interaction.type in [
                    n.InteractionType.application_command,
                    n.InteractionType.autocomplete]:
                interaction = cast(n.Interaction[n.ApplicationCommandData], interaction)
                try:
                    command = self._commands_by_id[interaction.data.id]
                except KeyError:
                    log.warning(
                        "Failed to get cached command with ID %s (%s)"
                        % (interaction.data.id, interaction)
                    )
                else:
                    if interaction.type == n.InteractionType.application_command:
                        asyncio.create_task(
                            command.run(interaction),
                            name=f"Command invoke from interaction ({interaction.id})"
                        )
                    elif interaction.type == n.InteractionType.autocomplete:
                        asyncio.create_task(
                            command.run_autocomplete(interaction),
                            name=f"Command invoke from interaction ({interaction.id})"
                        )
                    else:
                        log.error("Failed to run interaction command %s" % interaction)

        for p in self.plugins:
            p.dispatch(event_name, *args, **kwargs)

    async def sync_commands(self) -> None:
        """
        Get all commands from Discord. Determine if they all already exist. If
        not, PUT them there. If so, save command IDs.
        """

        log.info("Syncing commands")

        # Get application ID
        aid: int | None = self.state.cache.application_id
        if aid is None:
            app = self.state.cache.application
            if app is None:
                app = await self.state.oauth2.get_current_bot_information()
                self.state.cache.application = app
                aid = app.id
        assert aid

        # Group our commands by guild ID
        commands_by_guild: dict[int | None, dict[str, Command]]
        commands_by_guild = defaultdict(partial(defaultdict, dict))
        for (guild_id, command_name), command in self._commands.items():
            if command.is_subcommand:
                continue  # can't sync command options
            commands_by_guild[guild_id][command_name] = command

        # See which commands we have that exist already
        for guild_id, commands in commands_by_guild.items():

            # Set up our requests
            state = self.state.interaction
            if guild_id is None:
                get = partial(state.get_global_application_commands, aid)
                bulk = partial(state.bulk_overwrite_global_application_commands, aid)
                create = partial(state.create_global_application_command, aid)
                edit = partial(state.edit_global_application_command, aid)
                delete = partial(state.delete_global_application_command, aid)
            else:
                get = partial(state.get_guild_application_commands, aid, guild_id)
                bulk = partial(state.bulk_overwrite_guild_application_commands, aid, guild_id)
                create = partial(state.create_guild_application_command, aid, guild_id)
                edit = partial(state.edit_guild_application_command, aid, guild_id)
                delete = partial(state.delete_guild_application_command, aid, guild_id)

            # See what we need to do
            on_server = await get()
            unchecked_local = commands.copy()
            to_add: list[Command] = []
            to_delete: list[int] = []
            to_edit: dict[int, Command] = {}
            for dis_com in on_server:
                try:
                    local = unchecked_local.pop(dis_com.name)
                except KeyError:
                    to_delete.append(dis_com.id)
                else:
                    if local.application_command._to_data() != dis_com._to_data():
                        to_edit[dis_com.id] = local
                    local.command_ids.add(dis_com.id)
                    self._commands_by_id[dis_com.id] = local
            to_add = list(unchecked_local.values())

            # Do everything of interest
            if len(to_add) + len(to_delete) + len(to_edit) > 1:
                local_commands = [
                    i.application_command._to_data()
                    for i in commands.values()
                ]
                log.info(
                    "Bulk updating %s app commands in guild %s"
                    % (len(local_commands), guild_id)
                )
                for dis_com in on_server:
                    self._commands_by_id.pop(dis_com.id, None)
                on_server = await bulk(local_commands)
                for dis_com in on_server:
                    commands[dis_com.name].add_id(dis_com.id)
                    self._commands_by_id[dis_com.id] = self._commands[(guild_id, dis_com.name)]
            elif to_add:
                log.info(
                    "Adding app command %s in guild %s"
                    % (to_add[0], guild_id)
                )
                on_server = await create(**to_add[0].application_command._to_data())
                to_add[0].command_ids.add(on_server.id)
                self._commands_by_id[on_server.id] = to_add[0]
            elif to_delete:
                log.info(
                    "Deleting app command %s in guild %s"
                    % (to_delete[0], guild_id)
                )
                await delete(to_delete[0])
            elif to_edit:
                for id, comm in to_edit.items():
                    log.info(
                        "Editing app command %s %s in guild %s"
                        % (id, comm, guild_id)
                    )
                    await edit(id, **comm.application_command._to_data())

    async def connect(self) -> None:
        """
        Connect the bot to the gateway, running the connection in the
        background.
        """

        log.info("Connecting to gateway")
        await self.state.gateway.connect(
            shard_ids=self.config.shard_ids,
            shard_count=self.config.shard_count,
            intents=self.config.intents,
        )

    async def close(self) -> None:
        """
        Close the gateway and session connection.
        """

        log.info("Closing bot")
        await self.state.gateway.close()
        await (await self.state.get_session()).close()

    async def run(self, sync: bool = True) -> None:
        """
        Connect the bot to the gateway, keeping the bot's connection to the
        websocket alive.
        """

        log.info("Running client")
        await self.load_plugins()
        if sync:
            await self.sync_commands()
        await self.connect()
        try:
            await self.state.gateway.wait()
        except asyncio.CancelledError:
            pass
        await self.close()
