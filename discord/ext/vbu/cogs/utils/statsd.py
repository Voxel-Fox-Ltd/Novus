import logging

import aiodogstatsd


def _fake_stats_collection_function(*args, **kwargs):
    pass


async def _fake_async_stats_collection_function(*args, **kwargs):
    pass


class _FakeContextManager(object):

    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self, *args, **kwargs):
        return self

    def __exit__(self, *args, **kwargs):
        pass

    async def __aenter__(self, *args, **kwargs):
        return self

    async def __aexit__(self, *args, **kwargs):
        pass


class _FakeStatsdConnection(object):

    def __init__(self):
        self.connect = _fake_async_stats_collection_function
        self.close = _fake_async_stats_collection_function

        self.increment = _fake_stats_collection_function
        self.decrement = _fake_stats_collection_function
        self.gauge = _fake_stats_collection_function
        self.histogram = _fake_stats_collection_function
        self.distribution = _fake_stats_collection_function
        self.timing = _fake_stats_collection_function

        self.timeit = _FakeContextManager


class StatsdConnection(object):
    """
    A helper class to wrap around an :class:`aiodogstatsd.Client` object so
    as to make it a little easier to use.
    Statsd is unique in my wrapper utils in that it'll fail
    silently if there's no connection to be made.
    """

    config: dict = None
    logger: logging.Logger = logging.getLogger("vbu.statsd")
    __slots__ = ('conn',)

    def __init__(self, connection: aiodogstatsd.Client = None):
        """:meta private:"""

        self.conn = connection

    @classmethod
    async def get_connection(cls) -> 'StatsdConnection':
        """
        Acquires a connection to the database from the pool.

        Returns:
            StatsdConnection: The connection that was aquired from the pool.
        """

        config = cls.config.copy()
        if not config.get("constant_tags", {}).get("service"):
            # cls.logger.debug("Creating fake Statsd connection")
            conn = _FakeStatsdConnection()
        else:
            # cls.logger.debug("Creating real Statsd connection")
            conn = aiodogstatsd.Client(**config)
        await conn.connect()
        return cls(conn)

    async def disconnect(self) -> None:
        """
        Releases a connection from the pool back to the mix.
        """

        await self.conn.close()
        self.conn = None
        del self

    async def __aenter__(self):
        v = await self.get_connection()
        self.conn = v.conn
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.disconnect()

    def increment(self, event, *args, **kwargs):
        return self.conn.increment(event, *args, **kwargs)

    def decrement(self, event, *args, **kwargs):
        return self.conn.decrement(event, *args, **kwargs)

    def gauge(self, event, *args, **kwargs):
        return self.conn.gauge(event, *args, **kwargs)

    def histogram(self, event, *args, **kwargs):
        return self.conn.histogram(event, *args, **kwargs)

    def distribution(self, event, *args, **kwargs):
        return self.conn.distribution(event, *args, **kwargs)

    def timing(self, event, *args, **kwargs):
        return self.conn.timing(event, *args, **kwargs)

    @property
    def timeit(self):
        return self.conn.timeit
