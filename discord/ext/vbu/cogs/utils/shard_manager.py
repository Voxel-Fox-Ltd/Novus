import typing
import asyncio
import aiohttp
import enum
import logging
import time
import json
from datetime import datetime as dt, timedelta


logger = logging.getLogger("vbu.sharder")


class ShardConnectTimer(object):
    """
    A class to keep track of how long a given shard takes to connect.
    """

    def __init__(self):
        self.start_time = time.perf_counter()

    def get_elapsed_time(self) -> float:
        return time.perf_counter() - self.start_time


class ShardManagerOpCodes(enum.Enum):
    """
    The opcodes that each shard connection wants to send/receive.
    """

    REQUEST_CONNECT = "REQUEST_CONNECT"  #: A bot asking to connect
    CONNECT_READY = "CONNECT_READY"  #: The manager saying that a given shard is allowed to connect
    CONNECT_COMPLETE = "CONNECT_COMPLETE"  #: A bot saying that a shard is done connecting
    PING = "PING"  #: A shard ping


class ShardManagerServer(object):
    """
    A small shard manager which handles launching a maximum amount of shards simultaneously.
    """

    def __init__(self, host: str, port: int, max_concurrency: int = 1):
        """
        Args:
            max_concurrency (int, optional): The maximum amount of shards allowed to be connecting simultaneously
        """

        # General
        self.host = host
        self.port = port
        self.lock = asyncio.Lock()
        self.loop = asyncio.get_event_loop()
        self.queue_handler_task = None
        self.shard_keepalive_handler_task = None

        # Things used by the manager
        self.max_concurrency: int = max_concurrency  #: The maximum number of shards that can connect concurrently.
        self.server: asyncio.Server = None  #: The shard manager TCP server.

        # Manager keeping track of shards
        self.shards_connecting: typing.List[int] = []  #: The IDs of the shards that are currently connecting.
        self.shard_queue = asyncio.PriorityQueue()  #: The IDs of the shards that are waiting to connect.
        self.shards_in_queue: typing.List[int] = []  #: A list of shard IDs that are in the queue because apparently I can't do that lookup.
        self.shard_wait_timers = {}  #: Timer objects to see how long a shard sits in the queue.
        self.shard_connect_timers = {}  #: Timer objects to see how long a shard takes to connect.
        self.shard_stream_writers = {}  #: A dictionary containing all of the shards being handled by the server.
        self.shard_identify_timestamps = []  #: A list of timestamps (within the last 5 seconds - the IDENFITY rate limit) that a shard tried to connect. Should only ever be :attr:`max_concurrency` sized or less.

    @staticmethod
    async def get_max_concurrency(token: str) -> int:
        """
        Ask Discord for the max concurrency of a bot given its token.

        Args:
            token (string): The token of the bot to request the maximum concurrency for

        Returns:
            int: The maximum concurrency for the given bot.
        """

        url = "https://discord.com/api/v9/gateway/bot"
        headers = {
            "Authorization": f"Bot {token}",
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as r:
                    data = await r.json()
            logger.debug(data)
            return data['session_start_limit']['max_concurrency']
        except Exception:
            logger.critical("Failed to get session start limit")
            raise

    async def run(self):
        """
        Connect and run the main event loop for the shard manager.
        """

        # Start the TCP server
        self.server = await asyncio.start_server(self.connection_handler, host=self.host, port=self.port)
        logger.info('Waiting for connections')
        self.queue_handler_task = self.loop.create_task(self.shard_queue_handler())
        self.shard_keepalive_handler_task = self.loop.create_task(self.shard_keepalive_handler())

    async def connection_handler(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """
        Handle an asyncio socket connection.
        """

        # Loop until buffer is empty and EOF is received
        logger.info(f"New connection at {writer.transport}")
        while not reader.at_eof():
            try:
                raw_data = await reader.readline()
            except asyncio.IncompleteReadError:
                return
            if not raw_data:
                continue
            try:
                data = json.loads(raw_data.decode())
            except Exception:
                logger.debug("Error reading line")
                continue
            logger.debug(f'Recieved message - {data}')

            # Make sure the data is valid
            if "op" not in data:
                logger.warning(f'Message is missing opcode or shard ID - {data}')
                continue

            # See if we need to update our stream writer cache
            if "shard" in data:
                self.shard_stream_writers[data.get("shard")] = writer

            # See which opcode we got
            opcode = data.get('op')
            if opcode == ShardManagerOpCodes.REQUEST_CONNECT.value:
                await self.shard_request(data.get('shard'), data.get('priority', False))
                continue
            elif opcode == ShardManagerOpCodes.CONNECT_COMPLETE.value:
                await self.shard_connected(data.get('shard'))
                continue

            # Invalid opcode
            else:
                logger.warning(f'Message with invalid opcode received - {data}')
                continue

    async def tell_shard(self, shard_id: int, data: dict):
        writer = self.shard_stream_writers[shard_id]
        writer.write(json.dumps(data).encode() + b"\n")
        await writer.drain()

    @property
    def max_concurrency_reached(self):
        return len(self.shards_connecting) >= self.max_concurrency

    @property
    def shard_in_waitlist(self):
        return not self.shard_queue.empty()

    @property
    def identify_ratelimit_hit(self):
        for i in self.shard_identify_timestamps:
            if i < (dt.utcnow() - timedelta(seconds=5.5)):
                self.shard_identify_timestamps.remove(i)
        return len(self.shard_identify_timestamps) >= self.max_concurrency

    async def shard_keepalive_handler(self):
        """
        Handles sending keepalives to each of the shards.
        """

        while True:

            # Set up a list of shards that we couldn't connect to
            ids_to_remove = list()

            # Ping each connected shard
            for shard_id, writer in self.shard_stream_writers.items():
                try:
                    logger.info(f"Sending ping to shard ID {shard_id}")
                    await self.tell_shard(shard_id, {"op": ShardManagerOpCodes.PING.value, "shard_id": shard_id})
                except Exception as e:
                    logger.info(f"Shard ID {shard_id} couldn't be sent our ping, removing from the list of connectable shards - {e}")
                    logger.debug(e, exc_info=True)
                    ids_to_remove.append(shard_id)

            # Remove unreachable shards
            for i in ids_to_remove:
                self.shard_stream_writers.pop(i, None)
                try:
                    self.shards_connecting.remove(i)
                except ValueError:
                    pass
                try:
                    self.shards_in_queue.remove(i)
                except ValueError:
                    pass

            # And sleep
            await asyncio.sleep(15)

    async def shard_queue_handler(self):
        """
        Moves waiting shards to connecting if there's enough room available.
        """

        while True:
            while self.shard_in_waitlist and not self.max_concurrency_reached and not self.identify_ratelimit_hit:
                _, shard_id = await self.shard_queue.get()
                if shard_id not in self.shards_in_queue:
                    logger.info(f"I wanted to tell shard ID {shard_id} to connect but they're not in the waitlist - continuing")
                    continue
                self.shards_connecting.append(shard_id)
                self.shard_identify_timestamps.append(dt.utcnow())
                self.shards_in_queue.remove(shard_id)
                self.loop.create_task(self.send_shard_connect(shard_id))
            await asyncio.sleep(0.1)

    async def shard_request(self, shard_id: int, priority: bool = False):
        """
        Add a shard to the waiting list for connections.

        Args:
            shard_id (int): The ID of the shard that's asking to connect.
            priority (bool): Whether or not this ID should be added to the priority waitlist.
        """

        if shard_id in self.shards_in_queue:
            logger.info(f"Shard {shard_id} already in the connection waitlist")
            pass
        elif shard_id in self.shards_connecting:
            logger.info(f"Shard {shard_id} asked to connect again - resending connect payload")
            await asyncio.sleep(1)
            return await self.send_shard_connect(shard_id)
        else:
            if priority:
                logger.info(f"Adding shard {shard_id} to the priority waitlist for connecting")
                self.shards_in_queue.append(shard_id)
                await self.shard_queue.put((0, shard_id))
            else:
                logger.info(f"Adding shard {shard_id} to the waitlist for connecting")
                self.shards_in_queue.append(shard_id)
                await self.shard_queue.put((10, shard_id))
            self.shard_wait_timers[shard_id] = ShardConnectTimer()

    async def send_shard_connect(self, shard_id: int):
        """
        Handle telling a shard that it should connect.

        Args:
            shard_id (int): The ID of the shard that's asking to connect.
        """

        logger.info(f"Telling shard {shard_id} that it can connect now")
        self.shard_connect_timers[shard_id] = ShardConnectTimer()
        await self.tell_shard(shard_id, {
            "shard": shard_id,
            "op": ShardManagerOpCodes.CONNECT_READY.value,
        })

    async def shard_connected(self, shard_id: int):
        """
        Handle receiving the signal on a shard having successfully connected.

        Args:
            shard_id (int): The ID of the shard that just connected.
        """

        connect_time = self.shard_connect_timers[shard_id].get_elapsed_time()
        wait_time = self.shard_wait_timers[shard_id].get_elapsed_time()
        logger.info(f"Shard {shard_id} connected after {connect_time:,.3f}s after being in the queue for {wait_time:,.3f}s")
        self.shards_connecting.remove(shard_id)
        writer = self.shard_stream_writers.pop(shard_id)
        writer.write_eof()
        writer.close()
        await writer.wait_closed()


class ShardManagerClient(object):
    """
    An object to be used by connecting shards to ask when they're allowed to connect.
    """

    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        self.reader = reader
        self.writer = writer
        self.message_listener_task = asyncio.get_event_loop().create_task(self.message_listener())
        self.can_connect = asyncio.Event()

    @classmethod
    async def open_connection(cls, host: str, port: int):
        """
        Connect to the shard manager.
        """

        logger.info("Connecting to shard manager...")
        reader, writer = await asyncio.open_connection(host, port)
        logger.info("Connected")
        return cls(reader, writer)

    async def tell_manager(self, shard_id: int, data: dict):
        """
        Send a JSON message over to the shard manager.
        """

        data.update({"shard": shard_id})
        logger.info(f"Telling shard manager {data}")
        self.writer.write(json.dumps(data).encode() + b"\n")
        await self.writer.drain()

    async def message_listener(self):
        """
        Handles receiving messages from the server.
        """

        while not self.reader.at_eof():

            # Get line
            try:
                raw_data = await self.reader.readline()
            except asyncio.IncompleteReadError:
                return

            # Decode data
            try:
                data = json.loads(raw_data.decode())
            except Exception:
                continue

            # Go through each receivable code and then act on it
            logger.info(f"Received message from shard_manager - {data}")
            if data['op'] == ShardManagerOpCodes.CONNECT_READY.value:
                self.can_connect.set()

            # Wait a bit before trying to read a message again
            await asyncio.sleep(0.1)

    async def ask_to_connect(self, shard_id: int, priority: bool = False):
        """
        A method for bots to use when connecting a shard.
        Waits until it recieves a message saying it's okay to connect
        before continuing.
        """

        while True:
            await self.tell_manager(shard_id, {
                "op": ShardManagerOpCodes.REQUEST_CONNECT.value,
                "priority": priority,
            })
            try:
                await asyncio.wait_for(self.can_connect.wait(), timeout=30)
                return
            except asyncio.TimeoutError:
                logger.info(f"Timed out waiting for connection - asking the shard manager if we can connect again")
                continue

    async def done_connecting(self, shard_id: int):
        """
        A method for bots to use when connecting a shard.
        Waits until it recieves a message saying it's okay to
        connect before continuing.
        """

        await self.tell_manager(shard_id, {
            "op": ShardManagerOpCodes.CONNECT_COMPLETE.value,
        })
        self.writer.write_eof()
        self.writer.close()
        await self.writer.wait_closed()
