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

from typing import TYPE_CHECKING

from typing_extensions import Self

from ..utils import DiscordDatetime, parse_timestamp
from .abc import Hashable
from .channel import Channel
from .guild_member import GuildMember

if TYPE_CHECKING:
    from .. import payloads
    from ..api import HTTPConnection
    from .guild import Guild

__all__ = (
    'VoiceState',
)


class VoiceState(Hashable):
    """
    The voice state associated with a user.

    Attributes
    ----------
    guild : novus.Guild | None
        The guild that the voice state is attached to.
    channel : novus.Channel | None
        The channel associated with the voice state.
    user : novus.GuildMember | User
        The user associated with the voice state.
    suppress : bool
    session_id : str
    self_video : bool
        Whether the user has video enabled.
    self_mute : bool
        Whether the user has muted themselves.
    self_deaf : bool
        Whether the user has deafened themselves.
    request_to_speak_timestamp : novus.utils.DiscordDatetime | None
        When the user requested to speak.
    mute : bool
        Whether the user is muted.
    deaf : bool
        Whether the user is deafened.
    """

    suppress: bool
    session_id: str
    self_video: bool
    self_mute: bool
    self_deaf: bool
    request_to_speak_timestamp: DiscordDatetime | None
    mute: bool
    deaf: bool

    def __init__(
            self,
            *,
            state: HTTPConnection,
            data: payloads.VoiceState,
            guild_id: int | None = None) -> None:
        self.state = state
        self._user_id = data["user_id"]
        if guild_id:
            self._guild_id = guild_id
        else:
            self._guild_id = data["guild_id"]
        self._update(data)

    @property
    def channel(self) -> Channel:
        return self.state.cache.get_channel(self._channel_id)

    @property
    def guild(self) -> Guild:
        return self.state.cache.get_guild(self._guild_id)

    @property
    def user(self) -> GuildMember:
        return self.guild.get_member(self._user_id)

    def _update(self, data: payloads.VoiceState) -> Self:
        if "member" in data:
            self.user._update(data["member"])
        self._channel_id = data["channel_id"]
        self.suppress = data.get("suppress", False)
        self.self_video = data.get("self_video", False)
        self.self_mute = data.get("self_mute", False)
        self.self_deaf = data.get("self_deaf", False)
        self.request_to_speak_timestamp = parse_timestamp(data.get("request_to_speak_timestamp"))
        self.mute = data.get("mute", False)
        self.deaf = data.get("deaf", False)
        self.guild._add_voice_state(self)
        return self
