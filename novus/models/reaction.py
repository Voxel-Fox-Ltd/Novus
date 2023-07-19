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

from typing import TYPE_CHECKING

from .emoji import PartialEmoji

if TYPE_CHECKING:
    from .. import Message, payloads
    from ..api import HTTPConnection

__all__ = (
    'Reaction',
)


class Reaction:
    """
    A reaction container class.

    Attributes
    ----------
    message : novus.abc.StateSnowflakeWithGuildChannel
        A representation of the message that was reacted on.
    emoji : novus.PartialEmoji
        The emoji that was added to the message. This will only ever be a
        partial emoji (ie it will only have ID, name, and animated attributes
        set).
    burst : bool
        Whether the reaction was a burst reaction or not.
    """

    def __init__(
            self,
            *,
            state: HTTPConnection,
            data: payloads.Reaction,
            message: Message):
        self.state = state
        self.message: Message = message
        self.emoji: PartialEmoji = PartialEmoji(data=data["emoji"])
        self.burst: bool = data.get("burst", False)
