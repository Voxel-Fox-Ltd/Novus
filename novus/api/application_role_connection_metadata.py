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

from ._route import Route

if TYPE_CHECKING:
    from ._http import HTTPConnection

__all__ = (
    'ApplicationRoleHTTPConnection',
)


class ApplicationRoleHTTPConnection:

    def __init__(self, parent: HTTPConnection):
        self.parent = parent

    async def get_application_role_records(
            self,
            application_id: int) -> list[dict]:
        """
        Get the application role connection metadata objects for the given
        application.
        """

        route = Route(
            "GET",
            "/applications/{application_id}/role-connections/metadata",
            application_id=application_id,
        )
        data: list[Any] = await self.parent.request(
            route,
        )
        return [
            d
            for d in data
        ]  # TODO

    async def update_application_role_records(
            self,
            application_id: int,
            records: list[Any]) -> list[dict]:
        """
        Get one guild emoji.
        """

        route = Route(
            "PUT",
            "/applications/{application_id}/role-connections/metadata",
            application_id=application_id,
        )
        data: list[Any] = await self.parent.request(
            route,
            data=[i.to_json() for i in records],
        )
        return [
            d
            for d in data
        ]  # TODO
