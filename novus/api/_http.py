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

from typing import TYPE_CHECKING, Any, Iterable
import logging
import io

import aiohttp

from .guild import GuildHTTPConnection
from ..utils import bytes_to_base64_data

if TYPE_CHECKING:
    from ._route import Route

__all__ = (
    'HTTPConnection',
)

log = logging.getLogger("novus.api")


class HTTPConnection:
    """
    A wrapper around the API for HTTP handling.

    Parameters
    ----------
    token : str
        The token to use.
    auth_prefix : str
        The prefix for the token to use in the authentication header. Defaults
        to `"Bot"`.

    Attributes
    ----------
    guild : GuildHTTPConnection
    """

    def __init__(self, token: str, auth_prefix: str = 'Bot'):
        self._session: aiohttp.ClientSession | None = None
        self._token = f"{auth_prefix} {token}"

        # Specific routes
        self.guild = GuildHTTPConnection(self)

    async def get_session(self) -> aiohttp.ClientSession:
        if self._session:
            return self._session
        self._session = aiohttp.ClientSession()
        return self._session

    async def request(
            self,
            route: Route,
            *,
            reason: str | None = None,
            params: dict | None = None,
            data: dict | None = None) -> Any:
        """
        Perform a web request.
        """

        headers = {
            "Authorization": self._token,
        }
        if reason:
            headers['X-Audit-Log-Reason'] = reason
        log.debug(
            "Sending {0.method} {0.path} with {1}"
            .format(route, data)
        )
        session = await self.get_session()
        resp: aiohttp.ClientResponse = await session.request(
            route.method,
            route.url,
            params=params,
            json=data,
            headers=headers,
            timeout=5,
        )
        json = await resp.json()
        log.debug(
            "Response {0.method} {0.path} returned {1.status} {2}"
            .format(route, resp, json)
        )
        return json

    @staticmethod
    def _get_type_kwargs(
            args: Iterable[tuple[str, str] | str],
            kwargs: dict) -> dict[str, Any]:
        """
        Fix up the given user list of kwargs to return a dict of updated ones.
        """

        updated = {}
        for item in args:
            if isinstance(item, tuple):
                updated_key, kwarg_key = item
            else:
                updated_key, kwarg_key = item, item
            if kwarg_key in kwargs:
                updated[updated_key] = kwargs.pop(kwarg_key)
        return updated

    @staticmethod
    def _get_snowflake_kwargs(
            args: Iterable[tuple[str, str] | str],
            kwargs: dict) -> dict[str, Any]:
        """
        Fix up the given user list of kwargs to return a dict of updated ones.
        This assumes each given item is a snowflake, so returns its ``.id``.
        """

        updated = {}
        for item in args:
            if isinstance(item, tuple):
                updated_key, kwarg_key = item
            else:
                updated_key, kwarg_key = item, item
            if kwarg_key in kwargs:
                updated[updated_key] = kwargs.pop(kwarg_key).id
        return updated

    @staticmethod
    def _get_enum_kwargs(
            args: Iterable[tuple[str, str] | str],
            kwargs: dict) -> dict[str, Any]:
        """
        Fix up the given user list of kwargs to return a dict of updated ones.
        This assumes each given item is an enum, so returns its ``.value``.
        """

        updated = {}
        for item in args:
            if isinstance(item, tuple):
                updated_key, kwarg_key = item
            else:
                updated_key, kwarg_key = item, item
            if kwarg_key in kwargs:
                updated[updated_key] = kwargs.pop(kwarg_key).value
        return updated

    @staticmethod
    def _get_image_kwargs(
            args: Iterable[tuple[str, str] | str],
            kwargs: dict) -> dict[str, Any]:
        """
        Fix up the given user list of kwargs to return a dict of updated ones.
        This assumes each given item is a binary string or `io.BytesIO` object.
        """

        updated = {}
        for item in args:
            if isinstance(item, tuple):
                updated_key, kwarg_key = item
            else:
                updated_key, kwarg_key = item, item
            if kwarg_key in kwargs:
                given_arg = kwargs.pop(kwarg_key)
                if given_arg is None:
                    encoded = None
                elif isinstance(given_arg, bytes):
                    encoded = bytes_to_base64_data(given_arg)
                elif isinstance(given_arg, str):
                    with open(given_arg, 'rb') as a:
                        encoded = bytes_to_base64_data(a.read())
                elif isinstance(given_arg, io.IOBase):
                    encoded = bytes_to_base64_data(given_arg.read())
                else:
                    raise ValueError("Unsupported type %s" % type(given_arg))
                updated[updated_key] = encoded
        return updated
