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

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..api import HTTPConnection
    from ..payloads import Message as MessagePayload

__all__ = (
    'MessageReference',
    'Message',
    'AllowedMentions',
)


class MessageReference:

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...


class Message:

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...


class AllowedMentions:

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...
