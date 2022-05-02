from __future__ import annotations

import typing

import asyncpg

from .types import DriverWrapper

if typing.TYPE_CHECKING:
    import asyncpg.pool
    import asyncpg.transaction
    from .types import UserDatabaseConfig, DatabaseConfig
    from .model import DatabaseWrapper, DatabaseTransaction

    class PostgresDatabaseWrapper(DatabaseWrapper):
        config: UserDatabaseConfig
        pool: asyncpg.pool.Pool
        conn: typing.Optional[asyncpg.Connection]
        cursor: None
        caller: asyncpg.Connection

    class PostgresDatabaseTransaction(DatabaseTransaction):
        parent: PostgresDatabaseWrapper
        _transaction: asyncpg.transaction.Transaction
        is_active: bool
        commit_on_exit: bool


class PostgresWrapper(DriverWrapper):

    @staticmethod
    async def create_pool(config: DatabaseConfig) -> asyncpg.pool.Pool:
        v = await asyncpg.create_pool(**config)
        assert v
        return v

    @staticmethod
    async def get_connection(dbw: typing.Type[PostgresDatabaseWrapper]) -> PostgresDatabaseWrapper:
        connection = await dbw.pool.acquire()
        v = dbw(
            conn=connection,
        )
        v.is_active = True
        return v

    @staticmethod
    async def release_connection(dbw: PostgresDatabaseWrapper) -> None:
        assert dbw.conn
        await dbw.pool.release(dbw.conn)
        dbw.conn = None
        dbw.is_active = False

    @classmethod
    async def start_transaction(cls, tra: PostgresDatabaseTransaction):
        assert tra.parent.conn
        transaction = tra.parent.conn.transaction()
        tra._transaction = transaction
        await transaction.start()

    @staticmethod
    async def commit_transaction(tra: PostgresDatabaseTransaction) -> None:
        await tra._transaction.commit()

    @staticmethod
    async def rollback_transaction(tra: PostgresDatabaseTransaction) -> None:
        await tra._transaction.rollback()

    @staticmethod
    async def fetch(dbw: PostgresDatabaseWrapper, sql: str, *args) -> typing.List[typing.Any]:
        assert dbw.conn
        x = None
        if 'select' in sql.casefold() or 'returning' in sql.casefold():
            x = await dbw.caller.fetch(sql, *args)
        else:
            await dbw.caller.execute(sql, *args)
        return x or list()

    @staticmethod
    async def executemany(dbw: PostgresDatabaseWrapper, sql: str, *args_list) -> None:
        assert dbw.conn
        await dbw.caller.executemany(sql, args_list)

    def prepare(self) -> typing.Generator[str, None, None]:
        start = 1
        while True:
            yield f"${start}"
            start += 1
