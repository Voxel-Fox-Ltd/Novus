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

import logging
from typing import TYPE_CHECKING, Any

import asyncpg

from novus.ext import client

if TYPE_CHECKING:
    class PoolAcquireContext:

        async def __aenter__(self) -> asyncpg.Connection:
            ...

        async def __aexit__(self, *args: Any) -> None:
            ...

__all__ = (
    "Database",
)


class Database(client.Plugin):

    CONFIG = {
        "database_dsn": "",
        "database_max_connections": 10,
    }
    pool: asyncpg.Pool = None  # pyright: ignore
    _log: logging.Logger = logging.getLogger("database")  # pyright: ignore

    @classmethod
    def acquire(cls, *args: Any, **kwargs: Any) -> PoolAcquireContext:
        if cls.pool is None:
            raise Exception(
                (
                    "Database pool is not created - was the plugin loaded? "
                    "Was there a DSN provided?"
                )
            )
        return cls.pool.acquire(*args, **kwargs)  # pyright: ignore

    async def on_load(self) -> None:
        """
        Open a database connection, store it in the class, continue.
        """

        # Make sure we have a DSN
        Database._log = self.log
        if not hasattr(self.bot.config, "database_dsn"):
            self.log.error("Missing database DSN from config")
            return
        if not self.bot.config.database_dsn:
            self.log.error("Missing database DSN from config")
            return
        if self.bot.config.database_max_connections is None:
            self.bot.config.database_max_connections = 10

        # Open a pool
        try:
            created = (
                await asyncpg.create_pool(
                    self.bot.config.database_dsn,
                    max_size=self.bot.config.database_max_connections,
                    min_size=min(self.bot.config.database_max_connections, 10),
                )
            )
            if created is None:
                raise AssertionError()
            Database.pool = created
            self.log.info("Created database pool")

        # Fail to open pool
        except Exception as e:
            self.log.error("Failed to create database pool", exc_info=e)
            raise

        # Create relevant tables
        else:
            await self.create_tables()

    async def create_tables(self) -> None:
        """
        Create any tables that have been instantiated with the database class.
        """

        # TODO
        pass
