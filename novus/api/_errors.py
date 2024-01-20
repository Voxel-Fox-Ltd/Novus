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

from collections import defaultdict
from typing import ClassVar, Type

__all__ = (
    'HTTPException',
    'NotFound',
    'Unauthorized',
    'BadRequest',
    'Forbidden',
    'GatewayException',
    'GatewayUnknownError',
    'GatewayUnknownOpcode',
    'GatewayDecodeError',
    'GatewayNotAuthenticated',
    'GatewayAuthenticationFailed',
    'GatewayAlreadyAuthenticated',
    'GatewayInvalidSeq',
    'GatewayRateLimited',
    'GatewaySessionTimeout',
    'GatewayInvalidShard',
    'GatewayShardingRequired',
    'GatewayInvalidAPIVersion',
    'GatewayInvalidIntents',
    'GatewayDisallowedIntents',
    'GatewayClose',
    'GatewayClosed',
)


class HTTPException(Exception):
    """
    Generic base class for all HTTP errors.
    """

    def __init__(self, payload: dict):
        self.payload: dict = payload
        self.message: str = payload['message']
        self.code: int = payload.get('code', -1)


class BadRequest(HTTPException):
    """When we're sending invalid data over to Discord."""


class NotFound(HTTPException):
    """When a resource cannot be found on the server."""


class Unauthorized(HTTPException):
    """When you are missing relevant permissions to access a resource."""


class Forbidden(HTTPException):
    """When you are missing relevant permissions to access a resource."""


class RateLimitExceeded(HTTPException):
    """A rate limit has been exceeded."""


class DiscordException(HTTPException):
    """A 5xx error from Discord was returned."""


class GatewayException(Exception):
    """When you get a generic gateway exception."""
    code: ClassVar[int] = 0
    reconnect: ClassVar[bool] = False
    all_exceptions: ClassVar[dict[int, Type[Exception]]] = {}


class GatewayUnknownError(GatewayException):
    """Unknown error."""
    code = 4000
    reconnect = True


class GatewayUnknownOpcode(GatewayException):
    """Unknown error."""
    code = 4001
    reconnect = True


class GatewayDecodeError(GatewayException):
    """Sent invalid payload to Discord."""
    code = 4002
    reconnect = True


class GatewayNotAuthenticated(GatewayException):
    """Sent a payload prior to identify."""
    code = 4003
    reconnect = True


class GatewayAuthenticationFailed(GatewayException):
    """If you try and identify with an invalid token."""
    code = 4004
    reconnect = False


class GatewayAlreadyAuthenticated(GatewayException):
    """Sent more than one identify payload."""
    code = 4005
    reconnect = True


class GatewayInvalidSeq(GatewayException):
    """Invalid sequence number sent on resume."""
    code = 4007
    reconnect = True


class GatewayRateLimited(GatewayException):
    """Rate limit."""
    code = 4008
    reconnect = True


class GatewaySessionTimeout(GatewayException):
    """Session timed out."""
    code = 4009
    reconnect = True


class GatewayInvalidShard(GatewayException):
    """Invalid shard in identify."""
    code = 4010
    reconnect = False


class GatewayShardingRequired(GatewayException):
    """Session would have handled too many guilds."""
    code = 4011
    reconnect = False


class GatewayInvalidAPIVersion(GatewayException):
    """Connected to an invalid API version."""
    code = 4012
    reconnect = False


class GatewayInvalidIntents(GatewayException):
    """Invalid intent number."""
    code = 4013
    reconnect = False


class GatewayDisallowedIntents(GatewayException):
    """Disallowed intents."""
    code = 4014
    reconnect = False


class GatewayClose(GatewayException):
    """Gateway is closing."""


class GatewayClosed(GatewayClose):
    """Gateway has been closed. A subclass of GatewayClose."""


GatewayException.all_exceptions = defaultdict(lambda: GatewayException)
GatewayException.all_exceptions[GatewayUnknownError.code] = GatewayUnknownError
GatewayException.all_exceptions[GatewayUnknownOpcode.code] = GatewayUnknownOpcode
GatewayException.all_exceptions[GatewayDecodeError.code] = GatewayDecodeError
GatewayException.all_exceptions[GatewayNotAuthenticated.code] = GatewayNotAuthenticated
GatewayException.all_exceptions[GatewayAuthenticationFailed.code] = GatewayAuthenticationFailed
GatewayException.all_exceptions[GatewayAlreadyAuthenticated.code] = GatewayAlreadyAuthenticated
GatewayException.all_exceptions[GatewayInvalidSeq.code] = GatewayInvalidSeq
GatewayException.all_exceptions[GatewayRateLimited.code] = GatewayRateLimited
GatewayException.all_exceptions[GatewaySessionTimeout.code] = GatewaySessionTimeout
GatewayException.all_exceptions[GatewayInvalidShard.code] = GatewayInvalidShard
GatewayException.all_exceptions[GatewayShardingRequired.code] = GatewayShardingRequired
GatewayException.all_exceptions[GatewayInvalidAPIVersion.code] = GatewayInvalidAPIVersion
GatewayException.all_exceptions[GatewayInvalidIntents.code] = GatewayInvalidIntents
GatewayException.all_exceptions[GatewayDisallowedIntents.code] = GatewayDisallowedIntents
