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
import sys
import textwrap
from argparse import ArgumentParser, Namespace
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from _typeshed import SupportsWrite

from novus.ext import client


def get_parser() -> ArgumentParser:
    p = ArgumentParser("novus")

    ap = p.add_subparsers(dest="action", required=True)

    rap = ap.add_parser("run")
    rap.add_argument("--config", nargs="?", const=None, default=None)
    logger_choices = []
    for i in ["debug", "info", "warning", "error"]:
        logger_choices.extend((i, i.upper(),))
    rap.add_argument("--loglevel", default='info', choices=logger_choices)
    rap.add_argument("--no-sync", default=False, action="store_true")
    rap.add_argument("--token", nargs="?", type=str, default=None)
    rap.add_argument("--shard_id", nargs="*", type=str, default=None)
    rap.add_argument("--shard_ids", nargs="?", type=str, const="", default=None)
    rap.add_argument("--shard_count", nargs="?", type=str, default=None)
    rap.add_argument("--intents", nargs="?", type=str, const="", default=None)
    rap.add_argument("--intent", nargs="*", type=str, default=None)
    rap.add_argument("--plugins", nargs="?", type=str, const="", default=None)
    rap.add_argument("--plugin", nargs="*", type=str, default=None)

    cap = ap.add_parser("config-dump")
    cap.add_argument("type", choices=["json", "yaml", "toml"])
    cap.add_argument("--token", nargs="?", type=str, default=None)
    cap.add_argument("--shard_id", nargs="*", type=str, default=None)
    cap.add_argument("--shard_ids", nargs="?", type=str, const="", default=None)
    cap.add_argument("--shard_count", nargs="?", type=str, default=None)
    cap.add_argument("--intents", nargs="?", type=str, const="", default=None)
    cap.add_argument("--intent", nargs="*", type=str, default=None)
    cap.add_argument("--plugins", nargs="?", type=str, const="", default=None)
    cap.add_argument("--plugin", nargs="*", type=str, default=None)

    np = ap.add_parser("new-plugin")
    np.add_argument("name")
    np.add_argument("commands", nargs="*", default=[])

    return p


async def main(args: Namespace, unknown: list[str]) -> None:
    """
    Main input point for our CLI.
    """

    if args.action == "run":
        config = client.Config.from_file(args.config)
        if "loglevel" in args:
            root = logging.Logger.root
            level = getattr(logging, args.loglevel.upper())
            root.setLevel(level)
        config.merge_namespace(args, unknown)
        bot = client.Client(config)
        await bot.run(sync=not args.no_sync)

    elif args.action == "config-dump":
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

    elif args.action == "new-plugin":
        plugin = textwrap.dedent("""
            import novus
            from novus.ext import client


            class {plugin}(client.Plugin):
        """).format(plugin=args.name).strip() + "\n"
        if not args.commands:
            plugin += " " * 4 + "...\n"
        for i in args.commands:
            command = textwrap.indent(textwrap.dedent("""
                @client.command(name="{name}")
                async def {name}(self, interaction: novus.types.CommandI) -> None:
                    ...
            """).strip(), " " * 4).format(name=i)
            plugin += "\n" + command + "\n"
        print(plugin)


class MaxLevelFilter(logging.Filter):
    """
    A filter that removes anything above a certain level.
    """

    def __init__(self, max_level: int):
        self.max_level = max_level

    def filter(self, record: logging.LogRecord):
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
    )
    args, unknown = get_parser().parse_known_args()
    try:
        asyncio.run(main(args, unknown))
    except KeyboardInterrupt:
        pass  # Silence, commandline


if __name__ == "__main__":
    main_sync()
