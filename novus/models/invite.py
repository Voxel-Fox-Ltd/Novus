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

import re
from typing import TYPE_CHECKING, Protocol

from ..utils import generate_repr, parse_timestamp, DiscordDatetime
from .channel import Channel
from .guild import Guild, PartialGuild

if TYPE_CHECKING:
    from .. import payloads
    from ..api import HTTPConnection

__all__ = (
    'Invite',
)


class StateWithCode(Protocol):
    state: HTTPConnection
    code: str


class Invite:
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

    INVITE_LINK_REGEX = re.compile(r"(?:https?://)?discord\.gg/(?P<code>[a-zA-Z0-9]+)")

    code: str
    channel: Channel | None
    uses: int | None
    max_uses: int | None
    max_age: int | None
    temporary: bool | None
    created_at: DiscordDatetime | None
    guild: Guild | PartialGuild | None

    def __init__(self, *, state: HTTPConnection, data: payloads.InviteWithMetadata | payloads.Invite):
        self.state = state
        self.code = data['code']
        self.channel = None
        self.uses = data.get('uses')
        self.max_uses = data.get('max_uses')
        self.max_age = data.get('max_age')
        self.temporary = data.get('temporary')
        self.created_at = parse_timestamp(data.get('created_at'))
        self.guild = None
        if "guild" in data:
            if isinstance(cached := self.state.cache.get_guild(data["guild"]["id"]), Guild):
                self.guild = cached._update(data["guild"])
            else:
                self.guild = PartialGuild(state=self.state, data=data['guild'])
        channel = data.get('channel')
        if channel:
            if cached := self.state.cache.get_channel(channel["id"]):
                self.channel = cached._update(channel)
            else:
                guild_id = None
                if self.guild:
                    guild_id = self.guild.id
                self.channel = Channel(state=self.state, data=channel)

    __repr__ = generate_repr(('code', 'channel', 'guild',))

    # API methods

    @classmethod
    async def fetch(
            cls,
            state: HTTPConnection,
            code: str) -> Invite:
        """
        Get an invite object via its code.

        Parameters
        ----------
        state : HTTPConnection
            The API connection.
        code : str
            The invite code, or URL. If an invalid code/URL is given, this is
            still passed over to the API for it to reject. This *will*
            count towards your API limit.

        Returns
        -------
        novus.Invite
            The invite associated with the code.
        """

        # Try and parse a URL
        if "/" in code:
            match = cls.INVITE_LINK_REGEX.search(code)
            if match is not None:
                code = match.group("code")
            else:
                pass  # Could raise here, but I'd rather the API at this point

        # API request
        return await state.invite.get_invite(code)

    async def delete(
            self: StateWithCode,
            *,
            reason: str | None = None) -> Invite:
        """
        Delete an instance of the invite.

        Parameters
        ----------
        reason : str | None
            The reason shown in the audit log.

        Returns
        -------
        novus.Invite
            The deleted invite object.
        """

        return await self.state.invite.delete_invite(self.code, reason=reason)
