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

from ..enums import GatewayOpcode
from ..flags import Intents
from ..models import Guild, User
from ..utils import try_snowflake
from ._route import Route

if TYPE_CHECKING:
    from ._http import HTTPConnection


log = logging.getLogger("novus.websocket")
dump = json.dumps


class GatewayException(Exception):
    """
    When you get a generic gateway exception.
    """


class GatewayUnauthorized(GatewayException):
    """
    If you try and identify with an invalid token.
    """


class GatewayInvalidIntents(GatewayException):
    """
    Disallowed intents.
    """


class GatewayConnection:

    def __init__(self, parent: HTTPConnection) -> None:
        self.parent = parent
        self.ws_url = Route.WS_BASE + "?" + urlencode({
            "v": 10,
            "encoding": "json",
            "compress": "zlib-stream",
        })
        self.cache = self.parent.cache

        # Websocket data
        self.socket: aiohttp.ClientWebSocketResponse
        self._buffer = bytearray()
        self._zlib = zlib.decompressobj()

        # Cached data
        self.heartbeat_task: asyncio.Task | None = None
        self.sequence: int = -1
        self.resume_url = self.ws_url

    async def messages(
            self) -> AG[tuple[GatewayOpcode, str | None, int | None, dict[Any, Any]], None]:
        while True:
            try:
                d = await self.receive()
            except Exception:
                return
            if d is None:
                return
            yield d

    async def send(self, opcode: GatewayOpcode, data: dict | None = None) -> None:
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
        if data is not None:
            sendable["d"] = data
        log.debug("Sending websocket data %s" % dump(sendable))
        await self.socket.send_json(sendable)

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
                log.info("Websocket closing apparently")
                continue
            elif data.type == aiohttp.WSMsgType.CLOSE:
                log.info("Socket forced to close (%s %s)" % (data, data.extra))
                match data.data:
                    case 4004:
                        raise GatewayUnauthorized()
                    case 4014:
                        raise GatewayInvalidIntents()
                    case _:
                        raise GatewayException()
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

    async def connect(
            self,
            shard_id: int = 0,
            shard_count: int = 1,
            presence: None = None,
            intents: Intents = Intents.none()) -> None:
        """
        Create a connection to the gateway.
        """

        # Open socket
        session = await self.parent.get_session()
        log.info("Creating websocket connection to %s" % self.ws_url)
        ws = await session.ws_connect(self.ws_url)
        self.socket = ws

        # Send hello
        got = await self.receive()  # pyright: ignore
        if got is None:
            return
        _, _, _, data = got
        log.info("Connected to gateway - %s" % dump(data))

        # Start heartbeat
        heartbeat_interval = data["heartbeat_interval"]
        self.heartbeat_task = asyncio.create_task(
            self.heartbeat(heartbeat_interval, jitter=True)
        )

        # Send identify
        await self.identify(
            shard_id=shard_id,
            shard_count=shard_count,
            presence=presence,
            intents=intents,
        )
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
        while True:
            try:
                await asyncio.sleep(wait / 1_000)
            except asyncio.CancelledError:
                return
            await self.send(GatewayOpcode.heartbeat)
            wait = heartbeat_interval

    async def identify(
            self,
            shard_id: int = 0,
            shard_count: int = 1,
            presence: None = None,
            intents: Intents = Intents.none()) -> None:
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
                "shard": [shard_id, shard_count],
                "intents": str(intents.value),
            },
        )

    async def handle_dispatch(self, event_name: str, data: dict) -> None:
        """
        Handle a Dispatch message from Discord.
        """

        match event_name:
            case "READY":
                self.cache.user = User(state=self.parent, data=data['user'])
                self.cache.application_id = try_snowflake(data['application']['id'])

            case "GUILD_CREATE":
                guild = Guild(state=self.parent, data=data)  # pyright: ignore
                await guild._sync(data=data)  # pyright: ignore
                self.cache.guilds[guild.id] = guild
                self.cache.users.update({
                    k: v._user
                    for k, v in guild._members.items()
                })
                self.cache.channels.update(guild._channels)
                self.cache.channels.update(guild._threads)
                self.cache.emojis.update(guild._emojis)
                self.cache.stickers.update(guild._stickers)
                self.cache.events.update(guild._guild_scheduled_events)

            case "PRESENCE_UPDATE":
                log.debug("Ignoring presence update %s" % dump(data))

            case _:
                print("Failed to parse event %s %s" % (event_name, dump(data)))

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
                    try:
                        await self.handle_dispatch(event_name, message)
                    except Exception as e:
                        print(e)

                # Everything else
                case _:
                    print("Failed to deal with gateway message %s" % dump(message))
