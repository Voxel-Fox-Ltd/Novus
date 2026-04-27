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


class DatabaseAcquireContext:

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.args = args
        self.kwargs = kwargs
        self._ctx: PoolAcquireContext | None = None

    async def __aenter__(self) -> asyncpg.Connection:
        try:
            await asyncio.wait_for(Database._pool_created.wait(), timeout=30)
        except asyncio.TimeoutError:
            raise Exception("Database pool was not created within 30 seconds")

        if Database.pool is None:
            raise Exception(
                (
                    "Database pool is not created - was the plugin loaded? "
                    "Was there a DSN provided?"
                )
            )

        self._ctx = Database.pool.acquire(*self.args, **self.kwargs)  # pyright: ignore
        assert self._ctx is not None, "Failed to acquire connection from pool"
        return await self._ctx.__aenter__()

    async def __aexit__(self, *args: Any) -> None:
        if self._ctx is not None:
            await self._ctx.__aexit__(*args)


class Database(client.Plugin):

    CONFIG = {
        "database_dsn": "",
        "database_max_connections": 10,
    }

    pool: asyncpg.Pool | None = None
    _log: logging.Logger = logging.getLogger("database")  # pyright: ignore
    _pool_created: asyncio.Event = asyncio.Event()

    @classmethod
    def acquire(cls, *args: Any, **kwargs: Any) -> DatabaseAcquireContext:
        return DatabaseAcquireContext(*args, **kwargs)

    async def create_pool(
            self,
            dsn: str,
            max_connections: int = 10,
            min_connections: int = 10) -> None:
        """
        Does the actual process of opening and storing a database pool.
        """

        # Open a pool
        try:
            created = (
                await asyncpg.create_pool(
                    dsn,
                    max_size=max_connections,
                    min_size=min(max_connections, min_connections),
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

    async def on_load(self) -> None:
        """
        Open a database connection, store it in the class, continue.
        """

        # Make sure we have a DSN
        if not hasattr(self.bot.config, "database_dsn"):
            self.log.error("Missing database DSN from config")
            return
        if not self.bot.config.database_dsn:
            self.log.error("Missing database DSN from config")
            return
        if self.bot.config.database_max_connections is None:
            self.bot.config.database_max_connections = 10

        # Create pool
        for _ in range(5):
            try:
                await self.create_pool(
                    self.bot.config.database_dsn,
                    self.bot.config.database_max_connections,
                    min(self.bot.config.database_max_connections, 10)
                )
            except Exception:
                self.log.error(
                    "Failed to create database pool, retrying in 5 seconds",
                    exc_info=True,
                )
                await asyncio.sleep(5)
            else:
                Database._pool_created.set()
                break
        else:
            Database._pool_created.set()
            raise Exception("Failed to create database pool after 5 attempts")

    async def create_tables(self) -> None:
        """
        Create any tables that have been instantiated with the database class.
        """

        # TODO
        pass
