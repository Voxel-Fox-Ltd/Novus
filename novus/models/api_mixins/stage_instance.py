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

from typing import TYPE_CHECKING, Any

from ...enums import EventPrivacyLevel
from ...utils import MISSING, try_object

if TYPE_CHECKING:
    from ...api import HTTPConnection
    from .. import StageInstance
    from ..abc import Snowflake, StateSnowflake

__all__ = (
    'StageInstanceAPIMixin',
)


class StageInstanceAPIMixin:

    id: int
    state: HTTPConnection

    @classmethod
    async def create(
            cls,
            state: HTTPConnection,
            *,
            reason: str | None = None,
            channel: int | Snowflake,
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

        return await state.stage_instance.create_stage_instance(
            reason=reason,
            **{
                "channel": try_object(channel),
                "topic": topic,
                "privacy_level": privacy_level,
                "send_start_notification": send_start_notification,
            }
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
            self: StateSnowflake,
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
