from __future__ import annotations

import logging
import typing

if typing.TYPE_CHECKING:
    from .types import (
        UserDatabaseConfig, DatabaseConfig, DriverWrapper,
        DriverPool, DriverConnection,
    )


class DatabaseTransaction(object):
    """
    A wrapper around a transaction for your database.

    Parameters
    -----------
    commit_on_exit: :class:`bool`
        Whether or not your changes should be automatically committed when the
        transaction context is left.

    Attributes
    -----------
    parent: :class:`DatabaseWrapper`
        The connection that spawned this transaction.
    """

    def __init__(self, driver: typing.Type[DriverWrapper], parent: DatabaseWrapper, *, commit_on_exit: bool = True):
        """:meta private:"""
        self._driver = driver
        self.parent = parent
        self._transaction = None
        self.is_active: bool = False
        self.commit_on_exit = commit_on_exit

    async def __aenter__(self) -> DatabaseTransaction:
        await self._driver.start_transaction(self)
        self.is_active = True
        return self

    async def __aexit__(self, *args):
        if not self.is_active:
            return
        if any(args):
            await self.rollback()  # Rollback errors
        elif self.commit_on_exit:
            await self.commit()  # Commit on exit
        else:
            await self.rollback()  # Not committed and exited the transaction

    async def __call__(self, *args, **kwargs):
        return await self.call(*args, *kwargs)

    async def call(self, *args, **kwargs):
        """
        Run some SQL, returning it's data. See :func:`DatabaseWrapper.call`.
        """

        return await self.parent.call(*args, **kwargs)

    async def execute_many(self, *args, **kwargs):
        """
        Run some SQL, returning it's data. See :func:`DatabaseWrapper.execute_many`.
        """

        return await self.parent.execute_many(*args, **kwargs)

    async def commit(self):
        """
        Commit the changes made to the database in this transaction context.
        """

        await self._driver.commit_transaction(self)
        self.is_active = False

    async def rollback(self):
        """
        Roll back the changes made to the database in this transaction context.
        """

        await self._driver.rollback_transaction(self)
        self.is_active = False


class DatabaseWrapper(object):
    """
    A wrapper around your preferred database driver.
    """

    __slots__ = ("conn", "is_active", "cursor",)

    config: typing.ClassVar[DatabaseConfig] = None  # type: ignore
    pool: typing.ClassVar[DriverPool] = None  # type: ignore
    logger: logging.Logger = logging.getLogger("vbu.database")
    enabled: typing.ClassVar[bool] = False
    driver: typing.ClassVar[typing.Type[DriverWrapper]] = None  # type: ignore

    def __init__(
            self,
            conn=None,
            *,
            cursor: DriverConnection = None):
        """:meta private:"""

        self.conn = conn
        self.cursor = cursor
        self.is_active = False

    @property
    def caller(self) -> DriverConnection:
        v = self.cursor or self.conn
        assert v
        return v

    @classmethod
    async def create_pool(cls, config: UserDatabaseConfig) -> None:
        """
        Create the database pool and store its instance in :attr:`pool`.

        Parameters
        ----------
        config: :class:`dict`
            The config that the pool should be created with.
        """

        # Grab the args that are valid
        config_args = ("host", "port", "database", "user", "password",)
        stripped_config: DatabaseConfig = {i: o for i, o in config.items() if i in config_args}  # type: ignore
        cls.config = stripped_config

        # See if we want to even enable the database
        if not config.get("enabled", True):
            raise RuntimeError("Database is not enabled in your config")

        # Check which driver we want to use
        database_type = config.get("type", "postgres").lower()
        if database_type in ["postgres", "postgresql", "psql"]:
            from .postgres import PostgresWrapper as Driver
        elif database_type == "mysql":
            from .mysql import MysqlWrapper as Driver
        elif database_type == "sqlite":
            from .sqlite_ import SQLiteWrapper as Driver
        else:
            raise RuntimeError("Invalid database type passed")
        cls.driver = Driver


        # Start and store our pool
        created = await cls.driver.create_pool(stripped_config)
        cls.pool = created
        cls.enabled = True

    @classmethod
    async def get_connection(cls) -> DatabaseWrapper:
        """
        Acquires a connection to the database from the pool.

        Using this method does not automatically call the ``.disconnect()`` method - if you
        want this to be handled automaticall you can use this class in a context manager.

        Examples
        ---------
        >>> db = await vbu.Database.get_connection()
        >>> rows = await db("SELECT 1")
        >>> await db.disconnect()

        Returns
        --------
        :class:`DatabaseWrapper`
            The connection that was aquired from the pool.
        """

        assert cls.driver, "No driver has been established"
        return await cls.driver.get_connection(cls)

    async def disconnect(self) -> None:
        """
        Releases a connection from the pool back to the mix. This should be called
        after you're done with a database connection.
        """

        if self.conn is None:
            return
        await self.driver.release_connection(self)

    async def __aenter__(self) -> DatabaseWrapper:
        """
        Get a connection from your database and close it automatically when you're done.

        Examples
        ---------
        >>> async with vbu.Database() as db:
        >>>     rows = await db("SELECT 1")
        """

        new_connection = await self.get_connection()
        for i in self.__slots__:
            setattr(self, i, getattr(new_connection, i))
        return self

    async def __aexit__(self, *_) -> None:
        return await self.disconnect()

    def transaction(self, *args, **kwargs) -> DatabaseTransaction:
        """
        Start a database transaction.

        Parameters
        ----------
        commit_on_exit: :class:`bool`
            Whether or not you want to commit automatically when you exit the
            context manager.
            Defaults to ``True``.

        Examples
        ---------
        >>> # This will commit automatically on exit
        >>> async with db.transaction() as transaction:
        >>>     await transaction("DROP TABLE example")

        >>> # This needs to be committed manually
        >>> async with db.transaction(commit_on_exit=False) as transaction:
        >>>     await transaction("DROP TABLE example")
        >>>     await transaction.commit()

        >>> # You can rollback a transaction with `.rollback()`
        >>> async with db.transaction() as transaction:
        >>>     await transaction("DROP TABLE example")
        >>>     await transaction.rollback()

        >>> # Rollbacks will happen automatically if any error is hit in the
        >>> # transaction context
        >>> async with db.transaction() as transaction:
        >>>     await transaction("DROP TABLE example")
        >>>     raise Exception()

        >>> # If you have `commit_on_exit` set to `False` and you don't commit then
        >>> # your changes will be automatically rolled back on exiting the context
        >>> async with db.transaction(commit_on_exit=False) as transaction:
        >>>     await transaction("DROP TABLE example")

        Returns
        -------
        :class:`DatabaseTransaction`
            A handler for your transaction instance.
        """

        assert self.conn, "No connection has been established"
        return self.driver.transaction(self, *args, **kwargs)

    async def __call__(self, sql: str, *args) -> typing.List[typing.Any]:
        return await self.call(sql, *args)

    async def call(self, sql: str, *args) -> typing.List[typing.Any]:
        """
        Run a line of SQL against your database driver.

        This method can also be run as ``__call__``.

        Parameters
        ----------
        sql: :class:`str`
            The SQL that you want to run. This will be parsed as a prepared or parameterized statement.
            For PostgreSQL, arguments will be in form ``$1`` numbered for each of your arguments;
            in SQLite they'll be ``?`` and inserted in the order of your given arguments; and
            in MySQL they'll be in format ``%s`` and inserted in the order of your given
            arguments.
        *args: typing.Any
            The arguments that are passed to your database call.

        Examples
        ---------
        >>> sql = "INSERT INTO example (a, b) VALUES ($1, $2)"
        >>> await db.executemany(sql, 1, 2)

        Returns
        --------
        typing.List[:class:`dict`]
            The list of rows that were returned from the database.
        """

        assert self.conn, "No connection has been established"
        self.logger.debug(f"Running SQL: {sql} {args!s}")
        return await self.driver.fetch(self, sql, *args)

    async def executemany(self, sql: str, *args_list: typing.Iterable[typing.Any]) -> None:
        """
        Run a line of SQL with a multitude of arguments.

        Parameters
        ----------
        sql: :class:`str`
            The SQL that you want to run. This will be parsed as a prepared or parameterized statement.
            For PostgreSQL, arguments will be in form ``$1`` numbered for each of your arguments;
            in SQLite they'll be ``?`` and inserted in the order of your given arguments; and
            in MySQL they'll be in format ``%s`` and inserted in the order of your given
            arguments.
        *args_list: typing.Iterable[typing.Any]
            A list of arguments that should be passed into your database call.

        Examples
        ---------
        >>> sql = "INSERT INTO example (a, b) VALUES ($1, $2)"
        >>> await db.executemany(sql, (1, 2), (3, 4), (5, 6), (7, 8))

        Returns
        --------
        typing.List[:class:`dict`]
            The list of rows that were returned from the database.
        """

        assert self.conn, "No connection has been established"
        self.logger.debug(f"Running SQL: {sql} {args_list!s}")
        return await self.driver.executemany(self, sql, *args_list)

    async def execute_many(self, sql: str, *args) -> None:
        """:meta private:"""
        return await self.executemany(sql, *args)
