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

from ..enums import EventPrivacyLevel
from ..utils import try_snowflake
from .api_mixins.stage_instance import StageInstanceAPIMixin

if TYPE_CHECKING:
    from ..api import HTTPConnection
    from ..payloads import StageInstance as StageInstancePayload

__all__ = (
    'StageInstance',
)


class StageInstance(StageInstanceAPIMixin):
    """
    A model for a stage instance, holding information about a live stage.

    Attributes
    ----------
    id : int
        The ID of this stage instance.
    guild_id : int
        The guild ID of the associated stage channel.
    channel_id : int
        The ID of the associated stage channel.
    topic : str
        The topic of the stage instance.
    privacy_level : novus.EventPrivacyLevel
        The privacy level of the stage instance.
    event_id : int | None
        The ID of the scheduled event for this stage instance.
    """

    def __init__(self, *, state: HTTPConnection, data: StageInstancePayload):
        self.state = state
        self.id: int = try_snowflake(data['id'])
        self.guild_id: int = try_snowflake(data['guild_id'])
        self.channel_id: int = try_snowflake(data['channel_id'])
        self.topic: str = data['topic']
        self.privacy_level: EventPrivacyLevel = EventPrivacyLevel(data['privacy_level'])
        self.event_id: int | None = try_snowflake(data.get('guild_scheduled_event_id'))
