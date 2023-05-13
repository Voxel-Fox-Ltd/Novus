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

from ..utils import parse_timestamp
from .guild_member import GuildMember
from .mixins import Hashable

if TYPE_CHECKING:
    from datetime import datetime as dt

    from .. import Guild, GuildVoiceChannel, User, payloads
    from ..api import HTTPConnection
    from . import api_mixins as amix

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
    request_to_speak_timestamp : dt | None
        When the user requested to speak.
    mute : bool
        Whether the user is muted.
    deaf : bool
        Whether the user is deafened.
    """

    guild: Guild | amix.GuildAPIMixin | None
    channel: GuildVoiceChannel
    user: GuildMember | User | amix.UserAPIMixin
    suppress: bool
    session_id: str
    self_video: bool
    self_mute: bool
    self_deaf: bool
    request_to_speak_timestamp: dt | None
    mute: bool
    deaf: bool

    def __init__(
            self,
            *,
            state: HTTPConnection,
            data: payloads.VoiceState) -> None:
        self.state = state
        if "member" in data:
            guild_id = data["guild_id"]  # pyright: ignore
            self.user = GuildMember(
                state=self.state,
                data=data["member"],
                guild_id=guild_id,
            )
        else:
            self.user = self.state.cache.get_user(data["user_id"], or_object=True)
        self.guild = self.state.cache.get_guild(data.get("guild_id"), or_object=True)
        from .guild import Guild
        if isinstance(self.guild, Guild):
            self.guild._add_voice_state(self)
        self.channel = self.state.cache.get_channel(data["channel_id"], or_object=True)  # pyright: ignore
        self.suppress = data.get("suppress", False)
        self.session_id = data["session_id"]
        self.self_video = data.get("self_video", False)
        self.self_mute = data.get("self_mute", False)
        self.self_deaf = data.get("self_deaf", False)
        self.request_to_speak_timestamp = parse_timestamp(data.get("request_to_speak_timestamp"))
        self.mute = data.get("mute", False)
        self.deaf = data.get("deaf", False)
