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

    async def get_bearer_from_code(self, code: str, redirect_uri: str) -> payloads.OauthToken:
        """Get the bearer token from a code."""

        route = Route(
            "POST",
            "/oauth2/token",
        )
        post_data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
        }
        data: payloads.OauthToken = await self.parent.request(
            route,
            data=post_data,
            auth=True,
            form=True,
        )
        return data

    async def get_bearer_from_refresh_token(self, token: str) -> payloads.OauthToken:
        """Get the bearer token from a refresh token."""

        route = Route(
            "POST",
            "/oauth2/token",
        )
        post_data = {
            "grant_type": "refresh_token",
            "refresh_token": token,
        }
        data: payloads.OauthToken = await self.parent.request(
            route,
            data=post_data,
            auth=True,
            form=True,
        )
        return data

    async def revoke_access_token(self, token: str) -> None:
        """Revoke an access token."""

        route = Route(
            "POST",
            "/oauth2/token/revoke",
        )
        post_data = {
            "token": token,
        }
        data: payloads.OauthToken = await self.parent.request(
            route,
            data=post_data,
            auth=True,
            form=True,
        )

    async def get_client_credentials(self, scopes: str = "identify") -> payloads.OauthToken:
        """Revoke an access token."""

        route = Route(
            "POST",
            "/oauth2/token",
        )
        post_data = {
            "grant_type": "client_credentials",
            "scope": scopes,
        }
        data: payloads.OauthToken = await self.parent.request(
            route,
            data=post_data,
            auth=True,
            form=True,
        )
        return data

    async def get_current_bot_information(self) -> Application:
        """Get the current bot information via token."""

        route = Route(
            "GET",
            "/oauth2/applications/@me",
        )
        data: payloads.Application = await self.parent.request(route)
        return Application(state=self.parent, data=data)
