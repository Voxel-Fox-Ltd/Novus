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

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from ..api import HTTPConnection, OauthHTTPConnection
    from .webhook import Webhook

__all__ = (
    'Snowflake',
    'StateSnowflake',
    'StateSnowflakeWithGuild',
    'StateSnowflakeWithChannel',
    'StateSnowflakeWithWebhook',
    'OauthStateSnowflake',
)


@runtime_checkable
class Snowflake(Protocol):
    """
    An ABC that almost all Discord models implement.

    Attributes
    ----------
    id : int
        The model's unique ID.
    """

    id: int


@runtime_checkable
class StateSnowflake(Protocol):
    """
    An ABC for Discord models that has a state attached.

    Attributes
    ----------
    id : int
        The model's unique ID.
    _state : novus.HTTPConection
        The HTTP connection state.
    """

    id: int
    _state: HTTPConnection


@runtime_checkable
class StateSnowflakeWithGuild(Protocol):
    """
    An ABC for Discord models that has a state attached.

    Attributes
    ----------
    id : int
        The model's unique ID.
    _state : novus.HTTPConection
        The HTTP connection state.
    guild: novus.abc.Snowflake
        An object containing the guild ID.
    """

    id: int
    _state: HTTPConnection
    guild: Snowflake


@runtime_checkable
class StateSnowflakeWithChannel(Protocol):
    """
    An ABC for Discord models that has a state attached.

    Attributes
    ----------
    id : int
        The model's unique ID.
    _state : novus.HTTPConection
        The HTTP connection state.
    channel: novus.abc.Snowflake
        An object containing the channel ID.
    """

    id: int
    _state: HTTPConnection
    channel: Snowflake


@runtime_checkable
class StateSnowflakeWithWebhook(Protocol):
    """
    An ABC for Discord models that has a state attached.

    Attributes
    ----------
    id : int
        The model's unique ID.
    _state : novus.HTTPConection
        The HTTP connection state.
    channel: novus.abc.Snowflake
        An object containing the channel ID.
    """

    id: int
    _state: HTTPConnection
    webhook: Webhook


@runtime_checkable
class StateSnowflakeWithGuildChannel(Protocol):
    """
    An ABC for Discord models that has a state attached.

    Attributes
    ----------
    id : int
        The model's unique ID.
    _state : novus.HTTPConection
        The HTTP connection state.
    guild: novus.abc.Snowflake | None
        An object containing the guild ID (or ``None``).
    channel: novus.abc.Snowflake
        An object containing the channel ID.
    """

    id: int
    _state: HTTPConnection
    guild: Snowflake | None
    channel: Snowflake


@runtime_checkable
class OauthStateSnowflake(Protocol):
    """
    An ABC for Discord models that has an oauth state attached.

    Attributes
    ----------
    id : int
        The model's unique ID.
    _state : novus.HTTPConection
        The HTTP connection state.
    """

    id: int
    _state: OauthHTTPConnection
