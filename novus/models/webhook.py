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

import re
from typing import TYPE_CHECKING, Any, Literal, Protocol, overload

from typing_extensions import override

from ..utils import (
    MISSING,
    cached_slot_property,
    generate_repr,
    try_id,
    try_object,
    try_snowflake,
)
from .asset import Asset

if TYPE_CHECKING:
    from ..api import HTTPConnection
    from ..flags import MessageFlags
    from ..payloads import Webhook as WebhookPayload
    from . import ActionRow, AllowedMentions, Embed, File, Message, Sticker, abc

__all__ = (
    'Webhook',
    'InteractionWebhook',
)


class StateSnowflakeWithToken(Protocol):
    id: int
    state: HTTPConnection
    token: str


class Webhook:
    """
    A model for a webhook instance.

    Attributes
    ----------
    id: int
        The ID of the webhook.
    guild_id: int | None
        The guild ID this webhook is for, if any.
    channel_id: int | None
        The channel ID this webhook is for, if any.
    name: str | None
        The default of the webhook.
    avatar_hash: str | None
        The hash associated with the user avatar.
    avatar: novus.Asset | None
        The avatar asset associated with the hash.
    token: str | None
        The token of the webhook.
    """

    WEBHOOK_REGEX = re.compile(
        r"discord(?:app)?\.com\/api\/webhooks\/"  # base and path
        + r"(?P<id>\d{16,23})"  # webhook ID
        + r"(?:\/(?P<token>[a-zA-Z0-9\-_]{0,80}))?"  # webhook token
    )

    __slots__ = (
        'state',
        'id',
        'guild_id',
        'channel_id',
        'name',
        'avatar_hash',
        'token',
        '_cs_avatar',
    )

    def __init__(self, *, state: HTTPConnection, data: WebhookPayload):
        self.state = state
        self.id: int = try_snowflake(data['id'])
        self.guild_id: int | None = try_snowflake(data.get('guild_id'))
        self.channel_id: int | None = try_snowflake(data.get('channel_id'))
        self.name: str | None = data.get('name')
        self.avatar_hash: str | None = data.get('avatar')
        self.token: str | None = data.get('token')

    __repr__ = generate_repr(("id",))

    @cached_slot_property('_cs_avatar')
    def avatar(self) -> Asset:
        return Asset.from_user_avatar(self)

    @classmethod
    def partial(
            cls,
            id: str | int,
            token: str | None = None,
            *,
            state: HTTPConnection | None = None) -> Webhook:
        """
        Create a partial webhook state, allowing you to run webhook API methods.

        Parameters
        ----------
        id : str | int
            The ID of the webhook.
        token : str | None
            The auth token for the webhook.
        state : HTTPConnection | None
            The API connection, if one is made. Passing this enables API
            methods to be run on returned objects (eg a `Message.guild` from a
            message returned by executing a webhook).
            If no state is provided, one will be created for you to enable the
            sending of messages.

        Returns
        -------
        novus.Webhook
            The created webhook instance.
        """

        from ..api import HTTPConnection  # Circular imports my beloved
        data = {
            "id": id,
            "token": token,
        }
        return cls(
            state=state or HTTPConnection(),
            data=data,
        )

    @classmethod
    def from_url(
            cls,
            url: str,
            state: HTTPConnection | None = None) -> Webhook:
        """
        Get a webhook object from a valid Discord URL. This won't get attributes
        like the name or channel ID, but will allow you to run API methods with
        the object.

        Parameters
        ----------
        url : str
            The URL of the webhook.
        state : HTTPConnection | None
            The API connection, if one is made. Passing this enables API
            methods to be run on returned objects (eg a `Message.guild` from a
            message returned by executing a webhook).
            If no state is provided, one will be created for you to enable the
            sending of messages.

        Returns
        -------
        novus.Webhook
            The created webhook instance.

        Raises
        ------
        ValueError
            The provided URL is not valid.
        """

        match = cls.WEBHOOK_REGEX.search(url)
        if match is None:
            raise ValueError("Invalid webhook URL")
        return cls.partial(
            id=match.group("id"),
            token=match.group("token"),
            state=state,
        )

    # API methods

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
            self: StateSnowflakeWithToken,
            *,
            reason: str | None = None,
            name: str = MISSING,
            avatar: File | None = MISSING,
            channel: int | abc.Snowflake = MISSING) -> Webhook:
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

        return await self.state.webhook.modify_webhook(
            self.id,
            reason=reason,
            **update,
        )

    async def edit_with_token(
            self: StateSnowflakeWithToken,
            *,
            reason: str | None = None,
            name: str = MISSING,
            avatar: File | None = MISSING) -> Webhook:
        """
        Edit the webhook.

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

        return await self.state.webhook.modify_webhook(
            self.id,
            token=self.token,  # pyright: ignore
            reason=reason,
            **update,
        )

    @overload
    async def send(
            self: StateSnowflakeWithToken,
            content: str,
            *,
            wait: Literal[False] = False,
            thread: int | abc.Snowflake | None,
            tts: bool,
            embeds: list[Embed],
            components: list[ActionRow] = MISSING,
            allowed_mentions: AllowedMentions,
            message_reference: Message,
            stickers: list[Sticker],
            files: list[File],
            flags: MessageFlags) -> None:
        ...

    @overload
    async def send(
            self: StateSnowflakeWithToken,
            content: str,
            *,
            wait: Literal[True] = True,
            thread: int | abc.Snowflake | None,
            tts: bool,
            embeds: list[Embed],
            components: list[ActionRow] = MISSING,
            allowed_mentions: AllowedMentions,
            message_reference: Message,
            stickers: list[Sticker],
            files: list[File],
            flags: MessageFlags) -> Message:
        ...

    async def send(
            self: StateSnowflakeWithToken,
            content: str = MISSING,
            *,
            wait: bool = False,
            thread: int | abc.Snowflake | None = None,
            tts: bool = MISSING,
            embeds: list[Embed] = MISSING,
            components: list[ActionRow] = MISSING,
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
        components : list[novus.ActionRow]
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

        return await self.state.webhook.execute_webhook(
            self.id,
            self.token,
            wait=wait,
            thread_id=try_id(thread),
            **data,
        )


class InteractionWebhook(Webhook):

    @override
    async def send(  # type: ignore
            self: StateSnowflakeWithToken,
            content: str = MISSING,
            *,
            tts: bool = MISSING,
            embeds: list[Embed] = MISSING,
            components: list[ActionRow] = MISSING,
            allowed_mentions: AllowedMentions = MISSING,
            message_reference: Message = MISSING,
            stickers: list[Sticker] = MISSING,
            files: list[File] = MISSING,
            flags: MessageFlags = MISSING,
            ephemeral: bool = False) -> Message | None:
        """
        Send a message to the channel associated with the webhook. Requires a
        token inside of the webhook.

        Parameters
        ----------
        content : str
            The content that you want to have in the message
        tts : bool
            If you want the message to be sent with the TTS flag.
        embeds : list[novus.Embed]
            The embeds you want added to the message.
        components : list[novus.ActionRow]
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
        if flags is MISSING:
            data["flags"] = MessageFlags()
        else:
            data["flags"] = flags
        if ephemeral:
            data["flags"].ephemeral = True

        return await self.state.webhook.execute_webhook(
            self.id,
            self.token,
            wait=True,
            **data,
        )
