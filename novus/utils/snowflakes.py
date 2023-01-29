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

from typing import TYPE_CHECKING, overload

if TYPE_CHECKING:
    from ..models.abc import Snowflake

__all__ = (
    "try_snowflake",
    "try_id",
    "try_object",
)


@overload
def try_snowflake(given: str) -> int:
    ...


@overload
def try_snowflake(given: None) -> None:
    ...


def try_snowflake(given: str | None) -> int | None:
    """
    Try and turn a given string into a snowflake, returning ``None`` if the
    given value is ``None``.

    Parameters
    ----------
    given : str | None
        The given "snowflake".

    Returns
    -------
    int | None
        If the given value was castable to an int, that value. Otherwise,
        ``None``.
    """

    if given is None:
        return None
    return int(given)


@overload
def try_id(given: int | Snowflake) -> int:
    ...


@overload
def try_id(given: None) -> None:
    ...


def try_id(given: int | Snowflake | None) -> int | None:
    """
    Get the ID from the given object if it is a snowflake; return the object
    unchanged otherwise.

    Parameters
    ----------
    given : int | novus.models.abc.Snowflake | None
        The object you want an ID from.

    Returns
    -------
    int | None
        The ID from the model if the object is one already (or contains one);
        ``None`` otherwise.
    """

    if given is None:
        return None
    if isinstance(given, int):
        return given
    return given.id


@overload
def try_object(given: int | Snowflake) -> Snowflake:
    ...


@overload
def try_object(given: None) -> None:
    ...


def try_object(given: int | Snowflake | None) -> Snowflake | None:
    """
    Wrap the given ID in a ``novus.models.Object``, or return ``None`` if the
    item is not an int (or if the object is a snowflake already, return it
    unchanged).

    Parameters
    ----------
    given : int | novus.models.abc.Snowflake | None
        The object you want to wrap.

    Returns
    -------
    Snowflake | None
        The wrapped object.
    """

    if given is None:
        return None
    if isinstance(given, int):
        from ..models import Object  # Circular import :(

        return Object(given, state=None)  # type: ignore
    return given
