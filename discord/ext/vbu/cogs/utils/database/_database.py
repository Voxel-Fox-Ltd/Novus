from __future__ import annotations

import logging
import typing

import asyncpg

if typing.TYPE_CHECKING:
    import asyncpg.pool
    import asyncpg.transaction


class DatabaseConnection(object):
    """
    A helper class to wrap around an :class:`asyncpg.Connection` object. This class is
    written so you don't need to interface with asyncpg directly (though you can if you
    want by using the :attr:`conn` attribute).

    Examples
    --------
    >>> # The database can be used via context
    >>> async with DatabaseConnection() as db:
    >>>     values = await db("SELECT user_id FROM user_settings WHERE enabled=$1", True)
    >>> for row in values:
    >>>     print(row['user_id'])
    >>>
    >>> # Or you can get a connection object that you can pass around
    >>> db = await DatabaseConnection.get_connection()
    >>> await db("DELETE FROM user_settings")
    >>> await db.disconnect()
    >>>
    >>> # And transactions are also available
    >>> async with DatabaseConnection() as db:
    >>>     await db.start_transaction()
    >>>     await db("DELETE FROM guild_settings")
    >>>     await db.commit_transaction()

    Attributes
    -----------
    conn: :class:`asyncpg.Connection`
        The asyncpg connection object that we use internally.
    enabled: :class:`bool`
        Whether the database system is enabled or not.
    """

    config: dict = None  # type: ignore
    pool: asyncpg.pool.Pool = None  # type: ignore
    logger: logging.Logger = logging.getLogger("vbu.database")
    enabled: bool = False
    __slots__ = ('conn', 'transaction', 'is_active',)

    def __init__(
            self, connection: asyncpg.Connection = None,
            transaction: asyncpg.transaction.Transaction = None):
        self.conn: typing.Optional[asyncpg.Connection] = connection
        self.transaction: typing.Optional[asyncpg.transaction.Transaction] = transaction
        self.is_active: bool = False

    @classmethod
    async def create_pool(cls, config: dict) -> None:
        """
        Creates the database pool and plonks it in :attr:`DatabaseConnection.pool`.

        Args:
            config (dict): The configuration for the dictionary, passed directly to
                :func:`asyncpg.create_pool` as kwargs.
        """

        # Grab the config
        cls.config = config.copy()
        modified_config = config.copy()

        # See if we even want to create a pool
        if modified_config.pop('enabled') is False:
            cls.logger.critical("Database create pool method is being run when the database is disabled")
            exit(1)

        # Create pool
        created = await asyncpg.create_pool(**modified_config)
        assert created, "Could not create pool"
        cls.pool = created
        cls.enabled = True

    @classmethod
    async def get_connection(cls) -> DatabaseConnection:
        """
        Acquires a connection to the database from the pool.

        Returns:
            DatabaseConnection: The connection that was aquired from the pool.
        """

        try:
            conn: asyncpg.Connection = await cls.pool.acquire()
        except AttributeError:
            raise Exception("Could not open a database connection as the database is disabled in your config.")
        v = cls(conn)
        v.is_active = True
        return v

    async def disconnect(self) -> None:
        """
        Releases a connection from the pool back to the mix.
        """

        await self.pool.release(self.conn)
        self.conn = None
        self.is_active = False
        del self

    async def start_transaction(self) -> None:
        """
        Creates a database object for a transaction.
        """

        assert self.conn, "No connection has been established"
        assert self.is_active, "Database connection is not active"

        self.transaction = self.conn.transaction()
        await self.transaction.start()

    async def commit_transaction(self) -> None:
        """
        Commits the current transaction.
        """

        if self.transaction is None:
            raise RuntimeError("No transaction has been established")
        assert self.is_active, "Database connection is not active"
        await self.transaction.commit()
        self.transaction = None

    async def __aenter__(self) -> DatabaseConnection:
        assert not self.is_active, "Can't open a new database connection while currently connected."
        v = await self.get_connection()
        self.conn = v.conn
        self.is_active = True
        return self

    async def __aexit__(self, *_) -> None:
        await self.disconnect()

    async def __call__(self, sql: str, *args) -> typing.List[typing.Any]:
        """
        Runs a line of SQL and returns a list, if things are expected back, or None, if nothing of interest is happening.

        Args:
            sql (str): The SQL that you want to run.
            *args: The args that are passed to the SQL, in order.

        Returns:
            typing.Union[typing.List[dict], None]: The list of rows that were returned from the database.
        """

        if self.conn is None:
            raise RuntimeError("No connection has been established")

        # Check we don't want to describe the table
        if sql.casefold().startswith("describe table "):
            table_name = sql[len("describe table "):].strip("; ")
            return await self.__call__(
                """SELECT column_name, column_default, is_nullable, data_type, character_maximum_length
                FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name=$1""",
                table_name,
            )

        # Runs the SQL
        self.logger.debug(f"Running SQL: {sql} {args!s}")
        if 'select' in sql.casefold() or 'returning' in sql.casefold():
            x = await self.conn.fetch(sql, *args)
        else:
            await self.conn.execute(sql, *args)
            return []

        # If it got something, return the dict, else None
        if x:
            return x
        return []

    async def execute_many(self, sql: str, *args) -> None:
        """
        Runs an executemany query.

        Args:
            sql (str): The SQL that you want to run.
            *args: A list of tuples of arguments to sent to the database.
        """

        if self.conn is None:
            raise RuntimeError("No connection has been established")
        self.logger.debug(f"Running SQL: {sql} {args!s}")
        await self.conn.executemany(sql, args)
        return None

    async def copy_records_to_table(
            self, table_name: str, *, records: typing.List[typing.Any],
            columns: typing.Tuple[str] = None, timeout: float = None) -> str:
        """
        Copies a series of records to a given table.

        Args:
            table_name (str): The name of the table you want to copy to.
            records (typing.List[typing.Any]): The list of records you want to input to the database.
            columns (typing.Tuple[str], optional): The columns (in order) that you want to insert to.
            timeout (float, optional): The timeout for the copy command.

        Returns:
            str: The COPY status string.
        """

        if self.conn is None:
            raise RuntimeError("No connection has been established")
        return await self.conn.copy_records_to_table(
            table_name=table_name, records=records,
            columns=columns, timeout=timeout
        )
