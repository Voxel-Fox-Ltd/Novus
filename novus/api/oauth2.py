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

from typing import TYPE_CHECKING

from ..models import Application
from ._route import Route

if TYPE_CHECKING:
    from .. import payloads
    from ._http import HTTPConnection

__all__ = (
    'Oauth2HTTPConnection',
)


class Oauth2HTTPConnection:

    def __init__(self, parent: HTTPConnection):
        self.parent = parent

    async def get_current_bot_information(self) -> Application:
        """Get the current bot information via token."""

        route = Route(
            "GET",
            "/oauth2/applications/@me",
        )
        data: payloads.Application = await self.parent.request(route)
        return Application(state=self.parent, data=data)
