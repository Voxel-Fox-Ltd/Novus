"""
The MIT License (MIT)

Copyright (c) 2015-2021 Rapptz
Copyright (c) 2021-present Kae Bartlett

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""


from typing import Any, Callable, Coroutine, TYPE_CHECKING, TypeVar, Union


if TYPE_CHECKING:
    from discord import Interaction
    from .context import Context, SlashContext
    from .cog import Cog
    from .errors import CommandError

T = TypeVar('T')

Coro = Coroutine[Any, Any, T]
MaybeCoro = Union[T, Coro[T]]
CoroFunc = Callable[..., Coro[Any]]

AnyContext = Union["Context[Any]", "SlashContext[Any]"]

Check = Union[
    Callable[["Cog", AnyContext], MaybeCoro[bool]],
    Callable[[AnyContext], MaybeCoro[bool]],
]
Hook = Union[
    Callable[["Cog", AnyContext], Coro[Any]],
    Callable[[AnyContext], Coro[Any]],
]
Error = Union[
    Callable[["Cog", AnyContext, "CommandError"], Coro[Any]],
    Callable[[AnyContext, "CommandError"], Coro[Any]],
]
Autocomplete = Union[
    Callable[["Cog", "SlashContext[Any]", "Interaction"], Coro[Any]],
    Callable[["SlashContext[Any]", "Interaction"], Coro[Any]],
]

# Error = Callable[[AnyContext, "CommandError"], Coro[Any]],
# Autocomplete = Callable[["SlashContext[Any]", "Interaction"], Coro[Any]],


# This is merely a tag type to avoid circular import issues.
# Yes, this is a terrible solution but ultimately it is the only solution.
class _BaseCommand:
    __slots__ = ()
