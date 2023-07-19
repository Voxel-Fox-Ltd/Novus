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

import functools
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Protocol, runtime_checkable

from .. import flags
from ..utils import MISSING

if TYPE_CHECKING:
    from ..api import HTTPConnection, OauthHTTPConnection
    from . import ActionRow, AllowedMentions, Embed, File, Message, Sticker, Webhook

__all__ = (
    'Snowflake',
    'StateSnowflake',
    'StateSnowflakeWithGuild',
    'StateSnowflakeWithChannel',
    'StateSnowflakeWithWebhook',
    'OauthStateSnowflake',
    'EqualityComparable',
    'Hashable',
    'Messageable',
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
    state : novus.HTTPConection
        The HTTP connection state.
    """

    id: int
    state: HTTPConnection


@runtime_checkable
class StateSnowflakeWithGuild(Protocol):
    """
    An ABC for Discord models that has a state attached.

    Attributes
    ----------
    id : int
        The model's unique ID.
    state : novus.HTTPConection
        The HTTP connection state.
    guild: novus.abc.Snowflake
        An object containing the guild ID.
    """

    id: int
    state: HTTPConnection
    guild: Snowflake


@runtime_checkable
class StateSnowflakeWithChannel(Protocol):
    """
    An ABC for Discord models that has a state attached.

    Attributes
    ----------
    id : int
        The model's unique ID.
    state : novus.HTTPConection
        The HTTP connection state.
    channel: novus.abc.Snowflake
        An object containing the channel ID.
    """

    id: int
    state: HTTPConnection
    channel: Snowflake


@runtime_checkable
class StateSnowflakeWithWebhook(Protocol):
    """
    An ABC for Discord models that has a state attached.

    Attributes
    ----------
    id : int
        The model's unique ID.
    state : novus.HTTPConection
        The HTTP connection state.
    channel: novus.abc.Snowflake
        An object containing the channel ID.
    """

    id: int
    state: HTTPConnection
    webhook: Webhook


@runtime_checkable
class StateSnowflakeWithGuildChannel(Protocol):
    """
    An ABC for Discord models that has a state attached.

    Attributes
    ----------
    id : int
        The model's unique ID.
    state : novus.HTTPConection
        The HTTP connection state.
    guild: novus.abc.Snowflake | None
        An object containing the guild ID (or ``None``).
    channel: novus.abc.Snowflake
        An object containing the channel ID.
    """

    id: int
    state: HTTPConnection
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
    state : novus.HTTPConection
        The HTTP connection state.
    """

    id: int
    state: OauthHTTPConnection


class EqualityComparable:

    __slots__ = ()

    id: int

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, self.__class__)
            and other.id == self.id
        )

    def __ne__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            return other.id != self.id
        return True


class Hashable(EqualityComparable):

    __slots__ = ()

    def __hash__(self) -> int:
        return self.id >> 22


class Messageable(StateSnowflake):
    """
    Any object that acts as a "channel" that can be sent to.
    """

    id: int
    state: HTTPConnection

    async def _get_send_method(self) -> Callable[..., Awaitable[Any]]:
        """
        Return a snowflake implementation with the ID of the channel, and the
        sendable method.
        """

        return functools.partial(self.state.channel.create_message, self.id)

    async def send(
            self,
            content: str = MISSING,
            *,
            tts: bool = MISSING,
            embeds: list[Embed] = MISSING,
            allowed_mentions: AllowedMentions = MISSING,
            components: list[ActionRow] = MISSING,
            message_reference: Message = MISSING,
            stickers: list[Sticker] = MISSING,
            files: list[File] = MISSING,
            flags: flags.MessageFlags = MISSING) -> Message:
        """
        Send a message to the channel associated with the model.

        Parameters
        ----------
        content : str
            The content that you want to have in the message
        tts : bool
            If you want the message to be sent with the TTS flag.
        embeds : list[novus.Embed]
            The embeds you want added to the message.
        allowed_mentions : novus.AllowedMentions
            The mentions you want parsed in the message.
        components : list[novus.ActionRow]
            A list of action rows to be added to the message.
        message_reference : novus.Message
            A reference to a message you want replied to.
        stickers : list[novus.Sticker]
            A list of stickers to add to the message.
        files : list[novus.File]
            A list of files to be sent with the message.
        flags : novus.MessageFlags
            The flags to be sent with the message.
        """

        send_method = await self._get_send_method()

        data: dict[str, Any] = {}

        if content is not MISSING:
            data["content"] = content
        if tts is not MISSING:
            data["tts"] = tts
        if embeds is not MISSING:
            data["embeds"] = embeds
        if allowed_mentions is not MISSING:
            data["allowed_mentions"] = allowed_mentions
        if components is not MISSING:
            data["components"] = components
        if message_reference is not MISSING:
            data["message_reference"] = message_reference
        if stickers is not MISSING:
            data["stickers"] = stickers
        if files is not MISSING:
            data["files"] = files
        if flags is not MISSING:
            data["flags"] = flags

        return await send_method(**data)
