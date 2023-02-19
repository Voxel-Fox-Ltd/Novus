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

from typing import TYPE_CHECKING, TypeAlias

if TYPE_CHECKING:
    import io

    from ....enums import AuditLogEventType
    from ... import AuditLog
    from ...abc import StateSnowflake

    FileT: TypeAlias = str | bytes | io.IOBase


class GuildAuditAPI:

    async def fetch_audit_logs(
            self: StateSnowflake,
            *,
            user_id: int | None = None,
            action_type: AuditLogEventType | None = None,
            before: int | None = None,
            after: int | None = None,
            limit: int = 50) -> AuditLog:
        """
        Get the audit logs for the guild.

        Parameters
        ----------
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
        novus.AuditLog
            The audit log for the guild.
        """

        return await self.state.audit_log.get_guild_audit_log(
            self.id,
            user_id=user_id,
            action_type=action_type,
            before=before,
            after=after,
            limit=limit,
        )
