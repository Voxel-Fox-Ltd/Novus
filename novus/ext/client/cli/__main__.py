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
from argparse import ArgumentParser, Namespace

from novus.ext import client


def get_parser() -> ArgumentParser:
    p = ArgumentParser("novus")

    ap = p.add_subparsers(dest="action", required=True)

    rap = ap.add_parser("run")
    rap.add_argument("config", nargs="?")

    cap = ap.add_parser("config-dump")
    cap.add_argument("type", choices=["json", "yaml", "toml"])

    return p


async def main(args: Namespace) -> None:
    """
    Main input point for our CLI.
    """

    if args.action == "run":
        config = client.Config.from_file(args.config)
        bot = client.Client(config)
        await bot.run()

    elif args.action == "config-dump":
        config = client.Config()
        match args.type:
            case "yaml":
                print(config.to_yaml())
            case "json":
                print(config.to_json())
            case "toml":
                print(config.to_toml())


def main_sync() -> None:
    logging.basicConfig(level=logging.INFO)
    args = get_parser().parse_args()
    asyncio.run(main(args))


if __name__ == "__main__":
    main_sync()
