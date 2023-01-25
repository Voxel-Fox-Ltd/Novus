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

from typing import TYPE_CHECKING, Any, Iterable, TypedDict
import logging
import io

import aiohttp


# .application_role_connection_metadata
# .audit_log
# .auto_moderation
# .channel
from .emoji import EmojiHTTPConnection
from .guild import GuildHTTPConnection
# .guild_scheduled_event
# .guild_template
# .invite
# .stage_instance
# .sticker
from .user import UserHTTPConnection
# .voice
# .webhook
from ..utils import bytes_to_base64_data

if TYPE_CHECKING:
    from ._route import Route

__all__ = (
    'HTTPConnection',
    'OauthHTTPConnection',
)


log = logging.getLogger("novus.api")


class FixableKwargs(TypedDict, total=False):
    type: Iterable[tuple[str, str] | str]
    enum: Iterable[tuple[str, str] | str]
    snowflake: Iterable[tuple[str, str] | str]
    image: Iterable[tuple[str, str] | str]
    object: Iterable[tuple[str, str] | str]
    timestamp: Iterable[tuple[str, str] | str]
    flags: Iterable[tuple[str, str] | str]


class HTTPException(Exception):
    """
    Generic base class for all HTTP errors.
    """

    def __init__(self, payload: dict):
        self.payload: dict = payload
        self.message: str = payload['message']
        self.code: int = payload['code']


class NotFound(HTTPException):
    """
    When a resource cannot be found on the server.
    """


class Unauthorized(HTTPException):
    """
    When you are missing relevant permissions to access a resource.
    """


class HTTPConnection:
    """
    A wrapper around the API for HTTP handling.

    As well as this class (and it's subclasses), each applicable model should
    have an API mixin.

    The mixins are intended to be user facing, so have all
    of the parameters added.

    The HTTP connection classes have positional parameters for the resource
    params; a keyword only parameter for the reason (if applicable) and any GET
    parameters; and the kwargs are added to the JSON body. For the most part,
    kwargs get fixed up into a valid payload. Known kwargs are assumed to be
    the correct type (things like a ``channel`` kwarg will be fixed into a
    ``channel_id`` via the ``.id`` attribute; a flags class will get its
    ``.value`` attribute and cast to a string for the payload, etc). Any
    unknown kwargs will be added as is to the payload, which allows you to
    add any additional arguments should Discord update before the library.

    Parameters
    ----------
    token : str
        The token to use.

    Attributes
    ----------
    application_role_connection_metadata: Any
    audit_log: Any
    auto_moderation: Any
    channel: Any
    emoji: EmojiHTTPConnection
    guild: GuildHTTPConnection
    guild_scheduled_event: Any
    guild_template: Any
    invite: Any
    stage_instance: Any
    sticker: Any
    user: UserHTTPConnection
    voice: Any
    webhook: Any
    """

    AUTH_PREFIX: str = "Bot"

    def __init__(self, token: str):
        self._session: aiohttp.ClientSession | None = None
        self._token = f"{self.AUTH_PREFIX} {token}"
        self._user_agent = (
            "DiscordBot (Python, Novus, https://github.com/Voxel-Fox-Ltd/Novus)"
        )

        # Specific routes
        self.application_role_connection_metadata: Any
        self.audit_log: Any
        self.auto_moderation: Any
        self.channel: Any
        self.emoji = EmojiHTTPConnection(self)
        self.guild = GuildHTTPConnection(self)
        self.guild_scheduled_event: Any
        self.guild_template: Any
        self.invite: Any
        self.stage_instance: Any
        self.sticker: Any
        self.user = UserHTTPConnection(self)
        self.voice: Any
        self.webhook: Any

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
            "User-Agent": self._user_agent,
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
        json: dict[Any, Any] | None
        try:
            json = await resp.json()
        except Exception:
            if resp.ok:
                json = None
            else:
                raise AssertionError("Cannot parse JSON from response.")
        if not resp.ok:
            assert isinstance(json, dict)
            if resp.status == 401:
                raise Unauthorized(json)
            elif resp.status == 404:
                raise NotFound(json)
            else:
                raise HTTPException(json)
        log.debug(
            "Response {0.method} {0.path} returned {1.status} {2}"
            .format(route, resp, json)
        )
        return json

    @classmethod
    def _get_kwargs(
            cls,
            args: FixableKwargs,
            kwargs: dict[str, Any]) -> dict[str, Any]:
        """
        A single catch-all kwargs fixer for POST requests.
        """

        to_return: dict[str, Any] = {}
        to_return.update(cls._get_type_kwargs(args.get('type', ()), kwargs))
        to_return.update(cls._get_enum_kwargs(args.get('enum', ()), kwargs))
        to_return.update(cls._get_snowflake_kwargs(args.get('snowflake', ()), kwargs))
        to_return.update(cls._get_image_kwargs(args.get('image', ()), kwargs))
        to_return.update(cls._get_object_kwargs(args.get('object', ()), kwargs))
        to_return.update(cls._get_timestamp_kwargs(args.get('timestamp', ()), kwargs))
        to_return.update(cls._get_flags_kwargs(args.get('flags', ()), kwargs))
        to_return.update(kwargs)
        return to_return

    @staticmethod
    def _unpack_kwarg_key(item: tuple[str, str] | str) -> tuple[str, str]:
        if isinstance(item, tuple):
            updated_key, kwarg_key = item
        else:
            updated_key, kwarg_key = item, item
        return updated_key, kwarg_key

    @classmethod
    def _get_type_kwargs(
            cls,
            args: Iterable[tuple[str, str] | str],
            kwargs: dict[str, Any]) -> dict[str, Any]:
        """
        Fix up the given user list of kwargs to return a dict of updated ones.
        """

        updated: dict[str, Any] = {}
        for iter_key in args:
            updated_key, kwarg_key = cls._unpack_kwarg_key(iter_key)
            if kwarg_key not in kwargs:
                continue
            updated[updated_key] = kwargs.pop(kwarg_key)
        return updated

    @classmethod
    def _get_snowflake_kwargs(
            cls,
            args: Iterable[tuple[str, str] | str],
            kwargs: dict[str, Any]) -> dict[str, Any]:
        """
        Fix up the given user list of kwargs to return a dict of updated ones.
        This assumes each given item is a snowflake, so returns its ``.id``.
        """

        updated: dict[str, Any] = {}
        for iter_key in args:
            updated_key, kwarg_key = cls._unpack_kwarg_key(iter_key)
            if kwarg_key not in kwargs:
                continue

            item = kwargs.pop(kwarg_key)
            updated[updated_key] = None
            if item is not None:
                if isinstance(item, (list, tuple)):
                    updated[updated_key] = [str(i.id) for i in item]
                else:
                    updated[updated_key] = str(item.id)

        return updated

    @classmethod
    def _get_enum_kwargs(
            cls,
            args: Iterable[tuple[str, str] | str],
            kwargs: dict[str, Any]) -> dict[str, Any]:
        """
        Fix up the given user list of kwargs to return a dict of updated ones.
        This assumes each given item is an enum, so returns its ``.value``.
        """

        updated: dict[str, Any] = {}
        for iter_key in args:
            updated_key, kwarg_key = cls._unpack_kwarg_key(iter_key)
            if kwarg_key not in kwargs:
                continue

            item = kwargs.pop(kwarg_key)
            updated[updated_key] = None
            if item is not None:
                if isinstance(item, (list, tuple)):
                    updated[updated_key] = [i.value for i in item]
                else:
                    updated[updated_key] = item.value

        return updated

    @classmethod
    def _get_image_kwargs(
            cls,
            args: Iterable[tuple[str, str] | str],
            kwargs: dict[str, Any]) -> dict[str, Any]:
        """
        Fix up the given user list of kwargs to return a dict of updated ones.
        This assumes each given item is a binary string or `io.BytesIO` object.
        """

        updated: dict[str, Any] = {}
        for iter_key in args:
            updated_key, kwarg_key = cls._unpack_kwarg_key(iter_key)
            if kwarg_key not in kwargs:
                continue

            given_arg = kwargs.pop(kwarg_key)
            if given_arg is None:
                updated[updated_key] = None
            elif isinstance(given_arg, bytes):
                updated[updated_key] = bytes_to_base64_data(given_arg)
            elif isinstance(given_arg, str):
                with open(given_arg, 'rb') as a:
                    updated[updated_key] = bytes_to_base64_data(a.read())
            elif isinstance(given_arg, io.IOBase):
                updated[updated_key] = bytes_to_base64_data(given_arg.read())
            else:
                raise ValueError("Unsupported type %s" % type(given_arg))

        return updated

    @classmethod
    def _get_object_kwargs(
            cls,
            args: Iterable[tuple[str, str] | str],
            kwargs: dict[str, Any]) -> dict[str, Any]:
        """
        Fix up the given user list of kwargs to return a dict of updated ones.
        This assumes each given item is an object implementing a ``.to_dict``
        method (or a list thereof).
        """

        updated: dict[str, Any] = {}
        for iter_key in args:
            updated_key, kwarg_key = cls._unpack_kwarg_key(iter_key)
            if kwarg_key not in kwargs:
                continue

            item = kwargs.pop(kwarg_key)
            updated[updated_key] = None
            if item is not None:
                if isinstance(item, (list, tuple)):
                    updated[updated_key] = [i.to_json() for i in item]
                else:
                    updated[updated_key] = item.to_json()

        return updated

    @classmethod
    def _get_timestamp_kwargs(
            cls,
            args: Iterable[tuple[str, str] | str],
            kwargs: dict[str, Any]) -> dict[str, Any]:
        """
        Fix up the given user list of kwargs to return a dict of updated ones.
        This assumes each given item is a timestamp.
        """

        updated: dict[str, Any] = {}
        for iter_key in args:
            updated_key, kwarg_key = cls._unpack_kwarg_key(iter_key)
            if kwarg_key not in kwargs:
                continue

            item = kwargs.pop(kwarg_key)
            updated[updated_key] = None
            if item is not None:
                if isinstance(item, (list, tuple)):
                    updated[updated_key] = [i.isoformat() for i in item]
                else:
                    updated[updated_key] = item.isoformat()

        return updated

    @classmethod
    def _get_flags_kwargs(
            cls,
            args: Iterable[tuple[str, str] | str],
            kwargs: dict[str, Any]) -> dict[str, Any]:
        """
        Fix up the given user list of kwargs to return a dict of updated ones.
        This assumes each given item is a flags item.
        """

        updated = {}
        for iter_key in args:
            updated_key, kwarg_key = cls._unpack_kwarg_key(iter_key)
            if kwarg_key not in kwargs:
                continue

            item = kwargs.pop(kwarg_key)
            if item is not None:
                item = str(item.value)
            updated[updated_key] = item

        return updated


class OauthHTTPConnection(HTTPConnection):
    AUTH_PREFIX: str = "Bearer"
