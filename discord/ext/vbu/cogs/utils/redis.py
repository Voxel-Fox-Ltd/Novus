from __future__ import annotations

import logging
import typing
import asyncio
import json

import aioredis


class RedisConnection(object):
    """
    A wrapper for an :class:`aioredis.Redis` object, provided in your bot object
    at :attr:`Bot.redis` for your convenience. Implemented are setter and getter methods
    for the redis database, as well as publish and subscribe via a decorator.

    Examples:

        ::

            # In a command
            async with RedisConnection() as re:
                await re.publish("channel_name", {"foo": "bar"})
                await re.publish_str("channel_two", "baz")

            # In a cog
            @voxelbotutils.redis_channel_handler("channel_name")
            async def handler(self, payload):
                self.logger.info(payload)
    """

    config: dict = None
    pool: aioredis.Redis = None
    logger: logging.Logger = logging.getLogger("vbu.redis")
    lock_manager = None
    enabled: bool = False

    def __init__(self, connection: typing.Optional[aioredis.RedisConnection] = None):
        """:meta private:"""

        self.conn = connection

    @classmethod
    async def create_pool(cls, config: dict) -> None:
        """
        Creates and connects the pool object.

        Args:
            config (dict): The config dictionary that should be passed directly to :func:`aioredis.create_redis_pool` directly as kwargs.
        """

        cls.config = config.copy()
        modified_config = config.copy()
        modified_config.pop('shard_manager_enabled', False)  # No longer present, here from old configs
        if modified_config.pop('enabled', True) is False:
            raise NotImplementedError("The Redis connection has been disabled.")
        address = modified_config.pop('host'), modified_config.pop('port')
        cls.pool = await aioredis.create_redis_pool(address, **modified_config)
        cls.enabled = True

    @classmethod
    async def get_connection(cls) -> RedisConnection:
        """
        Acquires a connection from the connection pool.
        """

        conn = cls.pool
        return cls(conn)

    @classmethod
    def _get_connection(cls):
        """
        Acquires a connection from the connection pool.
        """

        conn = cls.pool
        return cls(conn)

    async def disconnect(self) -> None:
        """
        Releases a connection back into the connection pool.
        """

        del self

    async def __aenter__(self):
        v = await self.get_connection()
        self.conn = v.conn
        return self

    async def __aexit__(self, *args, **kwargs):
        await self.disconnect()

    async def publish(self, channel: str, json: dict) -> None:
        """
        Publishes some JSON to a given redis channel.

        Args:
            channel (str): The name of the channel that you want to publish redis to.
            json (dict): The JSON that you want to publish.
        """

        self.logger.debug(f"Publishing JSON to channel {channel}: {json!s}")
        return await self.conn.publish_json(channel, json)

    async def publish_str(self, channel: str, message: str) -> None:
        """
        Publishes a message to a given redis channel.

        Args:
            channel (str): The name of the channel that you want to publish redis to.
            message (str): The message that you want to publish.
        """

        self.logger.debug(f"Publishing message to channel {channel}: {message}")
        return await self.conn.publish(channel, message)

    async def set(self, key: str, value: str) -> None:
        """
        Sets a key/value pair in the redis DB.

        Args:
            key (str): The key you want to set the value of
            value (str): The data you want to set the key to
        """

        self.logger.debug(f"Setting Redis key:value pair with {key}:{value}")
        return await self.conn.set(key, value)

    async def get(self, key: str) -> str:
        """
        Gets a value from the Redis DB given a key.

        Args:
            key (str): The key that you want to get from the Redis database.

        Returns:
            str: The key from the database.
        """

        v = await self.conn.get(key)
        self.logger.debug(f"Getting Redis from key with {key}")
        if v:
            return v.decode()
        return v

    async def mget(self, *keys) -> typing.List[str]:
        """
        Gets multiple values from the Redis DB given a list of keys.

        Args:
            keys (str): The keys that you want to get from the database.

        Returns:
            typing.List[str]: The values from the Redis database associated with the given keys.
        """

        if not keys:
            return []
        v = await self.conn.mget(keys)
        self.logger.debug(f"Getting Redis from keys with {keys}")
        if v:
            return [i.decode() for i in v]
        return v


class RedisChannelHandler(object):
    """
    A channel handler wrapper for a function, meant for cogs to run a task in the background when added to cogs.
    """

    connection = RedisConnection

    def __init__(self, channel_name, callback):
        self.channel_name = channel_name
        self.channels = None
        self.callback = callback
        self.cog = None
        self.task = None

    def start(self):
        """
        Start the Redis channel handler.
        """

        self.task = asyncio.get_event_loop().create_task(self.channel_handler())

    def cancel(self):
        """
        Cancel the running task.
        """

        self.task.cancel()

    def stop(self):
        """
        Stop the running task.
        """

        asyncio.get_event_loop().run_until_complete(self.unsubscribe())

    async def channel_handler(self):
        """
        General handler for creating a channel, waiting for an input, and then plugging the
        data into a function.
        """

        # Subscribe to the given channel
        async with self.connection() as re:
            self.connection.logger.info(f"Subscribing to Redis channel {self.channel_name}")
            channel_list = await re.conn.subscribe(self.channel_name)

        # Get the channel from the list, loop it forever
        channel = channel_list[0]
        self.connection.logger.info(f"Looping to wait for messages to Redis channel {self.channel_name}")
        while (await channel.wait_message()):
            data = await channel.get_json()
            self.connection.logger.debug(f"Received JSON at channel {self.channel_name}:{json.dumps(data)}")
            try:
                if asyncio.iscoroutine(self.callback) or asyncio.iscoroutinefunction(self.callback):
                    asyncio.create_task(self.callback(self.cog, data))
                else:
                    self.callback(self.cog, data)
            except Exception as e:
                self.connection.logger.error("Failed to run channel task", exc_info=True)

    async def unsubscribe(self):
        """
        Unsubscribe from the channel that this instance refers to.
        """

        self.connection.logger.info(f"Unsubscribing from Redis channel {self.channel_name}")
        await self.connection.pool.unsubscribe(self.channel_name)


def redis_channel_handler(channel_name):
    def wrapper(func):
        return RedisChannelHandler(channel_name, func)
    return wrapper
