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

from ..utils import MISSING

if TYPE_CHECKING:
    from ..api import HTTPConnection
    from ..flags import MessageFlags
    from .message import AllowedMentions, Embed, File, Message
    from .sticker import Sticker

__all__ = (
    "EqualityComparable",
    "Hashable",
    "Messageable",
)


class EqualityComparable:

    __slots__ = ()

    id: int

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and other.id == self.id

    def __ne__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            return other.id != self.id
        return True


class Hashable(EqualityComparable):

    __slots__ = ()

    def __hash__(self) -> int:
        return self.id >> 22


class Messageable:
    """
    A mixin that allows for sending messages.
    """

    _state: HTTPConnection

    async def _get_channel(self) -> int:
        raise NotImplementedError()

    async def send(
        self,
        content: str = MISSING,
        *,
        tts: bool = MISSING,
        embeds: list[Embed] = MISSING,
        allowed_mentions: AllowedMentions = MISSING,
        message_reference: Message = MISSING,
        stickers: list[Sticker] = MISSING,
        files: list[File] = MISSING,
        flags: MessageFlags = MISSING,
    ) -> Message:
        """
        Send a message to the channel associated with the model.

        Parameters
        ----------
        content : str
            The content that you want to have in the message
        tts : bool
            If you want the message to be sent with the TTS flag.
        embeds : list[novus.models.Embed]
            The embeds you want added to the message.
        allowed_mentions : novus.models.AllowedMentions
            The mentions you want parsed in the message.
        message_reference : novus.models.MessageReference
            A reference to a message you want replied to.
        stickers : list[novus.models.Sticker]
            A list of stickers to add to the message.
        files : list[novus.models.File]
            A list of files to be sent with the message.
        flags : novus.flags.MessageFlags
            The flags to be sent with the message.
        """

        channel_id = await self._get_channel()

        data: dict[str, Any] = {}

        if content is not MISSING:
            data["content"] = content
        if tts is not MISSING:
            data["tts"] = tts
        if embeds is not MISSING:
            data["embeds"] = embeds
        if allowed_mentions is not MISSING:
            data["allowed_mentions"] = allowed_mentions
        if message_reference is not MISSING:
            data["message_reference"] = message_reference
        if stickers is not MISSING:
            data["stickers"] = stickers
        if files is not MISSING:
            data["files"] = files
        if flags is not MISSING:
            data["flags"] = flags

        return await self._state.channel.create_message(
            channel_id,
            data,
        )
