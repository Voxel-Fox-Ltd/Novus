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
from .._errors import (
    GatewayAuthenticationFailed,
    GatewayClose,
    GatewayClosed,
    GatewayException,
)
from .._route import Route
from .dispatch import GatewayDispatch

if TYPE_CHECKING:
    from ... import Activity, GuildMember, payloads
    from .._http import APICache, HTTPConnection

__all__ = (
    'GatewayConnection',
    'GatewayShard',
)


log = logging.getLogger("novus.gateway.socket")
dump = json.dumps


class GatewayInvalidSession(Exception):

    def __init__(self, resumable: bool) -> None:
        self.resumable = resumable
        super().__init__(f"Gateway invalid session; resumable={resumable}")


class GatewayReconnectRequired(Exception):

    def __init__(self, *, resume: bool, ws_url: str | None = None) -> None:
        self.resume = resume
        self.ws_url = ws_url


class GatewayConnection:

    def __init__(self, parent: HTTPConnection) -> None:
        self.parent = parent
        self.presence: None = None
        self.intents: Intents = Intents.none()
        self.shards: dict[int, GatewayShard] = {}
        self.shard_count: int = 1
        self.guild_ids_only: bool = False

    async def connect(
            self,
            *,
            shard_ids: list[int] | None,
            shard_count: int,
            max_concurrency: int = 1,
            presence: None = None,
            intents: Intents = Intents.none(),
            sleep: bool = False) -> None:
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
        sleep : bool
            Whether or not the shards should sleep before attempting to open
            a websocket connection.
        """

        # Store values we'll need elsewhere
        self.presence = presence
        self.intents = intents
        self.shards = {}
        self.shard_count = shard_count

        # Make some semaphores so we can control which shards connect
        # simultaneously
        identify_semaphore = asyncio.Semaphore(max_concurrency)
        connect_semaphore = asyncio.Semaphore(max_concurrency)

        # Create shard objects
        shard_ids = shard_ids or list(range(shard_count))
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
            self.shards[i] = gs

        # Wait for shards to connect
        log.info(
            "Opening gateway connection with %s shards (IDs %s) and count %s",
            len(self.shards), shard_ids, shard_count)
        await asyncio.gather(*(i.connect(sleep=sleep) for i in self.shards.values()))

    async def wait(self) -> None:
        """
        A continuous asyncio loop for any shard being connected.
        """

        while any((shard.running for shard in self.shards.values())):
            await asyncio.sleep(1)

    async def close(self) -> None:
        """
        Close all connected shards.
        """

        for i in self.shards.values():
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
        self.ready_received = asyncio.Event()
        self.heartbeat_received = asyncio.Event()
        self.invalid_session_received = asyncio.Event()
        self.invalid_session_resumable: bool | None = None

        self.state: str = "Closed"

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
        self.reconnect_task: asyncio.Task | None = None
        self.sequence: int | None = None
        self.resume_url = self.ws_url
        self.session_id = None
        self.heartbeat_interval = 60.0

        # Temporarily cached data for combining requests
        self.chunk_counter: dict[str, int] = {}  # nonce: req_counter
        self.chunk_groups: dict[str, list[GuildMember]] = defaultdict(list)
        self.chunk_event: dict[str, asyncio.Event] = {}

        # And this is because I hate Python
        self.running_tasks: set[asyncio.Task] = set()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}[{self.shard_id}] state={self.state!r}>"

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
            self) -> AG[tuple[int, str | None, int | None, Any], None]:
        """
        Deal with getting and receiving messages.
        """

        while True:
            d = MISSING

            # Get data
            try:
                d = await self.receive()
            except (GatewayClose, GatewayClosed) as e:
                if isinstance(e, GatewayClosed):
                    log.info("[%s] Gateway closed by Discord", self.shard_id)
                elif isinstance(e, GatewayClose):
                    log.info("[%s] Gateway told to close by Discord", self.shard_id)
                self.reconnect(resume=True)
                return
            except GatewayAuthenticationFailed:
                log.info("[%s] Gateway authentication failed, closing with error code", self.shard_id)
                exit(1)
            except GatewayException as e:
                log.debug("[%s] Generic gateway exception %s", self.shard_id, e, exc_info=e)
                self.reconnect(resume=e.reconnect)
                return
            except Exception as e:
                log.debug("[%s] Hit error receiving", self.shard_id, exc_info=e)
                self.reconnect(resume=False)
                return

            # Yield data
            if d is None:
                return
            elif d is MISSING:
                continue
            yield d

    async def send(self, opcode: int, data: Any = MISSING) -> None:
        """
        Send a heartbeat to the connected socket.
        Will raise if there is no valid connected socket.
        """

        if self.socket is None:
            raise ValueError("Cannot receive messages from non-existing socket")
        elif self.socket.closed:
            raise ValueError("Cannot receive messages from closed socket")
        sendable: dict[Any, Any] = {
            "op": opcode,
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
            self) -> tuple[int, str | None, int | None, dict[Any, Any]] | None:
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
                log.error("[%s] Got error from socket %s", self.shard_id, data)
                return None
            elif data.type == aiohttp.WSMsgType.CLOSING:
                log.debug(
                    "[%s] Websocket currently closing (%s %s)",
                    self.shard_id, data, data.extra,
                )
                raise GatewayClose()
            elif data.type == aiohttp.WSMsgType.CLOSE:
                log.debug(
                    "[%s] Socket told to close (%s %s)",
                    self.shard_id, data, data.extra,
                )
                if data.data is None:
                    raise GatewayClosed()
                raise GatewayException.all_exceptions[data.data]()
            elif data.type == aiohttp.WSMsgType.CLOSED:
                log.debug("[%s] Socket closed by Discord (%s)", self.shard_id, data)
                raise GatewayException()

            # Load data into the buffer if we need to
            data_bytes = data.data
            if type(data_bytes) is bytes:
                try:
                    self._buffer.extend(data_bytes)
                except Exception as e:
                    log.critical(
                        "[%s] Failed to extend buffer %s",
                        self.shard_id, str(data), exc_info=e,
                    )
                    raise

            # See if we have a complete message now
            complete_message_received = (
                self._buffer[-4:] == b"\x00\x00\xff\xff"
                or type(data_bytes) is not bytes
            )
            if not complete_message_received:
                return None

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
                int(parsed["op"]),
                parsed.get("t"),
                parsed.get("s"),
                parsed.get("d"),
            )

    async def _reconnect(self, resume: bool = True) -> None:
        """
        Reconnect to the gateway.
        """

        log.debug("[%s] Starting reconnect... resume=%s", self.shard_id, resume)

        self.connecting.set()
        await self.close(code=0)

        if resume:
            ws_url = self.resume_url
        else:
            ws_url = self.ws_url
            self.session_id = None
            self.sequence = None
            self.resume_url = self.ws_url

        await self.connect(
            ws_url,
            resume=resume,
        )

    def reconnect(self, resume: bool = True) -> None:
        if self.reconnect_task is not None and not self.reconnect_task.done():
            log.debug(
                "[%s] Reconnect already running; ignoring duplicate reconnect",
                self.shard_id,
            )
            return

        self.reconnect_task = asyncio.create_task(
            self._reconnect(resume=resume),
            name=f"Reconnect shard {self.shard_id}",
        )
        self.running_tasks.add(self.reconnect_task)
        self.reconnect_task.add_done_callback(self.running_tasks.discard)

    async def connect(
            self,
            ws_url: str | None = None,
            resume: bool = False,
            sleep: bool = False) -> None:
        """
        Connect to the gateway, using the connection semaphore.
        """

        await self._connect(
            ws_url,
            resume,
            sleep_time=self.shard_id if sleep else 0.0,
        )

    async def _connect(
            self,
            ws_url: str | None = None,
            resume: bool = False,
            attempt: int = 1,
            sleep_time: float = 0.0) -> None:
        """
        Opens a new connection to the gateway, sending all relevant payloads
        and starting all relevant background tasks.
        """

        # Clear caches
        self.connecting.set()
        self._buffer.clear()
        self._zlib = zlib.decompressobj()

        # Close socket if it's open at the moment
        if self.socket and not self.socket.closed:
            log.debug(
                (
                    "[%s] Trying to open new connection while connection is "
                    "already open - closing current connection before opening "
                    "a new one"
                ),
                self.shard_id,
            )
            await self.close(0)

        # Do our generic setup
        if resume is False:
            self.sequence = None
        session = await self.parent.get_session()
        ws_url = ws_url or self.ws_url
        if sleep_time:
            log.debug("[%s] Sleeping %ss before attempting connection", self.shard_id, sleep_time)
            self.state = "Sleeping before connecting"
            await asyncio.sleep(sleep_time)

        # One big try/except so we can put everything inside of the semaphore
        HELLO_TIMEOUT = 60.0
        try:
            if resume:
                self.state = "Pending reconnect"
            else:
                self.state = "Pending connect"

            # Open semaphore
            async with self.connect_semaphore:

                # Open websocket
                log.info("[%s] Creating websocket connection to %s", self.shard_id, ws_url)
                if resume:
                    self.state = "Reconnecting"
                else:
                    self.state = "Connecting"
                try:
                    ws = await session.ws_connect(ws_url, timeout=10.0, max_msg_size=0)
                    self.socket = ws
                except Exception as e:
                    raise ValueError("Failed to connect to websocket") from e

                # Get hello
                self.state = "Waiting for HELLO"
                log.debug("[%s] Waiting for a HELLO", self.shard_id)
                try:
                    got = await asyncio.wait_for(self.receive(), timeout=HELLO_TIMEOUT)
                except Exception as e:
                    raise IndexError("Failed to get HELLO from gateway") from e
                if got is None:
                    return
                _, _, _, hello_data = got
                log.debug("[%s] Connected to gateway - %s", self.shard_id, dump(hello_data))

                # Send identify or resume
                self.ready_received.clear()
                self.message_task = asyncio.create_task(self.message_handler())
                try:
                    await self.send_resume_identify(resume=resume)
                except GatewayInvalidSession as e:
                    log.info(
                        "[%s] Gateway invalidated session during %s; resumable=%s",
                        self.shard_id,
                        "RESUME" if resume else "IDENTIFY",
                        str(e.resumable).lower(),
                    )

                    log.info("[%s] Closing current connection and opening new one", self.shard_id)

                    if e.resumable:
                        raise GatewayReconnectRequired(
                            resume=True,
                            ws_url=self.resume_url,
                        )

                    self.session_id = None
                    self.sequence = None
                    self.resume_url = self.ws_url

                    raise GatewayReconnectRequired(
                        resume=False,
                        ws_url=self.ws_url,
                    )
                except asyncio.TimeoutError as e:
                    raise AssertionError("Failed to receive READY/RESUMED in time") from e

                # Start heartbeat
                self.heartbeat_interval = hello_data["heartbeat_interval"]
                self.heartbeat_task = asyncio.create_task(
                    self.heartbeat(self.heartbeat_interval, jitter=not resume),
                    name="Heartbeat for shard %s" % self.shard_id,
                )

                # And we should be connected!
                return

        # Failed to connect to socket
        except ValueError as e:
            log.debug(
                "[%s] Failed to connect to websocket (%s - %s), reattempting (%s)",
                self.shard_id, type(e), e, attempt,
            )
            await self.close(code=0)
            return await self._connect(
                ws_url=ws_url,
                resume=resume,
                attempt=attempt + 1,
            )

        # Failed to get HELLO from gateway
        except IndexError as e:
            log.debug(
                "[%s] Failed to get a HELLO after %ss (%s), reattempting (%s)",
                self.shard_id, HELLO_TIMEOUT, e, attempt,
            )
            await self.close(code=0)
            return await self._connect(
                ws_url=ws_url,
                resume=resume,
                attempt=attempt + 1,
            )

        # Failed to get READY/RESUMED in time
        except AssertionError:
            log.debug(
                "[%s] Failed to get a READY from the gateway after 60s; reattempting connect (%s)",
                self.shard_id, attempt,
            )
            await self.close(code=0)

            if resume and attempt >= 3:
                log.debug(
                    "[%s] Resume timed out repeatedly; falling back to fresh IDENTIFY",
                    self.shard_id,
                )
                self.session_id = None
                self.sequence = None
                self.resume_url = self.ws_url
                return await self._connect(
                    ws_url=self.ws_url,
                    resume=False,
                    attempt=1,
                )
            return await self._connect(
                ws_url=ws_url,
                resume=resume,
                attempt=attempt + 1,
            )

        # Failed to connect due to invalid session
        except GatewayReconnectRequired as e:
            await self.close(code=0)
            await asyncio.sleep(5)

            return await self._connect(
                ws_url=e.ws_url,
                resume=e.resume,
                attempt=attempt + 1,
            )

        # All other unhandled errors
        except Exception as e:
            log.debug(
                "[%s] Hit generic exception during connect (%s), reattempting (%s)",
                self.shard_id, e, attempt,
            )
            await self.close(code=0)
            return await self._connect(
                ws_url=ws_url,
                resume=resume,
                attempt=attempt + 1,
            )

    async def send_resume_identify(self, resume: bool = False) -> None:
        """
        Send the RESUME/IDENTIFY payload to Discord and wait for a response.
        """

        self.connecting.set()
        self.ready_received.clear()
        self.invalid_session_received.clear()
        self.invalid_session_resumable = None

        self.state = "Pending send IDENTIFY/RESUME"
        async with self.identify_semaphore:
            self.state = "Sending IDENTIFY/RESUME"
            if resume:
                await self.resume()
            else:
                await self.identify()

            # Wait for a ready or resume
            log.debug("[%s] Waiting for READY/RESUMED or INVALID_SESSION", self.shard_id)
            self.state = "Waiting for READY/RESUMED"

            ready_task = asyncio.create_task(self.ready_received.wait())
            invalid_task = asyncio.create_task(self.invalid_session_received.wait())

            try:
                done, _ = await asyncio.wait(
                    {ready_task, invalid_task},
                    timeout=60.0,
                    return_when=asyncio.FIRST_COMPLETED,
                )
                if not done:
                    raise asyncio.TimeoutError
                if invalid_task in done:
                    resumable = bool(self.invalid_session_resumable)
                    raise GatewayInvalidSession(resumable)
                # Otherwise READY/RESUMED happened.
            finally:
                for task in (ready_task, invalid_task):
                    if not task.done():
                        task.cancel()

        self.state = "Ready"
        self.connecting.clear()

    async def close(self, code: int = 1_000) -> None:
        """
        Close the gateway connection, cancelling the heartbeat task.

        Everything in here has a timeout of 1 second.
        """

        if any((
                self.heartbeat_task is not None,
                self.message_task is not None,
                self.socket and not self.socket.closed)):
            log.info("[%s] Closing shard connection", self.shard_id)

        tasks_to_cancel = [
            task
            for task in (self.heartbeat_task, self.message_task)
            if task is not None
            and not task.done()
            and task is not asyncio.current_task()
        ]

        for task in tasks_to_cancel:
            task.cancel()
        if tasks_to_cancel:
            await asyncio.gather(*tasks_to_cancel, return_exceptions=True)

        if self.socket and not self.socket.closed:
            try:
                await asyncio.wait_for(self.socket.close(code=code), timeout=1.0)
            except asyncio.TimeoutError:
                pass
        self.state = "Closed"

    async def heartbeat(
            self,
            heartbeat_interval: int | float,
            *,
            jitter: bool = False,
            skip_first_wait: bool = False) -> None:
        """
        Send heartbeats to Discord. This implements a forever loop, so the
        method should be created as a task.
        """

        if heartbeat_interval <= 0:
            raise ValueError("Heartbeat interval cannot be below 0")
        wait = heartbeat_interval
        if jitter:
            wait = heartbeat_interval * random.random()
            log.debug(
                (
                    "[%s] Starting heartbeat - initial %ss, "
                    "normally %ss"
                ),
                self.shard_id, format(wait / 1e3, ".2f"),
                format(heartbeat_interval / 1e3, ".2f"),
            )
        else:
            log.debug(
                "[%s] Starting heartbeat at %ss",
                self.shard_id, format(heartbeat_interval / 1e3, ".2f"),
            )
        while True:
            try:
                if not skip_first_wait:
                    await asyncio.sleep(wait / 1e3)
                skip_first_wait = False
            except asyncio.CancelledError:
                log.debug("[%s] Heartbeat has been cancelled", self.shard_id)
                return
            for beat_attempt in range(1_000):
                try:
                    self.heartbeat_received.clear()
                    await self.send(GatewayOpcode.HEARTBEAT, self.sequence)
                    await asyncio.wait_for(self.heartbeat_received.wait(), timeout=10)
                except asyncio.CancelledError:
                    log.debug("[%s] Heartbeat has been cancelled", self.shard_id)
                    return
                except asyncio.TimeoutError:
                    if beat_attempt <= 5:
                        log.debug(
                            (
                                "[%s] Failed to get a response to heartbeat "
                                "(attempt %s) - trying again"
                            ),
                            self.shard_id, beat_attempt,
                        )
                        continue
                    log.debug(
                        (
                            "[%s] Failed to get a response to heartbeat "
                            "(attempt %s) - reconnecting"
                        ),
                        self.shard_id, beat_attempt,
                    )
                    self.reconnect(resume=True)
                    return
                except ValueError:
                    log.debug(
                        (
                            "[%s] Socket closed so could not send heartbeat - "
                            "reconnecting"
                        ),
                        self.shard_id,
                    )
                    self.reconnect(resume=True)
                    return
                else:
                    break
            wait = heartbeat_interval

    async def identify(self) -> None:
        """
        Send an identify to Discord.
        """

        log.debug("[%s] Sending identify", self.shard_id)
        token = cast(str, self.parent._token)
        await self.send(
            GatewayOpcode.IDENTIFY,
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

        log.debug("[%s] Chunking guild %s", self.shard_id, guild_id)
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
            GatewayOpcode.REQUEST_MEMBERS,
            data,
        )
        return event

    async def resume(self) -> None:
        """
        Send a resume to Discord.
        """

        log.debug("[%s] Sending resume", self.shard_id)
        token = cast(str, self.parent._token)
        await self.send(
            GatewayOpcode.RESUME,
            {
                "token": token,
                "session_id": self.session_id,
                "seq": self.sequence,
            },
        )

    async def change_presence(
            self,
            activities: list[Activity],
            status: str) -> None:
        """
        Change the presence of the client.

        Parameters
        ----------
        activities : list[novus.Activity]
            The activities that you want to set the client as displaying.
        status : str
            The status of the client.

            .. seealso:: `novus.Status`
        """

        if self.socket is None or self.socket.closed or not self.ready_received.is_set():
            log.debug("[%s] Not sending change presence (not yet READY)", self.shard_id)
            return
        log.debug("[%s] Sending change presence", self.shard_id)
        await self.send(
            GatewayOpcode.PRESENCE,
            {
                "activities": [i._to_data() for i in activities],
                "status": status,
                "since": None,
                "afk": False,
            },
        )

    async def handle_dispatch(self, event_name: str, message: dict) -> None:
        try:
            await self.dispatch.handle_dispatch(event_name, message)
        except Exception as e:
            log.error(
                "Error in dispatch (%s) (%e) (%s)", event_name, e, dump(message),
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
                case GatewayOpcode.HEARTBEAT_ACK:
                    self.heartbeat_received.set()

                # Sometimes Discord may ask for heartbeats explicitly
                case GatewayOpcode.HEARTBEAT:
                    if self.heartbeat_task:
                        self.heartbeat_task.cancel()
                    self.heartbeat_task = asyncio.create_task(
                        self.heartbeat(self.heartbeat_interval, skip_first_wait=True),
                        name="Heartbeat for shard %s" % self.shard_id,
                    )

                # Deal with dispatch
                case GatewayOpcode.DISPATCH:
                    event_name = cast(str, event_name)
                    sequence = cast(int, sequence)
                    if event_name == "READY" or event_name == "RESUMED":
                        log.info("[%s] Shard %s", self.shard_id, event_name)
                        self.ready_received.set()
                    self.sequence = sequence
                    t = asyncio.create_task(
                        self.handle_dispatch(event_name, message),
                        name="Dispatch handler for sequence %s" % sequence
                    )
                    self.running_tasks.add(t)
                    t.add_done_callback(self.running_tasks.discard)

                # Deal with reconnects
                case GatewayOpcode.RECONNECT:
                    self.reconnect()
                    return

                # Deal with invalid sesions
                case GatewayOpcode.INVALIDATE_SESSION:
                    resumable = bool(message)
                    log.info(
                        "[%s] Session invalidated (resumable: %s)",
                        self.shard_id,
                        str(resumable).lower(),
                    )
                    self.invalid_session_resumable = resumable
                    self.invalid_session_received.set()
                    return

                # Everything else
                case _:
                    log.warning("Failed to deal with gateway message %s" % dump(message))
