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

from datetime import datetime as dt
from typing import TYPE_CHECKING, Any, TypeAlias

from ....utils import MISSING

if TYPE_CHECKING:
    import io

    from ....enums import EventEntityType, EventPrivacyLevel, EventStatus
    from ... import ScheduledEvent
    from ...abc import Snowflake, StateSnowflake

    FileT: TypeAlias = str | bytes | io.IOBase


class GuildEventAPI:

    async def fetch_scheduled_events(
            self: StateSnowflake,
            *,
            with_user_count: bool = False) -> list[ScheduledEvent]:
        """
        Get a list of all of the scheduled events for a guild.

        .. seealso:: :func:`novus.ScheduledEvent.fetch_all_for_guild`

        Parameters
        ----------
        with_user_count : bool
            Whether or not to include the event's user count.

        Returns
        -------
        list[novus.ScheduledEvent]
            The scheduled events for the guild.
        """

        return await self.state.guild_scheduled_event.list_scheduled_events_for_guild(
            self.id,
            with_user_count=with_user_count,
        )

    async def create_scheduled_event(
            self: StateSnowflake,
            *,
            name: str,
            start_time: dt,
            entity_type: EventEntityType,
            privacy_level: EventPrivacyLevel,
            reason: str | None = None,
            channel: int | Snowflake | None = MISSING,
            location: str = MISSING,
            end_time: dt = MISSING,
            description: str | None = MISSING,
            status: EventStatus = MISSING,
            image: str | bytes | io.IOBase | None = MISSING) -> ScheduledEvent:
        """
        Create a new scheduled event.

        .. seealso:: :func:`novus.ScheduledEvent.create`

        Parameters
        ----------
        name : str
            The name of the event.
        start_time : datetime.datetime
            The time to schedule the event start.
        entity_type : novus.EventEntityType
            The type of the event.
        privacy_level : novus.EventPrivacyLevel
            The privacy level of the event.
        channel : int | Snowflake | None
            The channel of the scheduled event. Set to ``None`` if the event
            type is being set to external.
        location : str
            The location of the event.
        end_time : datetime.datetime
            The time to schedule the event end.
        description : str | None
            The description of the event.
        status : novus.EventStatus
            The status of the event.
        image : str | bytes | io.IOBase | None
            The cover image of the scheduled event.
        reason : str | None
            The reason shown in the audit log.

        Returns
        -------
        novus.ScheduledEvent
            The new scheduled event.
        """

        update: dict[str, Any] = {}
        if channel is not MISSING:
            update['channel'] = channel
        if location is not MISSING:
            update['location'] = location
        if name is not MISSING:
            update['name'] = name
        if privacy_level is not MISSING:
            update['privacy_level'] = privacy_level
        if start_time is not MISSING:
            update['start_time'] = start_time
        if end_time is not MISSING:
            update['end_time'] = end_time
        if description is not MISSING:
            update['description'] = description
        if entity_type is not MISSING:
            update['entity_type'] = entity_type
        if status is not MISSING:
            update['status'] = status
        if image is not MISSING:
            update['image'] = image

        return await self.state.guild_scheduled_event.create_guild_scheduled_event(
            self.id,
            **update,
            reason=reason,
        )
