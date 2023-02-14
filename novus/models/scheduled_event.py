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

from datetime import datetime as dt
from typing import TYPE_CHECKING

from ..enums import EventEntityType, EventPrivacyLevel, EventStatus
from ..utils import cached_slot_property, generate_repr, parse_timestamp, try_snowflake
from .api_mixins.scheduled_event import ScheduledEventAPIMixin
from .asset import Asset
from .object import Object
from .user import User

if TYPE_CHECKING:
    from ..api import HTTPConnection
    from ..models.abc import StateSnowflake
    from ..payloads.guild_scheduled_event import GuildScheduledEvent as EventPayload

__all__ = (
    'ScheduledEvent',
)


class ScheduledEvent(ScheduledEventAPIMixin):
    """
    A model representing a scheduled event for a guild.

    Attributes
    ----------
    id : int
        The ID of the event.
    guild : novus.abc.Snowflake
        A object wrapper for the guild ID.
    channel_id : int | None
        The channel ID that the event will take place in. Can be ``None`` if
        the event is taking place externally.
    creator_id : int | None
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
    creator : novus.User | None
        The creator of the event. Will be ``None`` if the event was created
        before October 25th 2021.
    user_count : int
        The number of users subscribed to the scheduled event.
    image_hash : str | None
        The cover image hash of the scheduled event.
    image : novus.Asset | None
        An asset associated with the cover image hash for the event.
    """

    __slots__ = (
        '_state',
        'id',
        'guild',
        'channel_id',
        'creator_id',
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

    def __init__(self, *, state: HTTPConnection, data: EventPayload, guild: StateSnowflake):
        self._state = state
        self.id: int = try_snowflake(data['id'])
        self.guild: StateSnowflake = Object(try_snowflake(data['guild_id']), state=self._state)
        self.channel_id: int | None = try_snowflake(data.get('channel_id'))
        self.creator_id: int | None = try_snowflake(data.get('creator_id'))
        self.name: str = data['name']
        self.description: str | None = data.get('description')
        self.start_time: dt = parse_timestamp(data['scheduled_start_time'])
        self.end_time: dt | None = parse_timestamp(data.get('scheduled_end_time'))
        self.privacy_level: EventPrivacyLevel = EventPrivacyLevel(data['privacy_level'])
        self.status: EventStatus = EventStatus(data['status'])
        self.entity_type: EventEntityType = EventEntityType(data['entity_type'])
        self.entity_id: int | None = try_snowflake(data.get('entity_id'))
        self.location: str | None = (data.get('entity_metadata') or {}).get('location')
        self.creator: User | None = None
        if 'creator' in data:
            self.creator = User(state=self._state, data=data['creator'])
        self.user_count: int = data.get('user_count', 0)
        self.image_hash: str | None = data.get('image')

    __repr__ = generate_repr(('id', 'guild_id', 'name',))

    @cached_slot_property('_cs_image')
    def image(self) -> Asset | None:
        if self.image_hash is None:
            return None
        return Asset.from_event_image(self)
