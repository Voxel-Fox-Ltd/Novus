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

from ..models import Invite
from ._route import Route

if TYPE_CHECKING:
    from .. import payloads
    from ._http import HTTPConnection

__all__ = (
    'InviteHTTPConnection',
)


class InviteHTTPConnection:

    def __init__(self, parent: HTTPConnection):
        self.parent = parent

    async def get_invite(
            self,
            invite_code: str,
            *,
            with_counts: bool | None = None,
            with_expiration: bool | None = None,
            guild_scheduled_event_id: int | None = None) -> Invite:
        """
        Get an invite from the API.
        """

        route = Route(
            "GET",
            "/invites/{invite_code}",
            invite_code=invite_code,
        )

        params: dict[str, str] = {}
        if with_counts is not None:
            params['with_counts'] = str(with_counts).lower()
        if with_expiration is not None:
            params['with_expiration'] = str(with_expiration).lower()
        if guild_scheduled_event_id is not None:
            params['guild_scheduled_event_id'] = str(guild_scheduled_event_id)

        data: payloads.InviteWithMetadata = await self.parent.request(
            route,
            params=params,
        )
        return Invite(state=self.parent, data=data)

    async def delete_invite(
            self,
            invite_code: str,
            *,
            reason: str | None = None) -> Invite:
        """
        Get an invite from the API.
        """

        route = Route(
            "DELETE",
            "/invites/{invite_code}",
            invite_code=invite_code,
        )
        data: payloads.InviteWithMetadata = await self.parent.request(
            route,
            reason=reason,
        )
        return Invite(state=self.parent, data=data)
