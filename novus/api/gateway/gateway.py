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
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from __future__ import annotations

import asyncio
import json
import logging
import platform
import random
import zlib
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
    from .._http import HTTPConnection

__all__ = (
    'GatewayConnection',
)


log = logging.getLogger("novus.gateway.socket")
dump = json.dumps


class GatewayConnection:

    def __init__(self, parent: HTTPConnection) -> None:
        self.parent = parent
        self.ws_url = Route.WS_BASE + "?" + urlencode({
            "v": 10,
            "encoding": "json",
            "compress": "zlib-stream",
        })
        self.cache = self.parent.cache
        self.dispatch = GatewayDispatch(self.parent)

        # Initial identify data (for entire reconnects)
        self.shard_id: int = 0
        self.shard_count: int = 1
        self.presence: None = None
        self.intents: Intents = Intents.none()

        # Websocket data
        self.socket: aiohttp.ClientWebSocketResponse
        self._buffer = bytearray()
        self._zlib = zlib.decompressobj()

        # Cached data
        self.heartbeat_task: asyncio.Task | None = None
        self.sequence: int | None = None
        self.resume_url = self.ws_url
        self.session_id = None

    async def messages(
            self) -> AG[tuple[GatewayOpcode, str | None, int | None, Any], None]:
        while True:
            d = MISSING

            # Get data
            try:
                d = await self.receive()
            except GatewayClose:
                log.info("Gateway closing.")
                return
            except GatewayException as e:
                if not e.reconnect:
                    log.info("Cannot reconnect - starting a new session")
                    await self.close()
                    await self.connect()
                    return
                await self.reconnect()
                continue
            except Exception:
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
            "Sending websocket data %s"
            % dump(sendable).replace(self.parent._token or "\u200b", "TOKEN_REDACTED")
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
            except Exception as e:
                log.error("Failed to read websocket", exc_info=e)
                return None

            # Catch any errors
            if data.type == aiohttp.WSMsgType.ERROR:
                log.info("Got error from socket %s" % data)
                return None
            elif data.type == aiohttp.WSMsgType.CLOSING:
                log.info(
                    "Websocket closing apparently (%s %s)"
                    % (data, data.extra)
                )
                raise GatewayClose()
            elif data.type == aiohttp.WSMsgType.CLOSE:
                log.info(
                    "Socket forced to close (%s %s)"
                    % (data, data.extra)
                )
                raise GatewayException.all_exceptions[data.data]()
            elif data.type == aiohttp.WSMsgType.CLOSED:
                log.info("Socket closed")
                raise GatewayException()

            # Decode data
            data_bytes = data.data
            try:
                self._buffer.extend(data_bytes)
            except Exception as e:
                log.critical("Failed to extend buffer %s" % str(data), exc_info=e)
                raise
            if data_bytes[-4:] == b"\x00\x00\xff\xff":
                decompressed = self._zlib.decompress(self._buffer)
                decoded = decompressed.decode()
                parsed = json.loads(decoded)
                log.debug("Received data from gateway %s" % dump(parsed))
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

        await self.close()
        await self.connect(
            self.ws_url,
            reconnect=True,
        )

    async def connect(
            self,
            ws_url: str | None = None,
            reconnect: bool = False,
            shard_id: int = MISSING,
            shard_count: int = MISSING,
            presence: None = MISSING,
            intents: Intents = MISSING) -> None:
        """
        Create a connection to the gateway.
        """

        # Cache the connect data
        if reconnect is False:
            self.shard_id = shard_id if shard_id is not MISSING else self.shard_id
            self.shard_count = shard_count if shard_count is not MISSING else self.shard_count
            self.presence = presence if presence is not MISSING else self.presence
            self.intents = intents if intents is not MISSING else self.intents

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
        log.info("Creating websocket connection to %s" % ws_url or self.ws_url)
        ws = await session.ws_connect(ws_url or self.ws_url)
        self.socket = ws

        # Send hello
        got = await self.receive()
        if got is None:
            return
        _, _, _, data = got
        log.info("Connected to gateway - %s" % dump(data))

        # Start heartbeat
        heartbeat_interval = data["heartbeat_interval"]
        self.heartbeat_task = asyncio.create_task(
            self.heartbeat(heartbeat_interval, jitter=not reconnect)
        )

        # Send identify or resume
        if reconnect:
            await self.resume()
        else:
            await self.identify()
            self.message_task = asyncio.create_task(self.message_handler())

    async def close(self) -> None:
        """
        Close the gateway connection, cancelling the heartbeat task.
        """

        if self.heartbeat_task is not None:
            self.heartbeat_task.cancel()
        if self.socket and not self.socket.closed:
            await self.socket.close()

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
        while True:
            try:
                await asyncio.sleep(wait / 1_000)
            except asyncio.CancelledError:
                return
            await self.send(GatewayOpcode.heartbeat, self.sequence)
            wait = heartbeat_interval

    async def identify(self) -> None:
        """
        Send an identify to Discord.
        """

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
                "intents": str(self.intents.value),
            },
        )

    async def resume(self) -> None:
        """
        Send a resume to Discord.
        """

        token = cast(str, self.parent._token)
        await self.send(
            GatewayOpcode.resume,
            {
                "token": token,
                "session_id": self.session_id,
                "seq": self.sequence,
            },
        )

    async def handle_dispatch(self, event_name: str, message: dict) -> None:
        try:
            await self.dispatch.handle_dispatch(event_name, message)
        except Exception as e:
            log.error("Error in dispatch (%s) (%s)" % (event_name, dump(message)), exc_info=e)

    async def message_handler(self) -> None:
        """
        Handle new incomming messages from the gateway.
        """

        # Go through each valid Discord message
        async for opcode, event_name, sequence, message in self.messages():
            match opcode:

                # Ignore heartbeat acks
                case GatewayOpcode.heartbeat_ack:
                    pass

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
                    await self.reconnect()

                # Deal with invalid sesions
                case GatewayOpcode.invalidate_session:
                    if message is True:
                        await self.reconnect()
                    else:
                        log.warning("Session invalidated - creating a new session")
                        await self.close()
                        await self.connect()
                        return  # Cancel this task so a new one will be created

                # Everything else
                case _:
                    print("Failed to deal with gateway message %s" % dump(message))
