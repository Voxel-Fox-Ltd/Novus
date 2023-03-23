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

import io
import json
import logging
from typing import TYPE_CHECKING, Any, Iterable, TypedDict

import aiohttp

from ..models import File
from ..utils import bytes_to_base64_data
from ._cache import APICache
from ._errors import HTTPException, NotFound, Unauthorized
from .application_role_connection_metadata import ApplicationRoleHTTPConnection
from .audit_log import AuditLogHTTPConnection
from .auto_moderation import AutoModerationHTTPConnection
from .channel import ChannelHTTPConnection
from .emoji import EmojiHTTPConnection
from .gateway.gateway import GatewayConnection
from .guild import GuildHTTPConnection
from .guild_scheduled_event import GuildEventHTTPConnection
from .guild_template import GuildTemplateHTTPConnection
from .interaction import InteractionHTTPConnection
from .invite import InviteHTTPConnection
from .oauth2 import Oauth2HTTPConnection
from .stage_instance import StageHTTPConnection
from .sticker import StickerHTTPConnection
from .user import UserHTTPConnection
from .voice import VoiceHTTPConnection
from .webhook import WebhookHTTPConnection

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
    token : str | None
        The token to use.

    Attributes
    ----------
    application_role_connection_metadata : ApplicationRoleHTTPConnection
    audit_log : AuditLogHTTPConnection
    auto_moderation : AutoModerationHTTPConnection
    channel : ChannelHTTPConnection
    emoji : EmojiHTTPConnection
    guild : GuildHTTPConnection
    guild_scheduled_event : GuildEventHTTPConnection
    guild_template : GuildTemplateHTTPConnection
    interaction : InteractionHTTPConnection
    invite : InviteHTTPConnection
    oauth2 : Oauth2HTTPConnection
    stage_instance : StageHTTPConnection
    sticker : StickerHTTPConnection
    user : UserHTTPConnection
    voice : VoiceHTTPConnection
    webhook : WebhookHTTPConnection
    """

    AUTH_PREFIX: str = "Bot"

    def __init__(self, token: str | None = None):
        self._session: aiohttp.ClientSession | None = None
        self._token: str | None = token
        self._prefixed_token: str | None = None
        if token:
            self._prefixed_token = f"{self.AUTH_PREFIX} {token}"
        self._user_agent: str = (
            "DiscordBot (Python, Novus, https://github.com/Voxel-Fox-Ltd/Novus)"
        )
        self.cache = APICache(self)
        self.dispatch = lambda event_name, *data: None

        # Add API routes
        self.application_role_connection_metadata = ApplicationRoleHTTPConnection(self)
        self.audit_log = AuditLogHTTPConnection(self)
        self.auto_moderation = AutoModerationHTTPConnection(self)
        self.channel = ChannelHTTPConnection(self)
        self.emoji = EmojiHTTPConnection(self)
        self.guild = GuildHTTPConnection(self)
        self.guild_scheduled_event = GuildEventHTTPConnection(self)
        self.guild_template = GuildTemplateHTTPConnection(self)
        self.interaction = InteractionHTTPConnection(self)
        self.invite = InviteHTTPConnection(self)
        self.oauth2 = Oauth2HTTPConnection(self)
        self.stage_instance = StageHTTPConnection(self)
        self.sticker = StickerHTTPConnection(self)
        self.user = UserHTTPConnection(self)
        self.voice = VoiceHTTPConnection(self)
        self.webhook = WebhookHTTPConnection(self)

        # Add gateway
        self.gateway = GatewayConnection(self)

    async def get_session(self) -> aiohttp.ClientSession:
        if self._session:
            return self._session
        self._session = aiohttp.ClientSession()
        return self._session

    async def close(self) -> None:
        if self._session:
            await self._session.close()

    async def __aenter__(self) -> None:
        await self.get_session()

    async def __aexit__(self, *_args: Any) -> None:
        if self._session:
            await self._session.close()

    def request_params(
            self,
            *,
            reason: str | None = None,
            data: dict | list | None = None,
            files: list[File] | None = None,
            multipart: bool = False) -> dict:
        """
        Take parameters and return the corresponding web request response.
        """

        # Set headers
        headers = {
            "Authorization": self._prefixed_token,
            "User-Agent": self._user_agent,
        }
        if self._token is None:
            del headers["Authorization"]
        if reason:
            headers['X-Audit-Log-Reason'] = reason

        # Create multipart for files
        writer: aiohttp.FormData | None = None
        form: list[dict] = []
        if files:
            writer = aiohttp.FormData()
            attachments: list[dict] = []

            # Add files
            for index, f in enumerate(files):
                form.append({
                    "name": f"files[{index}]",
                    "value": f.data,
                    "filename": f.filename,
                    "content_type": "application/octet-stream",
                })
                attdata = {
                    "id": index,
                    "filename": f.filename,
                }
                if f.description:
                    attdata["description"] = f.description
                attachments.append(attdata)

            # Add json
            if isinstance(data, dict):
                data["attachments"] = attachments
            form.append({
                "name": "payload_json",
                "value": json.dumps(data),
            })
            data = None

        # Create multipart for forms
        elif multipart:
            raise Exception()

        # Build multipart now
        if files or multipart:
            writer = aiohttp.FormData()
            for v in form:
                writer.add_field(**v)

        # And done
        data_str: bytes | None = None
        if data:
            headers["Content-Type"] = "application/json"
            data_str = json.dumps(data).encode()
        return {
            "data": data_str or writer,
            "headers": headers,
        }

    async def request(
            self,
            route: Route,
            *,
            reason: str | None = None,
            params: dict | None = None,
            data: dict | list | None = None,
            files: list[File] | None = None,
            multipart: bool = False) -> Any:
        """
        Perform a web request.
        """

        args = self.request_params(
            reason=reason,
            data=data,
            files=files,
            multipart=multipart,
        )
        log.debug(
            "Sending {0.method} {0.path} with {1}"
            .format(route, args["data"])
        )
        session = await self.get_session()
        resp: aiohttp.ClientResponse = await session.request(
            route.method,
            route.url,
            params=params,
            **args,
            timeout=5,
        )

        # Parse response
        given: dict[Any, Any] | None
        try:
            given = await resp.json()
        except Exception:
            if resp.ok:
                given = None
            else:
                raise AssertionError("Cannot parse JSON from response.")
        if not resp.ok:
            assert isinstance(given, dict)
            if resp.status == 401:
                raise Unauthorized(given)
            elif resp.status == 404:
                raise NotFound(given)
            else:
                raise HTTPException(given)
        log.debug(
            "Response {0.method} {0.path} returned {1.status} {2}"
            .format(route, resp, given)
        )
        return given

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
                    if item:
                        if isinstance(item[0], (int, str, bool)):
                            updated[updated_key] = [i for i in item]
                        else:
                            updated[updated_key] = [i.value for i in item]
                else:
                    if isinstance(item, (int, str, bool)):
                        updated[updated_key] = item
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
        This assumes each given item is an object implementing a ``._to_json``
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
                    if item:
                        if isinstance(item[0], dict):
                            updated[updated_key] = [i for i in item]
                        else:
                            updated[updated_key] = [i._to_data() for i in item]
                else:
                    if isinstance(item, dict):
                        updated[updated_key] = item
                    else:
                        updated[updated_key] = item._to_data()

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
                if isinstance(item, (str, int, bool, dict)):
                    item = str(item)
                else:
                    item = str(item.value)
            updated[updated_key] = item

        return updated


class OauthHTTPConnection(HTTPConnection):
    AUTH_PREFIX: str = "Bearer"
