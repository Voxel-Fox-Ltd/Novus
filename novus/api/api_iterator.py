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

from typing import TYPE_CHECKING, Any, AsyncGenerator, Generic, TypeVar

if TYPE_CHECKING:
    from ..utils.types import AnySnowflake

__all__ = (
    'APIIterator',
)


T = TypeVar("T")


class APIIterator(Generic[T]):
    """
    An async iterator class for Discord API methods that return multiple - but
    limited - items in their return.
    """

    __slots__ = (
        'method',
        'before',
        'after',
        'limit',
        'method_limit',
        '_remaining',
    )

    def __init__(
            self,
            method: Any,
            before: AnySnowflake,
            after: AnySnowflake,
            limit: int | None,
            method_limit: int,):
        self.method = method
        self.before = before
        self.after = after
        self.limit = limit
        self.method_limit = method_limit
        self._remaining: int | bool = limit if limit is not None else True

    async def __aiter__(self) -> AsyncGenerator[T, Any]:
        after = self.after

        # Loop either forever or until we hit our limit
        while self._remaining:

            # Work out what our request limit is
            if self._remaining is True:
                limit = self.method_limit
            else:
                # is an int
                limit = min(self.method_limit, self._remaining)

            # Get items from the api
            items: list[T] = await self.method(
                before=self.before,
                after=after,
                limit=limit,
            )

            # Work out our new startpoint
            after = items[-1].id  # type: ignore

            # Yield our just-given items
            for i in items:
                yield i
                if self._remaining is not True:
                    self._remaining -= 1

            # Break out of this if we didn't get the right number of messages
            # (ie if there weren't enough messages available in the API)
            if len(items) != limit:
                break

    async def flatten(self) -> list[T]:
        """
        Flatten the entire item from its original API generator into a list.
        """

        x: list[T] = []
        async for i in self:
            x.append(i)
        return x
