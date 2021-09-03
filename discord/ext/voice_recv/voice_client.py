import typing
import threading

import discord
from discord.gateway import DiscordVoiceWebSocket

from .gateway import hook
from .reader import AudioReader, AudioSink

if typing.TYPE_CHECKING:
    from ...types.voice import (
        GuildVoiceState as GuildVoiceStatePayload,
    )


class VoiceReceiveClient(discord.VoiceClient):

    def __init__(self, client: discord.Client, channel: discord.VoiceChannel):
        super().__init__(client, channel)
        self._connecting: threading.Condition = threading.Condition()
        self._reader: typing.Optional[AudioReader] = None
        self._ssrc_to_id: typing.Dict[str, int] = {}  # speaking source -> user id
        self._id_to_ssrc: typing.Dict[int, str] = {}  # user id -> speaking source

    async def on_voice_state_update(self, data: GuildVoiceStatePayload):
        await super().on_voice_state_update(data)

        channel_id = discord.utils._get_as_snowflake(data, 'channel_id')
        user_id = discord.utils._get_as_snowflake(data, 'user_id')
        assert user_id  # it WILL be defined

        # Someone moved channels
        if channel_id and channel_id != self.channel.id and self._reader:

            # It was us
            if self._state.user.id == user_id:
                self.stop_listening()

            # It was someone else
            # else:
            #     ssrc, _ = self._get_ssrc_mapping(user_id=user_id)
            #     for reader in self._readers:
            #         reader._reset_decoders(ssrc)

    def cleanup(self):
        super().cleanup()
        self.stop()

    def _add_ssrc(self, user_id: int, ssrc: str) -> None:
        self._ssrc_to_id[ssrc] = user_id
        self._id_to_ssrc[user_id] = ssrc

    def _remove_ssrc(self, *, user_id: int) -> None:
        ssrc = self._id_to_ssrc.pop(user_id, None)
        if ssrc:
            self._ssrc_to_id.pop(ssrc, None)

    def _get_ssrc_mapping(
            self, *, ssrc: str = None,
            user_id: int = None) -> typing.Tuple[typing.Optional[str], typing.Optional[int]]:
        if ssrc is None and user_id is None:
            raise ValueError("You need to set either one of user_id and ssrc")
        if ssrc is not None and user_id is not None:
            raise ValueError("You can't set both user_id and ssrc")

        if ssrc:
            return ssrc, self._ssrc_to_id.get(ssrc)
        elif user_id:
            return self._id_to_ssrc.get(user_id), user_id
        else:
            return None, None

    def add_sink(self, sink: AudioSink) -> None:
        """Add a sink to the current audio reader instance.

        Parameters
        ----------
        :class:`AudioSink`
            The sink that you want to add.
        """

        if not isinstance(sink, AudioSink):
            raise TypeError('sink must be an AudioSink not {0.__class__.__name__}'.format(sink))
        if self._reader is None:
            self._reader = AudioReader(self)
        self._reader.add_sink(sink)

    def listen(self) -> None:
        """
        Receives audio into a :class:`AudioSink`.
        """

        if not self.is_connected():
            raise discord.ClientException('Not connected to voice.')
        if self._reader is None or not self._reader.sinks:
            raise discord.ClientException("No audio sinks are currently set.")
        if self.is_listening():
            raise discord.ClientException('Already receiving audio.')

        if self._reader is None:
            self._reader = AudioReader(self)
        self._reader.run()

    def is_listening(self) -> bool:
        """
        Indicates if any of the readers are currently listening to any audio.
        """

        return self._reader is not None and self._reader.is_listening()

    def stop_listening(self) -> None:
        """
        Stops receiving audio.
        """

        if self._reader:
            self._reader.stop()
            self._reader = None

    def stop_playing(self) -> None:
        """
        Stops playing audio.
        """

        if self._player:
            self._player.stop()
            self._player = None

    def stop(self) -> None:
        """
        Stops playing and receiving audio.
        """

        self.stop_playing()
        self.stop_listening()
