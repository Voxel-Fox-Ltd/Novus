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
from typing import TYPE_CHECKING, Any, Type

import novus

if TYPE_CHECKING:
    from .config import Config
    from .plugins import Plugin

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
        self.state = novus.api.HTTPConnection(self.config.token)
        self.state.dispatch = self.dispatch
        self.plugins: set[Plugin] = set()

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

        log.info(f"Loading {len(self.plugins)}")
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

        for p in self.plugins:
            p.dispatch(event_name, *args, **kwargs)

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

    async def run(self) -> None:
        """
        Connect the bot to the gateway, keeping the bot's connection to the
        websocket alive.
        """

        log.info("Running client")
        await self.load_plugins()
        await self.connect()
        while True:
            try:
                await asyncio.sleep(0)
            except asyncio.CancelledError:
                break
        await self.close()
