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
import re
import sys
import textwrap
from argparse import REMAINDER, ArgumentParser, Namespace
from typing import TYPE_CHECKING, Any, NoReturn

from aioconsole import AsynchronousCli

import novus
from novus.api._cache import NothingAPICache
from novus.ext import client

if TYPE_CHECKING:
    from asyncio import StreamReader, StreamWriter


class GuildLogger(client.Plugin):

    async def print_loop(self, sleep_time: float = 60.0) -> None:
        self.log.info(
            "Starting guild logger loop; printing guild count every %s seconds",
            sleep_time,
        )
        while True:
            self.log.info(
                "There are currently %s guild IDs in cache",
                len(self.bot.state.cache.guild_ids),
            )
            try:
                await asyncio.sleep(sleep_time)
            except asyncio.CancelledError:
                break

    async def on_load(self) -> None:
        await self.bot.wait_until_ready()
        self.print_loop_task = asyncio.create_task(self.print_loop())

    async def on_unload(self) -> None:
        if not self.print_loop_task.done():
            self.print_loop_task.cancel()

    @client.event("GUILD_CREATE")
    async def guild_added(self, guild: novus.Guild) -> None:
        if self.bot.is_ready:
            if isinstance(guild, novus.Guild):
                self.log.info("Guild create (%s) %s", guild.id, guild.name)
            elif isinstance(guild, novus.Object):
                self.log.info("Guild create (%s)", guild.id)
            else:
                self.log.info("Guild create (%s)", guild)

    @client.event("GUILD_DELETE")
    async def guild_removed(self, guild: novus.Guild | int) -> None:
        if isinstance(guild, int):
            self.log.info("Guild delete (%s)", guild)
        else:
            self.log.info("Guild delete (%s) %s", guild.id, guild.name)


def get_parser() -> ArgumentParser:
    p = ArgumentParser("novus")

    ap = p.add_subparsers(dest="action", required=True)
    logger_choices: list[str] = []
    for i in ["debug", "info", "warning", "error"]:
        logger_choices.extend((i, i.upper(),))

    rap = ap.add_parser("run")
    rap.add_argument("--config", nargs="?", const=None, default=None)
    rap.add_argument("--loglevel", default='info', choices=logger_choices)
    rap.add_argument("--no-sync", default=False, action="store_true")
    rap.add_argument("--token", nargs="?", type=str, default=None)
    rap.add_argument("--shard-id", nargs="*", type=str, default=None)
    rap.add_argument("--shard-ids", nargs="?", type=str, const="", default=None)
    rap.add_argument("--shard-count", nargs="?", type=str, default=None)
    rap.add_argument("--intents", nargs="?", type=str, const="", default=None)
    rap.add_argument("--intent", nargs="*", type=str, default=None)
    rap.add_argument("--no-intents", nargs="?", type=str, const="", default=None)
    rap.add_argument("--no-intent", nargs="*", type=str, default=None)
    rap.add_argument("--plugins", nargs="?", type=str, const="", default=None)
    rap.add_argument("--plugin", nargs="*", type=str, default=None)

    rwsap = ap.add_parser("run-webserver")
    rwsap.add_argument("--config", nargs="?", const=None, default=None)
    rwsap.add_argument("--port", nargs="?", type=int, default=8000)
    rwsap.add_argument("--loglevel", default='info', choices=logger_choices)
    rwsap.add_argument("--no-sync", default=False, action="store_true")
    rwsap.add_argument("--token", nargs="?", type=str, default=None)
    rwsap.add_argument("--pubkey", nargs="?", type=str, default=None)
    rwsap.add_argument("--plugins", nargs="?", type=str, const="", default=None)
    rwsap.add_argument("--plugin", nargs="*", type=str, default=None)

    rsap = ap.add_parser("run-status")
    rsap.add_argument("--config", nargs="?", const=None, default=None)
    rsap.add_argument("--loglevel", default='info', choices=logger_choices)
    rsap.add_argument("--token", nargs="?", type=str, default=None)
    rsap.add_argument("--shard-id", nargs="*", type=str, default=None)
    rsap.add_argument("--shard-ids", nargs="?", type=str, const="", default=None)
    rsap.add_argument("--shard-count", nargs="?", type=str, default=None)

    cap = ap.add_parser("config-dump")
    cap.add_argument("type", choices=["json", "yaml", "toml"])
    cap.add_argument("--token", nargs="?", type=str, default=None)
    cap.add_argument("--pubkey", nargs="?", type=str, default=None)
    cap.add_argument("--shard-id", nargs="*", type=str, default=None)
    cap.add_argument("--shard-ids", nargs="?", type=str, const="", default=None)
    cap.add_argument("--shard-count", nargs="?", type=str, default=None)
    cap.add_argument("--intents", nargs="?", type=str, const="", default=None)
    cap.add_argument("--intent", nargs="*", type=str, default=None)
    cap.add_argument("--no-intents", nargs="?", type=str, const="", default=None)
    cap.add_argument("--no-intent", nargs="*", type=str, default=None)
    cap.add_argument("--plugins", nargs="?", type=str, const="", default=None)
    cap.add_argument("--plugin", nargs="*", type=str, default=None)

    np = ap.add_parser("new-plugin")
    np.add_argument("name")
    np.add_argument("commands", nargs="*", default=[])

    return p


class CustomCloseCLI(AsynchronousCli):

    def __init__(self, *args: Any, bot: client.Client, **kwargs: Any):
        super().__init__(*args, *kwargs)
        self.bot = bot

    async def exit_command(self, reader: StreamReader, writer: StreamWriter) -> NoReturn:
        await self.bot.close()
        writer.close()
        raise SystemExit


def create_console(bot: client.Client) -> AsynchronousCli:
    """
    Create a console that users are able to interact with while the bot is
    running.
    """

    plugin_parser = ArgumentParser()
    plugin_parser.add_argument("plugin")
    run_parser = ArgumentParser()
    run_parser.add_argument("command", nargs=REMAINDER)
    command_locals: dict[str, Any] = {}

    async def add(reader: Any, writer: Any, plugin: str) -> None:
        bot.add_plugin_file(plugin, load=True)

    async def remove(reader: Any, writer: Any, plugin: str) -> None:
        bot.remove_plugin_file(plugin)

    async def reload(reader: Any, writer: Any, plugin: str) -> None:
        bot.remove_plugin_file(plugin)
        bot.add_plugin_file(plugin, load=True, reload_import=True)

    async def run_state(reader: Any, writer: asyncio.StreamWriter, command: list[str]) -> None:
        command_full = " ".join(command)
        match = re.search(r"^((\S+) ?= ?)?(await )?(.*)", command_full)
        assert match is not None
        store = match.group(2) or "_"
        await_ = bool(match.group(3))
        command_string = match.group(4)
        ret = eval(
            command_string,
            {
                **globals(),
                "asyncio": asyncio,
                "novus": novus,
                "bot": bot,
                **command_locals
            },
        )
        if await_:
            ret = await ret
        command_locals[store] = ret
        command_locals["_"] = ret
        writer.write(repr(ret).encode())
        writer.write(b"\n")

    return CustomCloseCLI(
        {
            "add-plugin": (add, plugin_parser,),
            "remove-plugin": (remove, plugin_parser,),
            "reload-plugin": (reload, plugin_parser,),

            "add": (add, plugin_parser,),
            "remove": (remove, plugin_parser,),
            "reload": (reload, plugin_parser,),

            "eval": (run_state, run_parser,),
        },
        bot=bot,
    )


async def main(args: Namespace, unknown: list[str]) -> None:
    """
    Main input point for our CLI.
    """

    match args.action:
        case "run":
            config = client.Config.from_file(args.config)
            if "loglevel" in args:
                level = getattr(logging, args.loglevel.upper())
            else:
                level = logging.INFO
            root = logging.Logger.root
            root.setLevel(level)
            config.merge_namespace(args, unknown)
            bot = client.Client(config)
            await asyncio.gather(
                bot.run(sync=not args.no_sync),
                create_console(bot).interact(
                    banner="Interactive bot console created; try \"help\".",
                    stop=False,
                    handle_sigint=False,
                ),
            )

        case "run-webserver":
            config = client.Config.from_file(args.config)
            if "loglevel" in args:
                level = getattr(logging, args.loglevel.upper())
            else:
                level = logging.INFO
            root = logging.Logger.root
            root.setLevel(level)
            config.merge_namespace(args, unknown)
            bot = client.Client(config)
            await asyncio.gather(
                bot.run_webserver(sync=not args.no_sync, port=args.port),
                create_console(bot).interact(banner="Created console :)", stop=False),
            )

        case "run-status":
            config = client.Config.from_file(args.config)
            if "loglevel" in args:
                root = logging.Logger.root
                level = getattr(logging, args.loglevel.upper())
                root.setLevel(level)
            config.merge_namespace(args, unknown)
            config.plugins = []
            config.intents = novus.Intents(guilds=True)
            bot = client.Client(config)
            bot.state.cache = NothingAPICache(bot.state)
            bot.state.gateway.guild_ids_only = True
            bot.add_plugin(GuildLogger)
            await bot.run(sync=False)

        case "config-dump":
            config = client.Config()
            logging.Logger.root.setLevel(logging.ERROR)
            config.merge_namespace(args, unknown)
            match args.type:
                case "yaml":
                    print(config.to_yaml())
                case "json":
                    print(config.to_json())
                case "toml":
                    print(config.to_toml())

        case "new-plugin":
            plugin = textwrap.dedent("""
                import novus as n
                from novus import types as t
                from novus.utils import Localization as LC
                from novus.ext import client


                class {plugin}(client.Plugin):
            """).format(plugin=args.name).strip() + "\n"
            if not args.commands:
                plugin += " " * 4 + "...\n"
            for i in args.commands:
                typesafe_name = "_".join(i.split(" ")[::-1])
                command = textwrap.indent(textwrap.dedent("""
                    @client.command(name="{name}")
                    async def {typesafe_name}(self, ctx: t.CommandI) -> None:
                        ...
                """).strip(), " " * 4).format(name=i, typesafe_name=typesafe_name)
                plugin += "\n" + command + "\n"
            print(plugin)


class MaxLevelFilter(logging.Filter):
    """
    A filter that removes anything above a certain level.
    """

    def __init__(self, max_level: int) -> None:
        self.max_level = max_level

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno <= self.max_level


def main_sync() -> None:
    stderr = logging.StreamHandler(sys.stderr)
    stderr.setLevel(logging.WARNING)
    stdout = logging.StreamHandler(sys.stdout)
    stdout.addFilter(MaxLevelFilter(logging.INFO))
    stdout.setLevel(logging.DEBUG)
    logging.basicConfig(
        level=logging.INFO,
        handlers=[stdout, stderr,],
        format="%(created)s:%(levelname)s:%(name)s:%(message)s",
    )
    args, unknown = get_parser().parse_known_args()
    try:
        asyncio.run(main(args, unknown))
    except KeyboardInterrupt:
        pass  # Silence, commandline


if __name__ == "__main__":
    main_sync()
