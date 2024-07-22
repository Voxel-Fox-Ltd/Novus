"""
Copyright (c) Kae Bartlett

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
any later version.

This program is dis2tributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ._route import Route
from ..models import Entitlement, SKU

if TYPE_CHECKING:
    from ._http import HTTPConnection
    from .. import payloads

__all__ = (
    'MonetizationHTTPConnection',
)


class MonetizationHTTPConnection:

    def __init__(self, parent: HTTPConnection):
        self.parent = parent

    async def list_skus(
            self,
            application_id: int) -> list[SKU]:
        """List all SKUs associated with the given application ID."""

        route = Route(
            "GET",
            "/applications/{application_id}/skus",
            application_id=application_id,
        )
        data: list[payloads.SKU] = await self.parent.request(
            route,
        )
        return [
            SKU(state=self.parent, data=d)
            for d in data
        ]

    async def list_entitlements(
            self,
            application_id: int) -> list[Entitlement]:
        """List all entitlements associated with the given application ID."""

        route = Route(
            "GET",
            "/applications/{application_id}/commands",
            application_id=application_id,
        )
        data: list[payloads.ApplicationCommand] = await self.parent.request(
            route,
        )
        return [
            Entitlement(state=self.parent, data=d)
            for d in data
        ]

    async def consume_entitlement(
            self,
            application_id: int,
            entitlement_id: int) -> list[Entitlement]:
        """List all entitlements associated with the given application ID."""

        route = Route(
            "GET",
            "/applications/{application_id}/commands",
            application_id=application_id,
        )
        data: list[payloads.ApplicationCommand] = await self.parent.request(
            route,
        )
        return [
            Entitlement(state=self.parent, data=d)
            for d in data
        ]
