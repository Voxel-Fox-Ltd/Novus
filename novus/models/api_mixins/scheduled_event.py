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

from ...utils import MISSING, try_id

if TYPE_CHECKING:
    import io
    from datetime import datetime as dt

    from ...api import HTTPConnection
    from ...enums import EventEntityType, EventPrivacyLevel, EventStatus
    from ..abc import Snowflake, StateSnowflakeWithGuild
    from ..guild_member import GuildMember
    from ..scheduled_event import ScheduledEvent
    from ..user import User

__all__ = (
    'ScheduledEventAPIMixin',
)


class ScheduledEventAPIMixin:

    id: int
    state: HTTPConnection

    @classmethod
    async def create(
            cls,
            state: HTTPConnection,
            guild: int | Snowflake,
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

        .. seealso:: :func:`novus.Guild.create_scheduled_event`

        Parameters
        ----------
        state : novus.HTTPConnection
            The API connection.
        guild : int | novus.abc.Snowflake
            A representation of the guild the event is to be created in.
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

        return await state.guild_scheduled_event.create_guild_scheduled_event(
            try_id(guild),
            **update,
            reason=reason,
        )

    @classmethod
    async def fetch(
            cls,
            state: HTTPConnection,
            guild: int | Snowflake,
            id: int | Snowflake,
            *,
            with_user_count: bool = False) -> ScheduledEvent:
        """
        Get a scheduled event via its ID.

        Parameters
        ----------
        state : HTTPConnection
            The API connection.
        guild : int | novus.abc.Snowflake
            A representation of the guild the event is from.
        id : int | novus.abc.Snowflake
            A representation of the ID of the event.
        with_user_count : bool
            Whether or not to include the event's user count.

        Returns
        -------
        novus.ScheduledEvent
            The scheduled event associated with the ID.
        """

        return await state.guild_scheduled_event.get_guild_scheduled_event(
            try_id(guild),
            try_id(id),
            with_user_count=with_user_count,
        )

    @classmethod
    async def fetch_all_for_guild(
            cls,
            state: HTTPConnection,
            guild: int | Snowflake,
            *,
            with_user_count: bool = False) -> list[ScheduledEvent]:
        """
        Get a list of all of the scheduled events for a guild.

        .. seealso:: :func:`novus.Guild.fetch_scheduled_events`

        Parameters
        ----------
        state : HTTPConnection
            The API connection.
        guild : int | novus.abc.Snowflake
            A representation of the guild the event is from.
        with_user_count : bool
            Whether or not to include the event's user count.

        Returns
        -------
        list[novus.ScheduledEvent]
            The scheduled events for the guild.
        """

        return await state.guild_scheduled_event.list_scheduled_events_for_guild(
            try_id(guild),
            with_user_count=with_user_count,
        )

    async def delete(
            self: StateSnowflakeWithGuild) -> None:
        """
        Delete the scheduled event.
        """

        await self.state.guild_scheduled_event.delete_guild_scheduled_event(
            self.guild.id,
            self.id,
        )

    async def edit(
            self: StateSnowflakeWithGuild,
            *,
            reason: str | None = None,
            channel: int | Snowflake | None = MISSING,
            location: str = MISSING,
            name: str = MISSING,
            privacy_level: EventPrivacyLevel = MISSING,
            start_time: dt = MISSING,
            end_time: dt = MISSING,
            description: str | None = MISSING,
            entity_type: EventEntityType | None = MISSING,
            status: EventStatus = MISSING,
            image: str | bytes | io.IOBase | None = MISSING) -> ScheduledEvent:
        """
        Edit the scheduled event.

        Parameters
        ----------
        channel : int | Snowflake | None
            The channel of the scheduled event. Set to ``None`` if the event
            type is being set to external.
        location : str
            The location of the event.
        name : str
            The name of the event.
        privacy_level : novus.EventPrivacyLevel
            The privacy level of the event.
        start_time : datetime.datetime
            The time to schedule the event start.
        end_time : datetime.datetime
            The time to schedule the event end.
        description : str | None
            The description of the event.
        entity_type : novus.EventEntityType | None
            The type of the event.
        status : novus.EventStatus
            The status of the event.
        image : str | bytes | io.IOBase | None
            The cover image of the scheduled event.
        reason : str | None
            The reason shown in the audit log.

        Returns
        -------
        novus.ScheduledEvent
            The updated scheduled event.
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

        return await self.state.guild_scheduled_event.modify_guild_scheduled_event(
            self.guild.id,
            self.id,
            **update,
            reason=reason,
        )

    async def fetch_users(
            self: StateSnowflakeWithGuild,
            *,
            limit: int = 100,
            with_member: bool = False,
            before: int | None = None,
            after: int | None = None) -> list[User | GuildMember]:
        """
        Get a scheduled event via its ID.

        Parameters
        ----------
        limit : int
            The number of users to return. Max 100.
        with_member : bool
            Whether to include guild member data if it exists.
        before : int
            Consider only users before the given ID.
        after : int
            Consider only users after the given ID.

        Returns
        -------
        list[novus.User | novus.GuildMember]
            The users/members subscribed to the event.
        """

        return await self.state.guild_scheduled_event.get_guild_scheduled_event_users(
            self.guild.id,
            self.id,
            limit=limit,
            with_member=with_member,
            before=before,
            after=after,
        )
