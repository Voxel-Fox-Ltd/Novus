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

from ..models import StageInstance
from ._route import Route

if TYPE_CHECKING:
    from .. import payloads
    from ._http import HTTPConnection

__all__ = (
    'StageHTTPConnection',
)


class StageHTTPConnection:

    def __init__(self, parent: HTTPConnection):
        self.parent = parent

    async def create_stage_instance(
            self,
            *,
            reason: str | None = None,
            **kwargs: dict[str, Any]) -> StageInstance:
        """
        Create a stage instance aassociated with a stage channel.
        """

        post_data = self.parent._get_kwargs(
            {
                "type": (
                    "topic",
                    "send_start_notification",
                ),
                "snowflake": (
                    ("channel_id", "channel",),
                ),
                "enum": (
                    "privacy_level",
                ),
            },
            kwargs,
        )
        route = Route(
            "POST",
            "/stage-instances",
        )
        data: payloads.StageInstance = await self.parent.request(
            route,
            reason=reason,
            data=post_data,
        )
        return StageInstance(state=self.parent, data=data)

    async def get_stage_instance(
            self,
            channel_id: int) -> StageInstance:
        """
        Get a stage instance.
        """

        route = Route(
            "GET",
            "/stage-instances/{channel_id}",
            channel_id=channel_id,
        )
        data: payloads.StageInstance = await self.parent.request(
            route,
        )
        return StageInstance(state=self.parent, data=data)

    async def modify_stage_instance(
            self,
            channel_id: int,
            *,
            reason: str | None = None,
            **kwargs: dict[str, Any]) -> StageInstance:
        """
        Update a stage instance.
        """

        post_data = self.parent._get_kwargs(
            {
                "type": (
                    "topic",
                ),
                "enum": (
                    "privacy_level",
                ),
            },
            kwargs,
        )
        route = Route(
            "PATCH",
            "/stage-instances/{channel_id}",
            channel_id=channel_id,
        )
        data: payloads.StageInstance = await self.parent.request(
            route,
            reason=reason,
            data=post_data,
        )
        return StageInstance(state=self.parent, data=data)

    async def delete_stage_instance(
            self,
            channel_id: int,
            *,
            reason: str | None = None) -> None:
        """
        Delete a stage instance.
        """

        route = Route(
            "DELETE",
            "/stage-instances/{channel_id}",
            channel_id=channel_id,
        )
        await self.parent.request(
            route,
            reason=reason,
        )
        return
