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
from typing import TYPE_CHECKING, Any

from typing_extensions import Self

from ..enums import EventEntityType, EventPrivacyLevel, EventStatus
from ..utils import (
    MISSING,
    cached_slot_property,
    generate_repr,
    parse_timestamp,
    try_id,
    try_snowflake,
    DiscordDatetime,
)
from .abc import Hashable
from .asset import Asset
from .user import User

if TYPE_CHECKING:
    from .. import payloads
    from ..api import HTTPConnection
    from ..utils.types import FileT
    from . import abc
    from .channel import Channel
    from .guild import BaseGuild
    from .guild_member import GuildMember

__all__ = (
    'ScheduledEvent',
)


class ScheduledEvent(Hashable):
    """
    A model representing a scheduled event for a guild.

    Attributes
    ----------
    id : int
        The ID of the event.
    guild : novus.Guild | novus.Object
        The guild that the event is taking place as part of.
    channel : novus.StageChannel | None
        The channel that the event will take place in. Can be ``None`` if
        the event is taking place externally.
    creator : novus.User | None
        The ID of the user that created the event. Will be ``None`` if the
        event was created before October 25th 2021.
    name : str
        The name of the event.
    description : str | None
        The description given to the event.
    start_time : datetime.datetime
        The scheduled start time of the event.
    end_time : datetime.datetime | None
        The time the event will end. Required if the event type is external.
    privacy_level : novus.EventPrivacyLevel
        The privacy level of the event.
    status : novus.EventStatus
        The status of the event.
    entity_type : novus.EventEntityType
        The tye of the scheduled event.
    entity_id : int | None
        The ID of an entity associated with the event. Will not be set if the
        type is external.
    location : str | None
        The given location of the event, if the event is external.
    user_count : int
        The number of users subscribed to the scheduled event.
    image_hash : str | None
        The cover image hash of the scheduled event.
    image : novus.Asset | None
        An asset associated with the cover image hash for the event.
    """

    __slots__ = (
        'state',
        'id',
        'guild',
        'channel',
        'creator',
        'name',
        'description',
        'start_time',
        'end_time',
        'privacy_level',
        'status',
        'entity_type',
        'entity_id',
        'location',
        'creator',
        'user_count',
        'image_hash',
        '_cs_image',
    )

    id: int
    guild: BaseGuild
    channel: Channel | None
    creator: User | None
    name: str
    description: str | None
    start_time: DiscordDatetime
    end_time: DiscordDatetime | None
    privacy_level: EventPrivacyLevel
    status: EventStatus
    entity_type: EventEntityType
    entity_id: int | None
    location: str | None
    user_count: int
    image_hash: str | None

    def __init__(self, *, state: HTTPConnection, data: payloads.GuildScheduledEvent):
        self.state = state
        self.id = try_snowflake(data['id'])
        self.guild = self.state.cache.get_guild(data["guild_id"])
        channel_id = data.get("channel_id")
        if channel_id is None:
            self.channel = None
        else:
            self.channel = self.state.cache.get_channel(channel_id)
        creator_id = data.get("creator_id")
        self.creator = None
        if creator_id is not None:
            cached = self.state.cache.get_user(creator_id)
            if cached and "creator" in data:
                cached._update(data["creator"])
                self.creator = cached
            elif "creator" in data:
                self.creator = User(state=self.state, data=data["creator"])
            else:
                self.creator = None  # no cached user, and no user provided
        self.name = data['name']
        self.description = data.get('description')
        self.start_time = parse_timestamp(data['scheduled_start_time'])
        self.end_time = parse_timestamp(data.get('scheduled_end_time'))
        self.privacy_level = EventPrivacyLevel(data['privacy_level'])
        self.status = EventStatus(data['status'])
        self.entity_type = EventEntityType(data['entity_type'])
        self.entity_id = try_snowflake(data.get('entity_id'))
        self.location = (data.get('entity_metadata') or {}).get('location')
        self.creator = None
        self.user_count = data.get('user_count', 0)
        self.image_hash = data.get('image')

    __repr__ = generate_repr(('id', 'guild', 'name',))

    @cached_slot_property('_cs_image')
    def image(self) -> Asset | None:
        if self.image_hash is None:
            return None
        return Asset.from_event_image(self)

    def _update(self, data: payloads.GuildScheduledEvent) -> Self:
        self.name = data["name"]
        self.description = data.get("description")
        self.start_time = parse_timestamp(data["scheduled_start_time"])
        self.end_time = parse_timestamp(data.get("scheduled_end_time"))
        self.privacy_level = EventPrivacyLevel(data["privacy_level"])
        self.status = EventStatus(data["status"])
        self.entity_type = EventEntityType(data["entity_type"])
        self.entity_id = try_snowflake(data.get('entity_id'))
        self.location = (data.get('entity_metadata') or {}).get('location')
        self.image_hash = data.get("image")
        del self.image
        return self

    # API methods

    @classmethod
    async def create(
            cls,
            state: HTTPConnection,
            guild: int | abc.Snowflake,
            *,
            name: str,
            start_time: dt,
            entity_type: EventEntityType,
            privacy_level: EventPrivacyLevel,
            reason: str | None = None,
            channel: int | abc.Snowflake | None = MISSING,
            location: str = MISSING,
            end_time: dt = MISSING,
            description: str | None = MISSING,
            status: EventStatus = MISSING,
            image: FileT | None = MISSING) -> ScheduledEvent:
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
            guild: int | abc.Snowflake,
            id: int | abc.Snowflake,
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
            guild: int | abc.Snowflake,
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
            self: abc.StateSnowflakeWithGuild) -> None:
        """
        Delete the scheduled event.
        """

        await self.state.guild_scheduled_event.delete_guild_scheduled_event(
            self.guild.id,
            self.id,
        )

    async def edit(
            self: abc.StateSnowflakeWithGuild,
            *,
            reason: str | None = None,
            channel: int | abc.Snowflake | None = MISSING,
            location: str = MISSING,
            name: str = MISSING,
            privacy_level: EventPrivacyLevel = MISSING,
            start_time: dt = MISSING,
            end_time: dt = MISSING,
            description: str | None = MISSING,
            entity_type: EventEntityType | None = MISSING,
            status: EventStatus = MISSING,
            image: FileT | None = MISSING) -> ScheduledEvent:
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
            self: abc.StateSnowflakeWithGuild,
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
