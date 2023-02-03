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

from typing import Any, Callable, Literal

__all__ = (
    'MISSING',
    'add_not_missing',
)


class MissingObject:

    __slots__ = ()

    def __bool__(self) -> Literal[False]:
        return False

    def __repr__(self) -> Literal['MISSING']:
        return 'MISSING'


MISSING: Any = MissingObject()


def add_not_missing(
        kwargs: dict[Any, Any],
        key: str,
        item: Any,
        additional: Callable[..., Any] | None = None) -> None:
    if item is not MISSING:
        if additional is None:
            kwargs[key] = item
        else:
            kwargs[key] = additional(item)
