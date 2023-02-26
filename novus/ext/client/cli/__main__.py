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

import asyncio
import logging
import textwrap
from argparse import ArgumentParser, Namespace

from novus.ext import client


def get_parser() -> ArgumentParser:
    p = ArgumentParser("novus")

    ap = p.add_subparsers(dest="action", required=True)

    rap = ap.add_parser("run")
    rap.add_argument("config", nargs="?")
    logger_choices = []
    for i in ["debug", "info", "warning", "error"]:
        logger_choices.extend((i, i.upper(),))
    rap.add_argument("--loglevel", default='info', choices=logger_choices)
    rap.add_argument("--sync", default=False, action="store_true")
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

    np = ap.add_parser("new-plugin")
    np.add_argument("name")
    np.add_argument("commands", nargs="*", default=[])

    return p


async def main(args: Namespace) -> None:
    """
    Main input point for our CLI.
    """

    if args.action == "run":
        config = client.Config.from_file(args.config)
        if "loglevel" in args:
            root = logging.Logger.root
            root.setLevel(getattr(logging, args.loglevel.upper()))
        config.merge_namespace(args)
        bot = client.Client(config)
        await bot.run(sync=args.sync)

    elif args.action == "config-dump":
        config = client.Config()
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
            plugin += " " * 8 + "...\n"
        for i in args.commands:
            command = textwrap.indent(textwrap.dedent("""
                @client.command(name="{name}")
                async def {name}(self, interaction: novus.Interaction[novus.ApplicationCommandData]) -> None:
                    ...
            """).strip(), " " * 8).format(name=i)
            plugin += "\n" + command + "\n"
        print(plugin)


def main_sync() -> None:
    logging.basicConfig(level=logging.INFO)
    args = get_parser().parse_args()
    asyncio.run(main(args))


if __name__ == "__main__":
    main_sync()
