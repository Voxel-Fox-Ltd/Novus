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
from .user import User

if TYPE_CHECKING:
    from .. import payloads
    from ..api import HTTPConnection
    from . import Channel, Guild
    from . import api_mixins as amix

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
        '_state',
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
    guild: Guild | amix.GuildAPIMixin
    channel: Channel | None
    creator: User | amix.UserAPIMixin | None
    name: str
    description: str | None
    start_time: dt
    end_time: dt | None
    privacy_level: EventPrivacyLevel
    status: EventStatus
    entity_type: EventEntityType
    entity_id: int | None
    location: str | None
    user_count: int
    image_hash: str | None

    def __init__(self, *, state: HTTPConnection, data: payloads.GuildScheduledEvent):
        self._state = state
        self.id = try_snowflake(data['id'])
        self.guild = self._state.cache.get_guild(data["guild_id"], or_object=True)
        channel_id = data.get("channel_id")
        if channel_id is None:
            self.channel = None
        else:
            self.channel = self._state.cache.get_channel(channel_id, or_object=True)
        creator_id = data.get("creator_id")
        if creator_id is None:
            self.creator = None
        else:
            cached = self._state.cache.get_user(creator_id, or_object=False)
            if cached:
                self.creator = cached
            elif "creator" in data:
                self.creator = User(state=self._state, data=data["creator"])
            else:
                self.creator = self._state.cache.get_user(creator_id, or_object=True)
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
