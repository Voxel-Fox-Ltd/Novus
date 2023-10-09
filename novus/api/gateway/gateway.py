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
import json
import logging
import platform
import random
import zlib
from collections import defaultdict
from typing import TYPE_CHECKING, Any
from typing import AsyncGenerator as AG
from typing import cast
from urllib.parse import urlencode

import aiohttp

from ...enums import GatewayOpcode
from ...flags import Intents
from ...utils import MISSING
from .._errors import GatewayClose, GatewayException
from .._route import Route
from .dispatch import GatewayDispatch

if TYPE_CHECKING:
    from ... import Activity, GuildMember, Status, payloads
    from .._http import APICache, HTTPConnection

__all__ = (
    'GatewayConnection',
    'GatewayShard',
)


log = logging.getLogger("novus.gateway.socket")
dump = json.dumps


class GatewayConnection:

    def __init__(self, parent: HTTPConnection) -> None:
        self.parent = parent
        self.presence: None = None
        self.intents: Intents = Intents.none()
        self.shards: set[GatewayShard] = set()
        self.shard_count: int = 1
        self.guild_ids_only: bool = False

    async def connect(
            self,
            *,
            shard_ids: list[int] | None,
            shard_count: int,
            max_concurrency: int = 1,
            presence: None = None,
            intents: Intents = Intents.none()) -> None:
        """
        Gateway entry point - connect the bot to the gateway across all shards.

        Parameters
        ----------
        shard_ids : list[int] | None
            The IDs of the shards that you want to connect.
            If ``None`` is provided, then all shards in ``shard_count`` are
        shard_count : int
            The total number of shards (across all clusters) that are connecting
            to the gateway.
        max_concurrency : int
            The maximum number of shards that can connect/identify at the same
            time.
        presence
            The bot's initial status.
        intents : novus.Intents
            The intents that should be used when identifying.
        """

        # Store values we'll need elsewhere
        self.presence = presence
        self.intents = intents
        self.shards = set()
        self.shard_count = shard_count

        # Make some semaphores so we can control which shards connect
        # simultaneously
        identify_semaphore = asyncio.Semaphore(max_concurrency)
        connect_semaphore = asyncio.Semaphore(1)

        # Create shard objects
        shard_ids = shard_ids or list(range(shard_count))
        tasks: list[asyncio.Task] = []
        for i in shard_ids:
            gs = GatewayShard(
                parent=self.parent,
                shard_id=i,
                shard_count=shard_count,
                presence=presence,
                intents=intents,
                identify_semaphore=identify_semaphore,
                connect_semaphore=connect_semaphore,
            )
            self.shards.add(gs)

        # Wait for shards to connect
        log.info("Opening gateway connection with %s shards (IDs %s)", len(self.shards), shard_ids)
        await asyncio.gather(*(i.connect() for i in self.shards))

    async def wait(self) -> None:
        """
        A continuous asyncio loop for any shard being connected.
        """

        while any((shard.running for shard in self.shards)):
            await asyncio.sleep(1)

    async def close(self) -> None:
        """
        Close all connected shards.
        """

        for i in self.shards:
            await i.close()

    async def get_gateway(self) -> payloads.gateway.Gateway:
        """
        Get a gateway connection URL. Doesn't require auth.
        """

        session = await self.parent.get_session()
        route = Route("GET", "/gateway")
        resp = await session.request(route.method, route.url)
        return await resp.json()

    async def get_gateway_bot(self) -> payloads.gateway.GatewayBot:
        """
        Get a gateway connection URL for the given bot.
        """

        route = Route("GET", "/gateway/bot")
        return await self.parent.request(route)


class GatewayShard:

    def __init__(
            self,
            parent: HTTPConnection,
            *,
            shard_id: int,
            shard_count: int,
            presence: None = None,
            intents: Intents = Intents.none(),
            connect_semaphore: asyncio.Semaphore,
            identify_semaphore: asyncio.Semaphore) -> None:
        self.parent = parent
        self.ws_url = Route.WS_BASE + "?" + urlencode({
            "v": 10,
            "encoding": "json",
            "compress": "zlib-stream",
        })
        self.dispatch = GatewayDispatch(self)
        self.connect_semaphore = connect_semaphore
        self.identify_semaphore = identify_semaphore
        self.connecting = asyncio.Event()
        self.ready = asyncio.Event()
        self.heartbeat_received = asyncio.Event()

        # Initial identify data (for entire reconnects)
        self.shard_id: int = shard_id
        self.shard_count: int = shard_count
        self.presence: None = presence
        self.intents: Intents = intents

        # Websocket data
        self.socket: aiohttp.ClientWebSocketResponse = None  # pyright: ignore
        self._buffer = bytearray()
        self._zlib = zlib.decompressobj()

        # Cached data
        self.heartbeat_task: asyncio.Task | None = None
        self.message_task: asyncio.Task | None = None
        self.sequence: int | None = None
        self.resume_url = self.ws_url
        self.session_id = None

        # Temporarily cached data for combining requests
        self.chunk_counter: dict[str, int] = {}  # nonce: req_counter
        self.chunk_groups: dict[str, list[GuildMember]] = defaultdict(list)
        self.chunk_event: dict[str, asyncio.Event] = {}

    @property
    def cache(self) -> APICache:
        return self.parent.cache

    @property
    def running(self) -> bool:
        """
        Returns whether or not the shard is currently connected to the gateway.

        Returns
        -------
        bool
        """

        # Check we have/had a heartbeat
        if self.heartbeat_task is None:
            return True
        if not self.heartbeat_task.done():
            return True

        # Check we have an open socket
        if self.socket is None:
            return True
        if not self.socket.closed:
            return True

        # Check we listened for messages
        if self.message_task is None:
            return True
        if not self.message_task.done():
            return True

        # See if we're connecting
        if self.connecting.is_set():
            return True

        # Ay nice
        return False

    async def messages(
            self) -> AG[tuple[GatewayOpcode, str | None, int | None, Any], None]:
        """
        Deal with getting and receiving messages.
        """

        while True:
            d = MISSING

            # Get data
            try:
                d = await self.receive()
            except GatewayClose:
                log.info("[%s] Gateway closing.", self.shard_id)
                await self.reconnect()
                continue
            except GatewayException as e:
                if not e.reconnect:
                    log.info("[%s] Cannot reconnect.", self.shard_id)
                    raise
                asyncio.create_task(self.reconnect())
                return
            except Exception as e:
                log.error("[%s] Hit error receiving", self.shard_id, exc_info=e)
                return

            # Yield data
            if d is None:
                return
            elif d is MISSING:
                continue
            yield d

    async def send(self, opcode: GatewayOpcode, data: Any = MISSING) -> None:
        """
        Send a heartbeat to the connected socket.
        Will raise if there is no valid connected socket.
        """

        if self.socket is None:
            raise ValueError("Cannot receive messages from non-existing socket")
        elif self.socket.closed:
            raise ValueError("Cannot receive messages from closed socket")
        sendable: dict[Any, Any] = {
            "op": opcode.value,
        }
        if data is not MISSING:
            sendable["d"] = data
        log.debug(
            "[%s] Sending websocket data %s",
            self.shard_id,
            dump(sendable).replace(self.parent._token or "\u200b", "TOKEN_REDACTED")
        )
        dumped = dump(
            sendable,
            separators=(',', ':'),
            ensure_ascii=True,
        )
        await self.socket.send_str(dumped)

    async def receive(
            self) -> tuple[GatewayOpcode, str | None, int | None, dict[Any, Any]] | None:
        """
        Receive a message from the gateway.
        """

        # Make sure we have a socket
        if self.socket is None:
            raise ValueError("Cannot receive messages from non-existing socket")
        elif self.socket.closed:
            raise ValueError("Cannot receive messages from closed socket")

        # Loop until we have a whole message
        while True:

            # Read data from the socket
            try:
                data = await self.socket.receive()
            except GatewayException:
                raise
            except Exception as e:
                log.error("[%s] Failed to read websocket", self.shard_id, exc_info=e)
                return None

            # Catch any errors
            if data.type == aiohttp.WSMsgType.ERROR:
                log.info("[%s] Got error from socket %s", self.shard_id, data)
                return None
            elif data.type == aiohttp.WSMsgType.CLOSING:
                log.info(
                    "[%s] Websocket currently closing (%s %s)",
                    self.shard_id, data, data.extra,
                )
                raise GatewayClose()
            elif data.type == aiohttp.WSMsgType.CLOSE:
                log.info(
                    "[%s] Socket told to close (%s %s)",
                    self.shard_id, data, data.extra,
                )
                raise GatewayException.all_exceptions[data.data]()
            elif data.type == aiohttp.WSMsgType.CLOSED:
                log.info("[%s] Socket closed", self.shard_id)
                raise GatewayException()

            # Load data into the buffer if we need to
            data_bytes = data.data
            if type(data_bytes) is bytes:
                try:
                    self._buffer.extend(data_bytes)
                except Exception as e:
                    log.critical("[%s] Failed to extend buffer %s",
                        self.shard_id, str(data), exc_info=e,
                    )
                    raise

            # See if we have a complete message now
            complete_message_received = (
                self._buffer[-4:] == b"\x00\x00\xff\xff"
                or type(data_bytes) is not bytes
            )
            if not complete_message_received:
                return

            # Deal with our complete data
            if type(data_bytes) is not bytes:
                decompressed = data_bytes
            else:
                try:
                    decompressed = self._zlib.decompress(self._buffer)
                except Exception as e:
                    log.error(
                        "[%s] Failed to decompress buffer (%s)",
                        self.shard_id, data_bytes, exc_info=e,
                    )
                    raise GatewayClose()
            self._buffer.clear()

            # Deal with our decompressed data
            try:
                if isinstance(decompressed, bytes):
                    decoded = decompressed.decode()
                else:
                    decoded = decompressed
                parsed = json.loads(decoded)
            except MemoryError:
                log.error(
                    "[%s] Hit memory error. Whoops.",
                    self.shard_id,
                )
                self._buffer.clear()
                raise GatewayClose()

            # Return our parsed data :)
            log.debug(
                "[%s] Received data from gateway %s",
                self.shard_id, dump(parsed),
            )
            self._buffer.clear()
            return (
                GatewayOpcode(parsed["op"]),
                parsed.get("t"),
                parsed.get("s"),
                parsed.get("d"),
            )

    async def reconnect(self) -> None:
        """
        Reconnect to the gateway.
        """

        self.connecting.set()
        await self.close(code=0)
        await self.connect(
            self.resume_url,
            reconnect=True,
        )

    async def connect(
            self,
            ws_url: str | None = None,
            reconnect: bool = False):
        """
        Connect to the gateway, using the connection semaphore.
        """

        async with self.connect_semaphore:
            await self._connect(ws_url, reconnect)

    async def _connect(
            self,
            ws_url: str | None = None,
            reconnect: bool = False,
            attempt: int = 1) -> None:
        """
        Create a connection to the gateway.
        """

        # Clear caches
        self.connecting.set()
        self._buffer.clear()
        self._zlib = zlib.decompressobj()

        # Close socket if it's open at the moment
        if self.socket and not self.socket.closed:
            log.info(
                (
                    "[%s] Trying to open new connection while connection is "
                    "already open - closing current connection before opening "
                    "a new one"
                ),
                self.shard_id,
            )
            await self.close(0)
            reconnect = True

        # Cache the connect data
        if reconnect is False:

            # This is our first connection; let's update the cache based on the
            # intents
            if not self.intents.guilds:
                self.cache.add_guilds = self.cache.do_nothing
                self.cache.add_channels = self.cache.do_nothing
            if not self.intents.guild_members:
                self.cache.add_users = self.cache.do_nothing
            if not self.intents.guild_scheduled_events:
                self.cache.add_events = self.cache.do_nothing
            if not self.intents.guild_emojis_and_stickers:
                self.cache.add_emojis = self.cache.do_nothing
                self.cache.add_stickers = self.cache.do_nothing
            if not self.intents.message_content:
                self.cache.add_messages = self.cache.do_nothing

        # Open socket
        if reconnect is False:
            self.sequence = None
        session = await self.parent.get_session()
        ws_url = ws_url or self.ws_url
        log.info("[%s] Creating websocket connection to %s", self.shard_id, ws_url)
        try:
            ws = await session.ws_connect(ws_url)
        except Exception:
            if attempt >= 5:
                log.info(
                    "[%s] Failed to connect to open ws connection, closing (%s)",
                    self.shard_id, attempt,
                )
                return await self.close()
            log.info(
                "[%s] Failed to connect to open ws connection, reattempting (%s)",
                self.shard_id, attempt,
            )
            return await self._connect(
                ws_url=ws_url,
                reconnect=reconnect,
                attempt=attempt + 1,
            )
        self.socket = ws

        # Send hello
        try:
            got = await self.receive()
        except GatewayException:
            return await self.close()
        except Exception:
            if attempt >= 5:
                log.info(
                    "[%s] Failed to connect to gateway, closing (%s)",
                    self.shard_id, attempt,
                )
                return await self.close()
            log.info(
                "[%s] Failed to connect to gateway, reattempting (%s)",
                self.shard_id, attempt,
            )
            return await self._connect(
                ws_url=ws_url,
                reconnect=reconnect,
                attempt=attempt + 1,
            )
        if got is None:
            return
        _, _, _, data = got
        log.info("[%s] Connected to gateway - %s", self.shard_id, dump(data))

        # Start heartbeat
        heartbeat_interval = data["heartbeat_interval"]
        self.heartbeat_task = asyncio.create_task(
            self.heartbeat(heartbeat_interval, jitter=not reconnect)
        )

        # Send identify or resume
        self.ready.clear()
        timeout = 10
        try:
            if reconnect:
                await asyncio.wait_for(self.resume(), timeout)
            else:
                await asyncio.wait_for(self.identify(), timeout)
        except asyncio.CancelledError:
            log.info(
                "[%s] Failed to get a response from resume/idenfity after %s seconds, reattempting connect (%s)",
                self.shard_id, timeout, attempt,
            )
            return await self._connect(
                ws_url=ws_url,
                reconnect=reconnect,
                attempt=attempt + 1,
            )
        self.message_task = asyncio.create_task(self.message_handler())
        await self.ready.wait()
        self.connecting.clear()

    async def close(self, code: int = 1_000) -> None:
        """
        Close the gateway connection, cancelling the heartbeat task.
        """

        if any((
                self.heartbeat_task is not None,
                self.message_task is not None,
                self.socket and not self.socket.closed)):
            log.info("[%s] Closing shard connection", self.shard_id)
        if self.heartbeat_task is not None:
            self.heartbeat_task.cancel()
        if self.message_task is not None:
            self.message_task.cancel()
        if self.socket and not self.socket.closed:
            try:
                await asyncio.wait_for(self.socket.close(code=0), timeout=1)
            except asyncio.TimeoutError:
                pass

    async def heartbeat(
            self,
            heartbeat_interval: int | float,
            *,
            jitter: bool = False) -> None:
        """
        Send heartbeats to Discord. This implements a forever loop, so the
        method should be created as a task.
        """

        if heartbeat_interval <= 0:
            raise ValueError("Heartbeat interval cannot be below 0")
        wait = heartbeat_interval
        if jitter:
            wait = heartbeat_interval * random.random()
            log.info(
                (
                    f"Starting heartbeat - initial {wait / 100:.2f}s, "
                    f"normally {heartbeat_interval / 100:.2f}s"
                )
            )
        else:
            log.info(f"Starting heartbeat at {heartbeat_interval / 100:.2f}s")
        while True:
            try:
                await asyncio.sleep(wait / 1_000)
            except asyncio.CancelledError:
                log.info("[%s] Heartbeat has been cancelled", self.shard_id)
                return
            for beat_attempt in range(1_000):
                await self.send(GatewayOpcode.heartbeat, self.sequence)
                try:
                    await asyncio.wait_for(self.heartbeat_received.wait(), timeout=10)
                except asyncio.CancelledError:
                    if beat_attempt <= 5:
                        log.info(
                            (
                                "Failed to get a response to heartbeat (attempt "
                                "%s) - trying again"
                            ),
                            beat_attempt,
                        )
                        continue
                    log.info(
                        (
                            "Failed to get a response to heartbeat (attempt "
                            "%s) - starting new connection"
                        ),
                        beat_attempt,
                    )
                    asyncio.create_task(self.connect())
                    return
                else:
                    break
            wait = heartbeat_interval

    async def identify(self) -> None:
        """
        Send an identify to Discord.
        """

        log.info("[%s] Sending identify", self.shard_id)
        token = cast(str, self.parent._token)
        await self.send(
            GatewayOpcode.identify,
            {
                "token": token,
                "properties": {
                    "os": platform.system(),
                    "browser": "Novus",
                    "device": "Novus",
                },
                "shard": [self.shard_id, self.shard_count],
                "intents": self.intents.value,
            },
        )

    async def chunk_guild(
            self,
            guild_id: int,
            query: str = "",
            limit: int = 0,
            user_ids: list[int] | None = None,
            nonce: str | None = None) -> asyncio.Event | None:
        """
        Send a request to chunk a guild.
        """

        log.info("[%s] Chunking guild %s", self.shard_id, guild_id)
        data = {
            "guild_id": str(guild_id),
            "limit": limit,
        }
        if user_ids is None:
            data["query"] = query
        else:
            data["user_ids"] = [str(i) for i in user_ids]
        event = None
        if nonce:
            data["nonce"] = nonce
            self.chunk_counter[nonce] = 0
            self.chunk_event[nonce] = event = asyncio.Event()
            self.chunk_groups[nonce] = []
        await self.send(
            GatewayOpcode.request_members,
            data,
        )
        return event

    async def resume(self) -> None:
        """
        Send a resume to Discord.
        """

        log.info("[%s] Sending resume", self.shard_id)
        token = cast(str, self.parent._token)
        await self.send(
            GatewayOpcode.resume,
            {
                "token": token,
                "session_id": self.session_id,
                "seq": self.sequence,
            },
        )

    async def change_presence(
            self,
            activities: list[Activity],
            status: Status) -> None:
        """
        Change the presence of the client.

        Parameters
        ----------
        activities : list[novus.Activity]
            The activities that you want to set the client as displaying.
        status : novus.Status
            The status of the client.
        """

        log.debug("[%s] Sending change presence", self.shard_id)
        await self.send(
            GatewayOpcode.presence,
            {
                "activities": [i._to_data() for i in activities],
                "status": status.value,
                "since": None,
                "afk": False,
            },
        )

    async def handle_dispatch(self, event_name: str, message: dict) -> None:
        try:
            await self.dispatch.handle_dispatch(event_name, message)
        except Exception as e:
            log.error(
                "Error in dispatch (%s) (%s)", event_name, dump(message),
                exc_info=e,
            )

    async def message_handler(self) -> None:
        """
        Handle new incomming messages from the gateway.
        """

        # Go through each valid Discord message
        async for opcode, event_name, sequence, message in self.messages():
            match opcode:

                # Ignore heartbeat acks
                case GatewayOpcode.heartbeat_ack:
                    self.heartbeat_received.set()

                # Deal with dispatch
                case GatewayOpcode.dispatch:
                    event_name = cast(str, event_name)
                    sequence = cast(int, sequence)
                    self.sequence = sequence
                    asyncio.create_task(
                        self.handle_dispatch(event_name, message),
                        name="Dispatch handler for sequence %s" % sequence
                    )

                # Deal with reconnects
                case GatewayOpcode.reconnect:
                    asyncio.create_task(self.reconnect())
                    return

                # Deal with invalid sesions
                case GatewayOpcode.invalidate_session:
                    if message is True:
                        asyncio.create_task(self.reconnect())
                        return
                    else:
                        log.warning(
                            "[%s] Session invalidated - creating a new session",
                            self.shard_id,
                        )
                        try:
                            await asyncio.wait_for(self.close(), timeout=5)
                        except asyncio.CancelledError:
                            pass
                        asyncio.create_task(self.connect())
                        return  # Cancel this task so a new one will be created

                # Everything else
                case _:
                    print("Failed to deal with gateway message %s" % dump(message))
