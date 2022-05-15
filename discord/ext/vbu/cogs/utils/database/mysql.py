from __future__ import annotations

import typing

import aiomysql

from .types import DriverWrapper

if typing.TYPE_CHECKING:
    from .types import UserDatabaseConfig, DatabaseConfig
    from .model import DatabaseWrapper, DatabaseTransaction

    class MysqlDatabaseWrapper(DatabaseWrapper):
        config: UserDatabaseConfig
        pool: aiomysql.pool.Pool
        conn: typing.Optional[aiomysql.Connection]
        cursor: aiomysql.Cursor
        caller: aiomysql.Cursor

    class MysqlDatabaseTransaction(DatabaseTransaction):
        parent: MysqlDatabaseWrapper
        _transaction: None
        is_active: bool
        commit_on_exit: bool


class MysqlWrapper(DriverWrapper):

    @staticmethod
    async def create_pool(config: DatabaseConfig) -> aiomysql.Pool:
        return await aiomysql.create_pool(**config, autocommit=True)

    @staticmethod
    async def get_connection(dbw: typing.Type[MysqlDatabaseWrapper]) -> MysqlDatabaseWrapper:
        connection: aiomysql.Connection = await dbw.pool.acquire()
        cursor = await connection.cursor(aiomysql.DictCursor)
        v = dbw(
            conn=connection,
            cursor=cursor,
        )
        v.is_active = True
        return v

    @staticmethod
    async def release_connection(dbw: MysqlDatabaseWrapper) -> None:
        assert dbw.conn
        assert dbw.cursor
        await dbw.cursor.close()
        await dbw.pool.release(dbw.conn)
        dbw.conn = None
        dbw.is_active = False

    @classmethod
    async def start_transaction(cls, tra: MysqlDatabaseTransaction):
        assert tra.parent.conn
        await tra.parent.conn.begin()

    @staticmethod
    async def commit_transaction(tra: MysqlDatabaseTransaction) -> None:
        assert tra.parent.conn
        await tra.parent.conn.commit()

    @staticmethod
    async def rollback_transaction(tra: MysqlDatabaseTransaction) -> None:
        assert tra.parent.conn
        await tra.parent.conn.rollback()

    @staticmethod
    async def fetch(dbw: MysqlDatabaseWrapper, sql: str, *args) -> typing.List[typing.Any]:
        await dbw.caller.execute(sql, args)
        data = await dbw.caller.fetchall()
        return data or list()

    @staticmethod
    async def executemany(dbw: MysqlDatabaseWrapper, sql: str, *args_list) -> None:
        assert dbw.conn
        await dbw.caller.executemany(sql, args_list)

    def prepare(self) -> typing.Generator[str, None, None]:
        while True:
            yield "%s"
