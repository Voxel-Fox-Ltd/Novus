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
    from ..api import HTTPConnection

__all__ = (
    'Snowflake',
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

    __slots__ = ()
    id: int


@runtime_checkable
class StateSnowflake(Protocol):
    """
    An ABC for Discord models that has a state attached.

    Attributes
    ----------
    id : int
        The model's unique ID.
    _state : novus.api.HTTPConection
        The HTTP connection state.
    """

    __slots__ = ()
    id: int
    _state: HTTPConnection
