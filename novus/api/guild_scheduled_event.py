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

from typing import TYPE_CHECKING, Any, TypeAlias

from ..models import GuildMember, ScheduledEvent, User
from ..utils import MISSING
from ._route import Route

if TYPE_CHECKING:
    from .. import payloads
    from ._http import HTTPConnection

    ValidJSON: TypeAlias = dict[
        str,
        str | int | bool | list['ValidJSON'] | 'ValidJSON',
    ]

__all__ = (
    'GuildEventHTTPConnection',
)


class GuildEventHTTPConnection:

    def __init__(self, parent: HTTPConnection):
        self.parent = parent

    async def list_scheduled_events_for_guild(
            self,
            guild_id: int,
            *,
            with_user_count: bool = MISSING) -> list[ScheduledEvent]:
        """
        Get the scheduled events for the guild.
        """

        route = Route(
            "GET",
            "/guilds/{guild_id}/scheduled-events",
            guild_id=guild_id,
        )
        params: dict[str, str] = {}
        if with_user_count is not MISSING:
            params['with_user_count'] = str(with_user_count).lower()
        data: list[payloads.GuildScheduledEvent] = await self.parent.request(
            route,
            params=params,
        )
        return [
            ScheduledEvent(state=self.parent, data=d)
            for d in data
        ]

    async def create_guild_scheduled_event(
            self,
            guild_id: int,
            *,
            reason: str | None,
            **kwargs: Any) -> ScheduledEvent:
        """
        Get the scheduled events for the guild.
        """

        route = Route(
            "POST",
            "/guilds/{guild_id}/scheduled-events",
            guild_id=guild_id,
        )
        json: ValidJSON = self.parent._get_kwargs(
            {
                "type": (
                    "location",
                    "name",
                    "description",
                ),
                "enum": (
                    "privacy_level",
                    "entity_type",
                ),
                "snowflake": (
                    ("channel_id", "channel"),
                ),
                "image": (
                    "image",
                ),
                "timestamp": (
                    ("scheduled_start_time", "start_time",),
                    ("scheduled_end_time", "end_time",),
                ),
            },
            kwargs,
        )
        location = json.pop("location", None)
        if location is not None:
            json["entity_metadata"] = {
                "location": location,
            }
        data: payloads.GuildScheduledEvent = await self.parent.request(
            route,
            data=json,
            reason=reason,
        )
        return ScheduledEvent(state=self.parent, data=data)

    async def get_guild_scheduled_event(
            self,
            guild_id: int,
            event_id: int,
            *,
            with_user_count: bool = MISSING) -> ScheduledEvent:
        """
        Get a particular guild scheduled event.
        """

        route = Route(
            "GET",
            "/guilds/{guild_id}/scheduled-events/{event_id}",
            guild_id=guild_id,
            event_id=event_id,
        )
        params: dict[str, str] = {}
        if with_user_count is not MISSING:
            params['with_user_count'] = str(with_user_count).lower()
        data: payloads.GuildScheduledEvent = await self.parent.request(
            route,
            params=params,
        )
        return ScheduledEvent(state=self.parent, data=data)

    async def modify_guild_scheduled_event(
            self,
            guild_id: int,
            event_id: int,
            *,
            reason: str | None,
            **kwargs: Any) -> ScheduledEvent:
        """
        Modify a particular scheduled event.
        """

        route = Route(
            "PATCH",
            "/guilds/{guild_id}/scheduled-events/{event_id}",
            guild_id=guild_id,
            event_id=event_id,
        )
        json: ValidJSON = self.parent._get_kwargs(
            {
                "type": (
                    "location",
                    "name",
                    "description",
                ),
                "enum": (
                    "privacy_level",
                    "entity_type",
                ),
                "snowflake": (
                    ("channel_id", "channel"),
                ),
                "image": (
                    "image",
                ),
                "timestamp": (
                    ("scheduled_start_time", "start_time",),
                    ("scheduled_end_time", "end_time",),
                ),
            },
            kwargs,
        )
        location = json.pop("location", None)
        if location is not None:
            json["entity_metadata"] = {
                "location": location,
            }
        data: payloads.GuildScheduledEvent = await self.parent.request(
            route,
            data=json,
            reason=reason,
        )
        return ScheduledEvent(state=self.parent, data=data)

    async def delete_guild_scheduled_event(
            self,
            guild_id: int,
            event_id: int) -> None:
        """
        Delete a given guild scheduled event.
        """

        route = Route(
            "DELETE",
            "/guilds/{guild_id}/scheduled-events/{event_id}",
            guild_id=guild_id,
            event_id=event_id,
        )
        await self.parent.request(
            route,
        )

    async def get_guild_scheduled_event_users(
            self,
            guild_id: int,
            event_id: int,
            *,
            limit: int = 100,
            with_member: bool = False,
            before: int | None = None,
            after: int | None = None) -> list[User | GuildMember]:
        """
        Get the event users for a guild scheduled event.
        """

        route = Route(
            "GET",
            "/guilds/{guild_id}/scheduled-events/{event_id}/users",
            guild_id=guild_id,
            event_id=event_id,
        )
        params: dict[str, int | str] = {
            "limit": limit,
            "with_member": str(with_member).lower(),
        }
        if before is not None:
            params['before'] = before
        if after is not None:
            params['after'] = after
        data: list[payloads.GuildScheduledEventUser] = await self.parent.request(
            route,
            params=params,
        )
        ret: list[User | GuildMember] = []
        for d in data:
            if "member" in d:
                ret.append(
                    GuildMember(
                        state=self.parent,
                        data=d['member'],
                        user=d['user'],
                    )
                )
            else:
                ret.append(
                    User(
                        state=self.parent,
                        data=d['user'],
                    )
                )
        return ret
