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

from typing import TYPE_CHECKING, Any

from ..models import AuditLog, Object
from ._route import Route

if TYPE_CHECKING:
    from .. import payloads
    from ._http import HTTPConnection

__all__ = (
    'AuditLogHTTPConnection',
)


class AuditLogHTTPConnection:

    def __init__(self, parent: HTTPConnection):
        self.parent = parent

    async def get_guild_audit_log(
            self,
            guild_id: int,
            *,
            user_id: int | None = None,
            action_type: int | None = None,
            before: int | None = None,
            after: int | None = None,
            limit: int = 50) -> AuditLog:
        """
        Get guild audit logs.
        """

        params: dict[str, Any] = {}
        params['limit'] = limit

        if user_id is not None:
            params['user_id'] = user_id
        if action_type is not None:
            params['action_type'] = action_type
        if before is not None:
            params['before'] = before
        if after is not None:
            params['after'] = after
        
        route = Route(
            "GET",
            "/guilds/{guild_id}/audit-logs",
            guild_id=guild_id,
        )
        data: payloads.AuditLog = await self.parent.request(
            route,
            params=params,
        )
        guild = Object(guild_id, state=self.parent)
        return AuditLog(data=data, state=self.parent, guild=guild)
