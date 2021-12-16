"""
The MIT License (MIT)

Copyright (c) 2021-present Kae Bartlett

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Union
from datetime import datetime as dt

from .guild import Guild
from .mixins import Hashable
from .utils import MISSING, _get_as_snowflake, parse_time
from .enums import GuildScheduledEventPrivacyLevel, GuildScheduledEventStatus, GuildScheduledEventEntityType, try_enum
from .user import User

if TYPE_CHECKING:
    from .channel import VoiceChannel, StageChannel

__all__ = (
    "GuildScheduledEventEntityMetadata",
    "GuildScheduledEvent",
)


class GuildScheduledEventEntityMetadata:
    """
    The medatadata that's included for external guild scheduled events.

    Attributes
    ----------------
    location: :class:`str`
        The location that the guild event is scheduled to take place in.
    """

    def __init__(self, *, data):
        self.location: Optional[str] = data.get("location")


class GuildScheduledEvent(Hashable):
    """
    An object representing a guild scheduled event.

    Attributes
    ------------
    id: :class:`int`
        The ID of the event.
    guild_id: :class:`int`
        The ID of the guild that the event is attached to.
    guild: Optional[:class:`Guild`]
        The guild that the event is attached to.
    channel_id: Optional[:class:`int`]
        The ID of the channel where the event is going to occur.
    channel: Optional[Union[:class:`VoiceChannel`, :class:`StageChannel`]]
        The channel where the event is set to occur.
    creator_id: :class:`int`
        The ID of the user who created the event. Will only be present for events
        created after October 25th 2021.
    creator: Optional[:class:`User`]
        The user who created the event.
    name: :class:`str`
        The name of the event.
    description: :class:`str`
        The user-given description of the event.
    scheduled_start_time: :class:`datetime.datetime`
        The timestamp of when the event is meant to start.
    scheduled_end_time: Optional[:class:`datetime.datetime`]
        The timestamp of when the event is meant to end. Only required for external events.
    privacy_level: :class:`GuildScheduledEventPrivacyLevel`
        The privacy level of the event.
    status: :class:`GuildScheduledEventStatus`
        The event's status.
    entity_type: :class:`GuildScheduledEventEntityType`
        The entity that the event has been scheduled onto.
    entity_id: Optional[:class:`int`]
        The ID of the channel that the event has been scheduled onto.
    entity_metadata: Optional[:class:`GuildScheduledEventEntityMetadata`]
        The metadata attached to the event. Only applicable to external events.
    creator: Optional[:class:`User`]
        The creator of the event. Will only be present for events created after October 25th 2021.
    user_count: Optional[:class:`int`]
        The number of users who've said they're interested in the event.
    """

    __slots__ = (
        "_state",
        "id",
        "guild_id",
        "channel_id",
        "creator_id",
        "name",
        "description",
        "scheduled_start_time",
        "scheduled_end_time",
        "privacy_level",
        "status",
        "entity_type",
        "entity_id",
        "entity_metadata",
        "creator",
        "user_count",
    )

    def __init__(self, *, state, data):
        self._state = state
        self.id: int = _get_as_snowflake(data, "id")
        self.guild_id: Optional[int] = _get_as_snowflake(data, "guild_id")
        self.channel_id: Optional[int] = _get_as_snowflake(data, "channel_id")
        self.creator_id: Optional[int] = _get_as_snowflake(data, "creator_id")
        self.name: str = data.get("name")
        self.description: Optional[str] = data.get("description")
        self.scheduled_start_time: dt = parse_time(data.get("scheduled_start_time"))
        self.scheduled_end_time: Optional[dt] = parse_time(data.get("scheduled_end_time"))
        self.privacy_level: GuildScheduledEventPrivacyLevel = try_enum(GuildScheduledEventPrivacyLevel, data.get("privacy_level"))
        self.status: GuildScheduledEventStatus = try_enum(GuildScheduledEventStatus, data.get("status"))
        self.entity_type: GuildScheduledEventEntityType = try_enum(GuildScheduledEventEntityType, data.get("entity_type"))
        self.entity_id: Optional[int] = _get_as_snowflake(data, "entity_id")
        self.entity_metadata: Optional[GuildScheduledEventEntityMetadata] = None
        if data.get("entity_metadata"):
            self.entity_metadata = GuildScheduledEventEntityMetadata(data=data.get("entity_metadata"))
        self.creator: Optional[User] = None
        if data.get("creator"):
            self.creator = User(state=state, data=data.get("creator"))
        self.user_count: Optional[int] = data.get("user_count")

    @property
    def guild(self) -> Optional[Guild]:
        """:class:`Guild`: The guild this event belongs to."""

        return self._state._get_guild(self.guild_id)

    @property
    def channel(self) -> Optional[Union[VoiceChannel, StageChannel]]:
        """Union[:class:`VoiceChannel`, :class:`StageChannel`, None]: The channel where the event will occur."""

        if self.channel_id:
            return self._state._get_channel(self.channel_id)
        return None

    async def edit(self, **kwargs):
        """
        Edit the attributes of this event.

        Parameters
        -------------
        """
