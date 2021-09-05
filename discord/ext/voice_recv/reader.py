"""
The MIT License (MIT)

Copyright (c) 2015-2021 Rapptz, 2021-present Kae Bartlett

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

import time
import wave
import bisect
import select
import socket
import audioop
import logging
import threading
import typing

import discord

from .common import rtp
from .common.utils import DefaultDict
from .common.rtp import SilencePacket, RTPPacket
from .common.opus import Decoder
from ...errors import DiscordException, ClientException

try:
    import nacl.secret
    from nacl.exceptions import CryptoError
except ImportError:
    pass

if typing.TYPE_CHECKING:
    from .voice_client import VoiceReceiveClient


log = logging.getLogger(__name__)

__all__ = (
    'AudioSink',
    'BasicSink',
    'AudioReader',
)


class SinkExit(DiscordException):
    """A signal type exception (like ``GeneratorExit``) to raise in a Sink's write() method to stop it.

    TODO: make better words

    Parameters
    -----------
    drain: :class:`bool`
        ...
    flush: :class:`bool`
        ...
    """

    def __init__(self, *, drain: bool = True, flush: bool = False):
        self.drain: bool = drain
        self.flush: bool = flush


class VoicePayload:

    __slots__ = ('data', 'user', 'packet')

    def __init__(self, data: bytes, user: discord.User, packet):
        self.data: bytes = data
        self.user: discord.User = user
        self.packet = packet


class AudioSink:
    """
    A base class for handling bytes received.
    """

    def __del__(self):
        self.cleanup()

    def write(self, data: VoicePayload) -> None:
        raise NotImplementedError()

    def wants_opus(self) -> bool:
        return False

    def cleanup(self) -> None:
        pass


class WaveSink(AudioSink):

    def __init__(self, destination: str):
        self._file: wave.Wave_write = wave.open(destination, 'wb')
        self._file.setnchannels(Decoder.CHANNELS)
        self._file.setsampwidth(Decoder.SAMPLE_SIZE // Decoder.CHANNELS)
        self._file.setframerate(Decoder.SAMPLING_RATE)

    def write(self, data: VoicePayload) -> None:
        self._file.writeframes(data.data)

    def cleanup(self) -> None:
        try:
            self._file.close()
        except:
            pass


class BasicSink(AudioSink):

    def __init__(self, event, *, rtcp_event=lambda _: None):
        self.on_voice_packet = event
        self.on_voice_rtcp_packet = rtcp_event


# I need some sort of filter sink with a predicate or something
# Which means I need to sort out the write() signature issue
# Also need something to indicate a sink is "done", probably
# something like raising an exception and handling that in the write loop
# Maybe should rename some of these to Filter instead of Sink


class AudioFilter(AudioSink):
    pass


class PCMVolumeTransformerFilter(AudioFilter):

    def __init__(self, destination, volume: float = 1.0):
        if not isinstance(destination, AudioSink):
            raise TypeError('expected AudioSink or AudioFilter not {0.__class__.__name__}.'.format(destination))
        if destination.wants_opus():
            raise ClientException('AudioSink must not request Opus encoding.')
        self.destination: AudioSink = destination
        setattr(self, "volume", volume)

    @property
    def volume(self) -> float:
        """
        Retrieves or sets the volume as a floating point percentage (e.g. 1.0 for 100%).
        """

        return self._volume

    @volume.setter
    def volume(self, value: float):
        self._volume = max(value, 0.0)

    def write(self, data: VoicePayload):
        changed_bytes = audioop.mul(data.data, 2, min(self._volume, 2.0))
        new_data = VoicePayload(changed_bytes, data.user, data.packet)
        self.destination.write(new_data)


class ConditionalFilter(AudioFilter):

    def __init__(self, destination: AudioSink, predicate: typing.Callable[[VoicePayload], bool]):
        self.destination: AudioSink = destination
        self.predicate: typing.Callable[[VoicePayload], bool] = predicate

    def write(self, data: VoicePayload) -> None:
        if self.predicate(data):
            self.destination.write(data)


class TimedFilter(ConditionalFilter):

    def __init__(self, destination: AudioSink, duration: float, *, start_on_init: bool = False):
        super().__init__(destination, self._predicate)
        self.duration: float = duration
        self.start_time: typing.Optional[float]
        if start_on_init:
            self.start_time = self.get_time()
        else:
            self.start_time = None
            self.write = self._write_once

    def _write_once(self, data):
        self.start_time = self.get_time()
        super().write(data)
        self.write = super().write

    def _predicate(self, data: VoicePayload) -> bool:
        return self.start_time is not None and self.get_time() - self.start_time < self.duration

    def get_time(self) -> float:
        return time.time()


class UserFilter(ConditionalFilter):

    def __init__(self, destination, user):
        super().__init__(destination, self._predicate)
        self.user = user

    def _predicate(self, data: VoicePayload) -> bool:
        return data.user == self.user


class _ReaderBase(threading.Thread):

    def __init__(self, client: VoiceReceiveClient, **kwargs):
        daemon = kwargs.pop('daemon', True)
        super().__init__(daemon=daemon, **kwargs)

        self.client: VoiceReceiveClient = client
        self.box = nacl.secret.SecretBox(bytes(client.secret_key))
        self.decrypt_rtp: typing.Callable[[RTPPacket], bytes] = getattr(self, '_decrypt_rtp_' + client.mode)
        self.decrypt_rtcp: typing.Callable[[bytes], bytes] = getattr(self, '_decrypt_rtcp_' + client.mode)

    def _decrypt_rtp_xsalsa20_poly1305(self, packet: RTPPacket) -> bytes:
        nonce = bytearray(24)
        nonce[:12] = packet.header
        result: bytes = self.box.decrypt(bytes(packet.data), bytes(nonce))

        if packet.extended:
            offset = packet.update_ext_headers(result)
            result = result[offset:]
        return result

    def _decrypt_rtcp_xsalsa20_poly1305(self, data: bytes) -> bytes:
        nonce = bytearray(24)
        nonce[:8] = data[:8]
        result = self.box.decrypt(data[8:], bytes(nonce))
        return data[:8] + result

    def _decrypt_rtp_xsalsa20_poly1305_suffix(self, packet: RTPPacket) -> bytes:
        nonce = packet.data[-24:]
        voice_data = packet.data[:-24]
        result = self.box.decrypt(bytes(voice_data), bytes(nonce))

        if packet.extended:
            offset = packet.update_ext_headers(result)
            result = result[offset:]
        return result

    def _decrypt_rtcp_xsalsa20_poly1305_suffix(self, data: bytes) -> bytes:
        nonce = data[-24:]
        header = data[:8]
        result = self.box.decrypt(data[8:-24], nonce)
        return header + result

    def _decrypt_rtp_xsalsa20_poly1305_lite(self, packet: RTPPacket) -> bytes:
        nonce = bytearray(24)
        nonce[:4] = packet.data[-4:]
        voice_data = packet.data[:-4]
        result = self.box.decrypt(bytes(voice_data), bytes(nonce))

        if packet.extended:
            offset = packet.update_ext_headers(result)
            result = result[offset:]
        return result

    def _decrypt_rtcp_xsalsa20_poly1305_lite(self, data: bytes) -> bytes:
        nonce = bytearray(24)
        nonce[:4] = data[-4:]
        header = data[:8]
        result = self.box.decrypt(data[8:-4], bytes(nonce))
        return header + result

    def run(self):
        raise NotImplementedError


class AudioReader(_ReaderBase):
    """
    An audio reader for handling receiving voice packet data.
    """

    def __init__(
            self, client: VoiceReceiveClient, *,
            after: typing.Optional[typing.Callable[[typing.Optional[Exception]], None]] = None):
        if after is not None and not callable(after):
            raise TypeError('Expected a callable for the "after" parameter.')

        super().__init__(client)

        self.sinks: typing.List[AudioSink] = list()
        self.client: VoiceReceiveClient = client
        self.after: typing.Optional[typing.Callable[[typing.Optional[Exception]], None]] = after

        self._current_error: typing.Optional[Exception] = None
        self._end: threading.Event = threading.Event()
        self._noop = lambda *_: None

    def add_sink(self, sink: AudioSink) -> None:
        """
        Add a sink to the reader's sink list.

        Parameters
        ----------
        :class:`AudioSink`
            The sink that you want to add.
        """

        self.sinks.append(sink)

    @property
    def connected(self) -> threading.Event:
        """
        Returns
        --------
        :class:`threading.Event`
            The connected event.
        """

        return self.client._connected

    def dispatch(self, event: str, *args):
        """
        Dispatch an event.
        """

        runnable: typing.Callable[..., None]
        for sink in self.sinks:
            runnable = getattr(sink, f"on_{event}", self._noop)
            runnable(*args)

    def _get_user(self, packet: RTPPacket) -> typing.Optional[typing.Union[discord.User, discord.Member]]:
        """
        Get the user object associated with an RTPPacket.
        """

        _, user_id = self.client._get_ssrc_mapping(ssrc=packet.ssrc)
        if self.client.guild and user_id:
            return self.client.guild.get_member(user_id)
        return None

    def _do_run(self):

        # Run until we're told to end
        while not self._end.is_set():

            # Wait until we're connected
            if not self.connected.is_set():
                self.connected.wait()

            # Wait for the socket to be readable
            ready, _, err = select.select(
                [self.client.socket], [], [self.client.socket], 0.01,
            )
            if not ready:
                if err:
                    log.error("Socket error")
                continue

            # Read from the socket
            try:
                raw_data: bytes = self.client.socket.recv(2 ** 12)
            except socket.error as e:

                # We're connecting to a socket that isn't a socket? Wild.
                if e.errno == 10038:  # ENOTSOCK
                    continue

                log.error("Socket error in reader thread", exc_info=e)

                # We timed out - let's reconnect
                with self.client._connecting:
                    timed_out = self.client._connecting.wait(20)

                # Make sure our connect didn't time out and continue
                if not timed_out:
                    raise
                elif self.client.is_connected():
                    continue
                else:
                    raise

            # Parse our data packet
            packet: typing.Optional[RTPPacket] = None
            try:

                # Make sure the data isn't RTCP
                if not rtp.is_rtcp(raw_data):
                    packet = rtp.decode(raw_data)
                    packet.decrypted_data = self.decrypt_rtp(packet)

                # If it is, decode and dispatch that elseshere
                else:
                    packet = rtp.decode(self.decrypt_rtcp(raw_data))
                    # if not isinstance(packet, rtp.ReceiverReportPacket):
                    #     pass
                    self.dispatch('voice_rtcp_packet', packet)
                    continue
            except CryptoError:
                log.exception("CryptoError decoding packet %s", packet)
                continue
            except:
                log.exception("Error unpacking packet", exc_info=True)

            # Dispatch our packet data
            if packet is None:
                continue
            if packet.ssrc not in self.client._ssrc_to_id:
                log.debug("Received packet for unknown ssrc %s", packet.ssrc)
            self.dispatch('voice_packet', self._get_user(packet), packet)

    def is_listening(self) -> bool:
        """
        Returns
        --------
        :class:`bool`
            Whether or not hte listener is currently listening.
        """

        return not self._end.is_set()

    def stop(self):
        """
        Stop reading on the voice socket.
        """

        self._end.set()

    def run(self):
        """
        Run the listener loop.
        """

        try:
            self._do_run()
        except socket.error as exc:
            self._current_error = exc
            self.stop()
        except Exception as exc:
            log.error("Hit error running thread", exc_info=exc)
            self._current_error = exc
            self.stop()
        finally:
            self._call_after()

    def _call_after(self):
        if self.after is not None:
            try:
                self.after(self._current_error)
            except Exception:
                log.exception('Calling the after function failed.', exc_info=True)


class SimpleJitterBuffer:
    """
    Push item in, returns as many contiguous items as possible.
    """

    def __init__(self, maxsize=10, *, prefill=0):
        if maxsize < 1:
            raise ValueError('maxsize must be greater than 0')

        self.maxsize = maxsize
        self.prefill = prefill
        self._last_seq = 0
        self._buffer = []

    def push(self, item):
        if item.sequence <= self._last_seq and self._last_seq:
            return []

        bisect.insort(self._buffer, item)

        if self.prefill > 0:
            self.prefill -= 1
            return []

        return self._get_ready_batch()

    def _get_ready_batch(self):
        if not self._buffer or self.prefill > 0:
            return []

        if not self._last_seq:
            self._last_seq = self._buffer[0].sequence - 1

        # check to see if the next packet is the next one
        if self._last_seq + 1 == self._buffer[0].sequence:

            # Check for how many contiguous packets we have
            n = ok = 0
            for n in range(len(self._buffer)): # TODO: enumerate
                if self._last_seq + n + 1 != self._buffer[n].sequence:
                    break
                ok = n + 1

            # slice out the next section of the buffer
            segment = self._buffer[:ok]
            self._buffer = self._buffer[ok:]
            if segment:
                self._last_seq = segment[-1].sequence

            return segment

        # size check and add skips as None
        if len(self._buffer) > self.maxsize:
            buf = [None for _ in range(self._buffer[0].sequence-self._last_seq-1)]
            self._last_seq = self._buffer[0].sequence - 1
            buf.extend(self._get_ready_batch())
            return buf

        return []