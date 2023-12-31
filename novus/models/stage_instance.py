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

from ..enums import EventPrivacyLevel
from ..utils import MISSING, try_object, try_snowflake

if TYPE_CHECKING:
    from ..api import HTTPConnection
    from ..payloads import StageInstance as StageInstancePayload
    from . import abc

__all__ = (
    'StageInstance',
)


class StageInstance:
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

    # API methods

    @classmethod
    async def create(
            cls,
            state: HTTPConnection,
            *,
            reason: str | None = None,
            channel: int | abc.Snowflake,
            topic: str,
            privacy_level: EventPrivacyLevel = MISSING,
            send_start_notification: bool = MISSING) -> StageInstance:
        """
        Create a stage instance.

        Parameters
        ----------
        state : HTTPConnection
            The API connection.
        channel : int | Snowflake
            The stage channel to be added to.
        topic : str
            The topic assigned to the stage.
        privacy_level : EventPrivacyLevel
            The privacy level of the instance.
        send_start_notification : bool
            Notify @everyone that a stage instance has started.
        reason : str | None
            The reason shown in the audit log.

        Returns
        -------
        novus.StageInstance
            The stage instance.
        """

        kwargs: dict[str, Any] = {
            "channel": try_object(channel),
            "topic": topic,
            "privacy_level": privacy_level,
            "send_start_notification": send_start_notification,
        }
        return await state.stage_instance.create_stage_instance(
            reason=reason,
            **kwargs
        )

    @classmethod
    async def fetch(
            cls,
            state: HTTPConnection,
            id: int) -> StageInstance:
        """
        Get a created stage instance.

        Parameters
        ----------
        state : HTTPConnection
            The API connection.
        id : int
            The ID of the stage.

        Returns
        -------
        novus.StageInstance
            The stage instance.
        """

        return await state.stage_instance.get_stage_instance(id)

    async def edit(
            self: abc.StateSnowflake,
            *,
            topic: str = MISSING,
            privacy_level: EventPrivacyLevel = MISSING) -> StageInstance:
        """
        Update an existing stage instance.

        Parameters
        ----------
        topic : str
            The topic of the stage instance.
        privacy_level : novus.EventPrivacyLevel
            The privacy level of the stage instance.

        Returns
        -------
        novus.StageInstance
            The stage instance.
        """

        update: dict[str, Any] = {}

        if topic is not MISSING:
            update["topic"] = topic
        if privacy_level is not MISSING:
            update["privacy_level"] = privacy_level

        return await self.state.stage_instance.modify_stage_instance(
            self.id,
            **update,
        )
