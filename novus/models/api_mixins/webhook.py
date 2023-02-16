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

from typing import TYPE_CHECKING, Any, Literal, overload

from novus.utils.snowflakes import try_id

from ...utils import MISSING, try_object

if TYPE_CHECKING:
    from ...api import HTTPConnection
    from ...flags import MessageFlags
    from .. import AllowedMentions, Embed, File, Message, Sticker, Webhook
    from ..abc import Snowflake, StateSnowflake

__all__ = (
    'WebhookAPIMixin',
)


class WebhookAPIMixin:

    id: int
    _state: HTTPConnection

    @classmethod
    async def fetch(
            cls,
            state: HTTPConnection,
            id: int,
            token: str | None = None) -> Webhook:
        """
        Get a webhook instance.

        Parameters
        ----------
        state : novus.HTTPConnection
            The API connection.
        id : int
            The ID of the webhook.
        token : str
            The webhook token.

        Returns
        -------
        novus.Webhook
            The webhook instance.
        """

        return await state.webhook.get_webhook(id, token=token)

    async def edit(
            self: StateSnowflake,
            *,
            reason: str | None = None,
            name: str = MISSING,
            avatar: File | None = MISSING,
            channel: int | Snowflake = MISSING) -> Webhook:
        """
        Edit the webhook.

        Parameters
        ----------
        name : str
            The new name of the webhook.
        avatar : novus.File | None
            The avatar of the webhook.
        channel : int | novus.abc.Snowflake
            The channel to move the webhook to.
        reason : str | None
            The reason shown in the audit log.

        Returns
        -------
        novus.Webhook
            The updated webhook instance.
        """

        update: dict[str, Any] = {}
        if name is not MISSING:
            update["name"] = name
        if avatar is not MISSING:
            update["avatar"] = None
            if avatar is not None:
                update["avatar"] = avatar.data
        if channel is not MISSING:
            update["channel"] = try_object(channel)

        return await self._state.webhook.modify_webhook(
            self.id,
            reason=reason,
            **update,
        )

    async def edit_with_token(
            self: StateSnowflake,
            *,
            reason: str | None = None,
            name: str = MISSING,
            avatar: File | None = MISSING) -> Webhook:
        """
        Edit the webhook. Requires the state to have a ``token`` attribute.

        Parameters
        ----------
        name : str
            The new name of the webhook.
        avatar : novus.File | None
            The avatar of the webhook.
        reason : str | None
            The reason shown in the audit log.

        Returns
        -------
        novus.Webhook
            The updated webhook instance.
        """

        update: dict[str, Any] = {}
        if name is not MISSING:
            update["name"] = name
        if avatar is not MISSING:
            update["avatar"] = None
            if avatar is not None:
                update["avatar"] = avatar.data

        return await self._state.webhook.modify_webhook(
            self.id,
            token=self.token,  # pyright: ignore
            reason=reason,
            **update,
        )

    @overload
    async def send(
            self: StateSnowflake,
            content: str,
            *,
            wait: Literal[False],
            thread: int | Snowflake | None,
            tts: bool,
            embeds: list[Embed],
            allowed_mentions: AllowedMentions,
            message_reference: Message,
            stickers: list[Sticker],
            files: list[File],
            flags: MessageFlags,
            ) -> None:
        ...

    @overload
    async def send(
            self: StateSnowflake,
            content: str,
            *,
            wait: Literal[True],
            thread: int | Snowflake | None,
            tts: bool,
            embeds: list[Embed],
            allowed_mentions: AllowedMentions,
            message_reference: Message,
            stickers: list[Sticker],
            files: list[File],
            flags: MessageFlags) -> Message:
        ...

    async def send(
            self: StateSnowflake,
            content: str = MISSING,
            *,
            wait: bool = False,
            thread: int | Snowflake | None = None,
            tts: bool = MISSING,
            embeds: list[Embed] = MISSING,
            components: list[Any] = MISSING,
            allowed_mentions: AllowedMentions = MISSING,
            message_reference: Message = MISSING,
            stickers: list[Sticker] = MISSING,
            files: list[File] = MISSING,
            flags: MessageFlags = MISSING) -> Message | None:
        """
        Send a message to the channel associated with the webhook. Requires a
        token inside of the webhook.

        Parameters
        ----------
        wait : bool
            Whether or not to wait for a message response.
        thread : int | Snowflake | None
            A reference to a thread to send a message in.
        content : str
            The content that you want to have in the message
        tts : bool
            If you want the message to be sent with the TTS flag.
        embeds : list[novus.Embed]
            The embeds you want added to the message.
        components : novus.Component
            The components that you want added to the message.
        allowed_mentions : novus.AllowedMentions
            The mentions you want parsed in the message.
        message_reference : novus.MessageReference
            A reference to a message you want replied to.
        stickers : list[novus.Sticker]
            A list of stickers to add to the message.
        files : list[novus.File]
            A list of files to be sent with the message.
        flags : novus.MessageFlags
            The flags to be sent with the message.
        """

        data: dict[str, Any] = {}

        if content is not MISSING:
            data["content"] = content
        if tts is not MISSING:
            data["tts"] = tts
        if embeds is not MISSING:
            data["embeds"] = embeds
        if components is not MISSING:
            data["components"] = components
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

        return await self._state.webhook.execute_webhook(
            self.id,
            self.token,  # pyright: ignore  # Could be missing token.
            wait=wait,
            thread_id=try_id(thread),
            **data,
        )
