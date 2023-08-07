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
import importlib.util
import itertools
import json
import logging
import os
import sys
import time
from collections import defaultdict
from functools import partial
from typing import TYPE_CHECKING, Any, Type, cast

from aiohttp import web

import novus as n

if TYPE_CHECKING:
    from types import ModuleType

    from novus.api._cache import APICache

    from .command import Command, CommandGroup
    from .config import Config
    from .plugin import Plugin

__all__ = (
    'Client',
)


log = logging.getLogger("novus.ext.bot.client")
IMPORTED_PLUGIN_MODULES: dict[str, ModuleType] = {}


class Client:
    """
    A gateway and API connection into Discord.

    Attributes
    ----------
    config : novus.ext.client.Config
        The config file for the bot.
    state : novus.api.HTTPConnection
        The connection for the bot.
    plugins : set[novus.ext.client.Plugin]
        A list of plugins that have been added to the bot. This does *not* mean
        that the plugin has been loaded necessarily, just that it has been
        added.
    me : novus.User | None
        The user associated with the bot. Will be ``None`` if the bot has not
        connected to the gateway.
    commands : set[novus.ext.client.Command]
        A list of commands that have been loaded into the bot.
    """

    def __init__(self, config: Config, *, load_plugins: bool = False) -> None:
        self.config: Config = config
        self.state: n.api.HTTPConnection = n.api.HTTPConnection(self.config.token)
        self.state.dispatch = self.dispatch

        self.plugins: set[Plugin] = set()

        self._commands: dict[tuple[int | None, str], Command] = {}
        self._commands_by_id: dict[int, Command] = {}

        sys.path.append(".")
        plugin_modules = itertools.groupby(
            self.config.plugins,
            lambda m: m.split(":")[0],
        )
        for _, lines in plugin_modules:
            self.add_plugin_file(*lines, load=load_plugins)

    @property
    def me(self) -> n.User | None:
        return self.state.cache.user

    @property
    def commands(self) -> set[Command]:
        return set(self._commands.values())

    @property
    def is_ready(self) -> bool:
        for i in self.state.gateway.shards:
            if not i.ready.is_set():
                return False
        return True

    @property
    def cache(self) -> APICache:
        return self.state.cache

    @property
    def guilds(self) -> list[n.Guild]:
        return list(self.cache.guilds.values())

    @property
    def users(self) -> list[n.User]:
        return list(self.cache.users.values())

    @property
    def channels(self) -> list[n.Channel]:
        return list(self.cache.channels.values())

    async def wait_until_ready(self) -> None:
        """
        Wait until all of the shards for the bot have received the "ready"
        message from the gateway.
        """

        for i in self.state.gateway.shards:
            await i.ready.wait()

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

    def add_plugin(self, plugin: Type[Plugin], *, load: bool = False) -> None:
        """
        Load a plugin into the bot.

        Parameters
        ----------
        plugin : Type[novus.ext.client.Plugin]
            The plugin that you want to add to the bot.
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
        self.config._extended[created] = created.CONFIG

        # Run ``.on_load()`` if we've started the event loop.
        if load:
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
        returned = await asyncio.gather(*tasks, return_exceptions=True)
        log.info("Plugin load results: %s", returned)

    def remove_command(self, command: Command) -> None:
        """
        Remove a command from the bot's internal cache.

        Parameters
        ----------
        command : novus.ext.client.Command
            The command you want to remove.

        Raises
        ------
        NameError
            You have tried to remove a command that has not been loaded or is
            not in the cache.
        """

        if command.guild_ids:
            for gid in command.guild_ids:
                key = (gid, command.name,)
                try:
                    self._commands.pop(key)
                except KeyError:
                    raise NameError("Command with name %s is not loaded", command.name)
        else:
            key = (None, command.name,)
            try:
                self._commands.pop(key)
            except KeyError:
                raise NameError("Command with name %s is not loaded", command.name)

    def remove_plugin(self, plugin: Type[Plugin]) -> None:
        """
        Remove a plugin from the bot.

        Parameters
        ----------
        plugin : Type[novus.ext.client.Plugin]
            The plugin type that you want to remove.

        Raises
        ------
        TypeError
            There are no plugins with that plugin type loaded.
        """

        instance = None
        for p in self.plugins:
            if type(p) == plugin:
                instance = p
        if instance is None:
            raise TypeError("Plugin %s is not loaded" % plugin)

        for c in instance._commands:
            self.remove_command(c)
        self.plugins.remove(instance)

        log.info("Removed plugin %s from client instance", instance)

    def add_plugin_file(self, *plugin: str, load: bool = False, reload_import: bool = False) -> None:
        """
        Add a plugin via its filename:ClassName pair.

        Parameters
        ----------
        plugin : str
            The plugin reference.

        Raises
        ------
        TypeError
            No plugin could be loaded from the given reference.
        """

        module = plugin[0].split(":")[0]
        module = importlib.util.resolve_name(module, None)
        if module in IMPORTED_PLUGIN_MODULES and reload_import is False:
            lib = IMPORTED_PLUGIN_MODULES[module]
        else:
            spec = importlib.util.find_spec(module, None)
            if spec is None or spec.loader is None:
                raise TypeError("Missing module %s" % module)
            lib = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(lib)
            IMPORTED_PLUGIN_MODULES[module] = lib
        for p in plugin:
            _, class_name = p.split(":", 1)
            p_class: Type[Plugin] = getattr(lib, class_name)
            self.add_plugin(p_class, load=load)

    def remove_plugin_file(self, *plugin: str) -> None:
        """
        Remove a plugin via its filename:ClassName pair.

        Parameters
        ----------
        plugin : str
            The plugin reference.

        Raises
        ------
        TypeError
            No plugin could be loaded from the given reference.
        """

        module = plugin[0].split(":")[0]
        module = importlib.util.resolve_name(module, None)
        if module in IMPORTED_PLUGIN_MODULES:
            lib = IMPORTED_PLUGIN_MODULES[module]
        else:
            spec = importlib.util.find_spec(module, None)
            if spec is None or spec.loader is None:
                raise TypeError("Missing module %s" % module)
            lib = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(lib)
            IMPORTED_PLUGIN_MODULES[module] = lib
        for p in plugin:
            _, class_name = p.split(":", 1)
            p_class: Type[Plugin] = getattr(lib, class_name)
            self.remove_plugin(p_class)

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

    async def _handle_command_sync(
            self,
            application_id: int,
            guild_id: int | None,
            commands: dict[str, Command]) -> None:
        """
        Handle a guild's list of commands being changed.
        """

        # Set up our requests
        state = self.state.interaction
        if guild_id is None:
            get = partial(state.get_global_application_commands, application_id, with_localizations=True)
            create = partial(state.create_global_application_command, application_id)
            edit = partial(state.edit_global_application_command, application_id)
            delete = partial(state.delete_global_application_command, application_id)
            bulk = partial(state.bulk_overwrite_global_application_commands, application_id)
        else:
            get = partial(state.get_guild_application_commands, application_id, guild_id, with_localizations=True)
            create = partial(state.create_guild_application_command, application_id, guild_id)
            edit = partial(state.edit_guild_application_command, application_id, guild_id)
            delete = partial(state.delete_guild_application_command, application_id, guild_id)
            bulk = partial(state.bulk_overwrite_guild_application_commands, application_id, guild_id)

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
                    log.debug(
                        "Commands different: new %s; current %s",
                        json.dumps(local.application_command._to_data()),
                        json.dumps(dis_com._to_data()),
                    )
                    to_edit[dis_com.id] = local
                local.add_id(guild_id, dis_com.id)
                self._commands_by_id[dis_com.id] = local
        to_add = list(unchecked_local.values())

        # Bulk change
        if len(to_add) + len(to_delete) + len(to_edit) > int(os.getenv("NOVUS_BULK_COMMAND_LIMIT", 10)):
            local_commands = [
                i.application_command._to_data()
                for i in commands.values()
            ]
            log.info("Bulk updating %s app commands in guild %s", len(local_commands), guild_id)
            for dis_com in on_server:
                self._commands_by_id.pop(dis_com.id, None)
            on_server = await bulk(local_commands)
            for dis_com in on_server:
                commands[dis_com.name].add_id(guild_id, dis_com.id)
                self._commands_by_id[dis_com.id] = (
                    self._commands[(guild_id, dis_com.name)]
                )

        # Add new command
        if to_add:
            for comm in to_add:
                log.info("Adding app command %s in guild %s", comm, guild_id)
                on_server = await create(**comm.application_command._to_data())
                comm.add_id(guild_id, on_server.id)
                self._commands_by_id[on_server.id] = comm

        # Delete command
        if to_delete:
            for comm in to_delete:
                log.info("Deleting app command %s in guild %s", comm, guild_id)
                await delete(comm)

        # Edit single command
        if to_edit:
            for id, comm in to_edit.items():
                log.info("Editing app command %s %s in guild %s", id, comm, guild_id)
                await edit(id, **comm.application_command._to_data())

    async def sync_commands(self) -> None:
        """
        Get all commands from Discord. Determine if they all already exist. If
        not, PUT them there. If so, save command IDs.
        This command is required to run to be able to dispatch command events
        properly.
        """

        command_length = [i for i in self._commands.values() if not i.is_subcommand]
        log.info(f"Syncing {len(command_length)} commands")

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
        commands_by_guild = defaultdict(dict)
        for (guild_id, command_name), command in self._commands.items():
            if command.is_subcommand:
                continue  # can't sync command options
            commands_by_guild[guild_id][command_name] = command

        # See which commands we have that exist already
        for guild_id, commands in commands_by_guild.items():
            await self._handle_command_sync(aid, guild_id, commands)

    async def connect(self, check_concurrency: bool = False) -> None:
        """
        Connect the bot to the gateway, running the connection in the
        background.
        """

        concurrency = 1
        if check_concurrency:
            log.info("Checking max concurrency for bot")
            d = await self.state.gateway.get_gateway_bot()
            concurrency = d["session_start_limit"]["max_concurrency"]
            log.info("Set max concurrency to %s", concurrency)
            ws_url = d["url"]
            from novus.api._route import Route
            if Route.WS_BASE == "":
                Route.WS_BASE = ws_url
                log.info("Set websocket connect URL to %s", concurrency)
            else:
                log.info("Ignored websocket connect URL in /gateway/bot due to ENV change")
        log.info("Connecting to gateway")
        await self.state.gateway.connect(
            shard_ids=self.config.shard_ids,
            shard_count=self.config.shard_count,
            intents=self.config.intents,
            max_concurrency=concurrency,
        )

    async def connect_webserver(self, *, port: int = 8000) -> web.BaseSite:
        """
        Open a webserver to receive interactions from Discord.

        Parameters
        ----------
        port : int
            The port to open the server on.
        """

        from nacl.exceptions import BadSignatureError
        from nacl.signing import VerifyKey

        routes = web.RouteTableDef()

        @routes.post("/")
        async def handler(request: web.Request) -> web.StreamResponse:
            verify_key = VerifyKey(bytes.fromhex(self.config.pubkey))
            signature = request.headers["X-Signature-Ed25519"]
            timestamp = request.headers["X-Signature-Timestamp"]
            body = (await request.read()).decode("utf-8")
            try:
                verify_key.verify(
                    f"{timestamp}{body}".encode(),
                    bytes.fromhex(signature),
                )
            except BadSignatureError:
                return web.Response(text="Invalid signature", status=401)

            data: n.payloads.Interaction = await request.json()
            if data["type"] == n.InteractionType.ping.value:
                return web.json_response({"type": 1})
            interaction = n.Interaction(state=self.state, data=data)
            stream = web.StreamResponse()
            interaction._stream = stream
            interaction._stream_request = request
            self.dispatch("INTERACTION_CREATE", interaction)

            t0 = time.time()
            while stream._eof_sent is False and time.time() - t0 < 5.0:
                await asyncio.sleep(0)
            return stream

        app = web.Application()
        app.add_routes(routes)
        runner = web.AppRunner(app)
        await runner.setup()
        webserver = web.TCPSite(
            runner,
            host="0.0.0.0",
            port=port,
        )
        await webserver.start()
        return webserver

    async def close(self) -> None:
        """
        Close the gateway and session connection.
        """

        log.info("Closing bot")
        for i in self.plugins:
            await i.on_unload()
        await self.state.gateway.close()
        await self.state.close()

    async def run(self, *, sync: bool = True) -> None:
        """
        Connect the bot to the gateway, keeping the bot's connection to the
        websocket alive.

        Parameters
        ----------
        sync : bool
            Whether or not to sync the bot's commands to Discord.
        """

        log.info("Running client")
        await self.load_plugins()
        try:
            if sync:
                await self.sync_commands()
            await self.connect(check_concurrency=True)
            try:
                await self.state.gateway.wait()
            except asyncio.CancelledError:
                pass
        finally:
            await self.close()

    async def run_webserver(self, *, port: int = 8000, sync: bool = True) -> None:
        """
        Run a webserver for the bot so as to receive interactions from Discord.

        Parameters
        ----------
        port : int
            The port that you want to open the webserver on.
        sync : bool
            Whether or not to sync the bot's commands to Discord.
        """

        log.info("Running client webserver")
        await self.load_plugins()
        try:
            if sync:
                await self.sync_commands()
            site = await self.connect_webserver(port=port)
            try:
                while True:
                    await asyncio.sleep(60)
            except asyncio.CancelledError:
                pass
            await site.stop()
        finally:
            await self.close()
