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

from collections.abc import Iterable
from typing import TYPE_CHECKING, Literal, overload

if TYPE_CHECKING:
    from ..models.abc import Snowflake

__all__ = (
    'try_snowflake',
    'try_id',
    'try_object',
)


@overload
def try_snowflake(given: list[str] | list[int]) -> list[int]:
    ...


@overload
def try_snowflake(given: str | int) -> int:
    ...


@overload
def try_snowflake(given: None) -> None:
    ...


def try_snowflake(given: str | int | list[str] | list[int] | None) -> int | list[int] | None:
    """
    Try and turn a given string into a snowflake, returning ``None`` if the
    given value is ``None``.

    Parameters
    ----------
    given : str | int | list[str] | list[int] | None
        The given "snowflake".

    Returns
    -------
    int | list[int] | None
        If the given value was castable to an int, that value. Otherwise,
        ``None``.
    """

    if given is None:
        return None
    if isinstance(given, (int, str)):
        return int(given)
    return [int(i) for i in given]


@overload
def try_id(given: Literal[None]) -> None:
    ...


@overload
def try_id(given: int | Snowflake | str) -> int:
    ...


@overload
def try_id(given: list[int] | list[Snowflake] | list[str]) -> list[int]:
    ...


def try_id(given: int | Snowflake | str | list[int] | list[str] | list[Snowflake] | None) -> int | list[int] | None:
    """
    Get the ID from the given object if it is a snowflake; return the object
    unchanged otherwise.

    Parameters
    ----------
    given : int | novus.abc.Snowflake | str | None
        The object you want an ID from.

    Returns
    -------
    int | None
        The ID from the model if the object is one already (or contains one);
        ``None`` otherwise.
    """

    if given is None:
        return None
    elif isinstance(given, list):
        if not given:
            return []
        builder = []
        for i in given:
            if isinstance(i, (int, str)):
                builder.append(int(i))
            else:
                builder.append(i.id)
        return builder
    elif isinstance(given, (int, str)):
        return int(given)
    return given.id


@overload
def try_object(given: int | str | Snowflake) -> Snowflake:
    ...


@overload
def try_object(given: None) -> None:
    ...


def try_object(given: int | str | Snowflake | None) -> Snowflake | None:
    """
    Wrap the given ID in a ``novus.Object``, or return ``None`` if the
    item is not an int (or if the object is a snowflake already, return it
    unchanged).

    Parameters
    ----------
    given : int | novus.abc.Snowflake | None
        The object you want to wrap.

    Returns
    -------
    Snowflake | None
        The wrapped object.
    """

    if given is None:
        return None
    if isinstance(given, (int, str)):
        from ..models import Object  # Circular import :(
        return Object(given, state=None)  # pyright: ignore
    return given
