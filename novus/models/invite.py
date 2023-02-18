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

from typing import TYPE_CHECKING

from ..models.channel import channel_builder
from ..utils import generate_repr, parse_timestamp
from .api_mixins.invite import InviteAPIMixin
from .guild import PartialGuild

if TYPE_CHECKING:
    from datetime import datetime as dt

    from ..api import HTTPConnection
    from ..payloads import InviteWithMetadata as InviteMetadataPayload
    from . import Channel, Guild
    from . import api_mixins as amix

__all__ = (
    'Invite',
)


class Invite(InviteAPIMixin):
    """
    A model representing a guild invite.

    Attributes
    ----------
    code : str
        The code associated with the invite.
    channel : novus.Channel | None
        The channel that the invite leads to.
    uses : int | None
        How many times the invite has been used.
    max_uses : int | None
        The maximum number of times the invite can be used.
    max_age : int | None
        Duration (in seconds) after which the invite expires.
    temporary : bool | None
        Whether the invite only grants temporary membership.
    created_at : datetime.datetime | None
        The time that the invite was created.
    guild : novus.PartialGuild | None
        The guild that the invite leads to. Could be ``None`` if the invite
        leads to a group DM.
    """

    code: str
    channel: Channel | None
    uses: int | None
    max_uses: int | None
    max_age: int | None
    temporary: bool | None
    created_at: dt | None
    guild: Guild | amix.GuildAPIMixin | None

    def __init__(self, *, state: HTTPConnection, data: InviteMetadataPayload):
        self._state = state
        self.code = data['code']
        self.channel = None
        self.uses = data.get('uses')
        self.max_uses = data.get('max_uses')
        self.max_age = data.get('max_age')
        self.temporary = data.get('temporary')
        self.created_at = parse_timestamp(data.get('created_at'))
        self.guild = None
        if "guild" in data:
            if cached := self._state.cache.get_guild(data["guild"]["id"], or_object=False):
                self.guild = cached
            else:
                self.guild = PartialGuild(state=self._state, data=data['guild'])
        channel = data.get('channel')
        if channel:
            if cached := self._state.cache.get_channel(channel["id"], or_object=False):
                self.channel = cached
            else:
                guild_id = None
                if self.guild:
                    guild_id = self.guild.id
                self.channel = channel_builder(state=self._state, data=channel, guild_id=guild_id)

    __repr__ = generate_repr(('code', 'channel', 'guild',))
