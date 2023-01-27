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

if TYPE_CHECKING:
    from ..audit_log import AuditLog
    from ...api import HTTPConnection
    from ...enums import AuditLogEventType


class AuditLogAPIMixin:

    @classmethod
    async def fetch(
            cls,
            state: HTTPConnection,
            guild_id: int,
            *,
            user_id: int | None = None,
            action_type: AuditLogEventType | None = None,
            before: int | None = None,
            after: int | None = None,
            limit: int = 50) -> AuditLog:
        """
        Get an instance of a user from the API.

        Parameters
        ----------
        state : HTTPConnection
            The API connection.
        guild_id : int
            The ID associated with the user you want to get.
        user_id: int | None
            The ID of the moderator you want to to filter by.
        action_type: AuditLogEventType | None
            The ID of an action to filter by.
        before: int | None
            The snowflake before which to get entries.
        after: int | None
            The snowflake after which to get entries.
        limit: int
            The number of entries to get. Max 100, defaults to 50.

        Returns
        -------
        novus.models.AuditLog
            The audit log for the guild.
        """

        return await state.audit_log.get_guild_audit_log(
            guild_id,
            user_id=user_id,
            action_type=action_type,
            before=before,
            after=after,
            limit=limit,
        )
