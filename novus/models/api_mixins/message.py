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

from typing import TYPE_CHECKING, Any, Literal

from ...utils import MISSING, add_not_missing, try_id

if TYPE_CHECKING:
    from ...api import HTTPConnection
    from ...flags import MessageFlags
    from .. import (
        ActionRow,
        AllowedMentions,
        Channel,
        Embed,
        Emoji,
        File,
        Guild,
        Sticker,
        Thread,
        User,
        abc,
    )
    from .. import api_mixins as amix
    from ..message import Message

__all__ = (
    'MessageAPIMixin',
)


class MessageAPIMixin:

    id: int
    _state: HTTPConnection
    channel: Channel
    guild: Guild | amix.GuildAPIMixin | None

    @classmethod
    async def create(
            cls,
            state: HTTPConnection,
            channel: int | abc.Snowflake,
            content: str = MISSING,
            *,
            tts: bool = MISSING,
            embeds: list[Embed] = MISSING,
            allowed_mentions: AllowedMentions = MISSING,
            components: list[ActionRow] = MISSING,
            message_reference: Message = MISSING,
            stickers: list[Sticker] = MISSING,
            files: list[File] = MISSING,
            flags: MessageFlags = MISSING) -> Message:
        """
        Send a message to the given channel.

        .. seealso:: :func:`novus.Channel.send`

        Parameters
        ----------
        state : novus.api.HTTPConnection
            The API connection.
        channel : int | novus.abc.Snowflake
            The channel to send the message to.
        content : str
            The content to be added to the message.
        tts : bool
            Whether the message should be sent with TTS.
        embeds : list[novus.Embed]
            A list of embeds to be added to the message.
        allowed_mentions : novus.AllowedMentions
            An object of users that you want to be pinged.
        components : list[novus.ActionRow]
            A list of components to add to the message.
        message_reference : novus.Message
            A message to reply to.
        stickers : list[novus.Sticker]
            A list of stickers to add to the message.
        files : list[novus.File]
            A list of files to be added to the message.
        flags : novus.MessageFlags
            Message send flags.

        Returns
        -------
        novus.Message
            The created message.
        """

        update: dict[str, Any] = {}
        add_not_missing(update, "content", content)
        add_not_missing(update, "tts", tts)
        add_not_missing(update, "embeds", embeds)
        add_not_missing(update, "allowed_mentions", allowed_mentions)
        add_not_missing(update, "components", components)
        add_not_missing(update, "message_reference", message_reference)
        add_not_missing(update, "stickers", stickers)
        add_not_missing(update, "files", files)
        add_not_missing(update, "flags", flags)
        return await state.channel.create_message(
            try_id(channel),
            **update,
        )

    @classmethod
    async def fetch(
            cls,
            state: HTTPConnection,
            channel: int | abc.Snowflake,
            message: int | abc.Snowflake) -> Message:
        """
        Get an existing message.

        .. seealso:: :func:`novus.Channel.fetch_message`

        Parameters
        ----------
        state : novus.api.HTTPConnection
            The API connection.
        channel : int | novus.abc.Snowflake
            The channel to send the message to.
        message : int | novus.abc.Snowflake
            The message you want to get.

        Returns
        -------
        novus.Message
            The created message.
        """

        return await state.channel.get_channel_message(
            try_id(channel),
            try_id(message),
        )

    async def delete(
            self: abc.StateSnowflakeWithChannel,
            *,
            reason: str | None = None) -> None:
        """
        Delete a message.

        Parameters
        ----------
        reason: str | None
            The reason to be added to the audit log.
        """

        return await self._state.channel.delete_message(
            self.channel.id,
            self.id,
            reason=reason,
        )

    async def crosspost(self: abc.StateSnowflakeWithChannel) -> Message:
        """
        Crosspost a message.
        """

        return await self._state.channel.crosspost_message(
            self.channel.id,
            self.id,
        )

    async def add_reaction(
            self: abc.StateSnowflakeWithChannel,
            emoji: str | Emoji) -> None:
        """
        Add a reaction to a message.

        Parameters
        ----------
        emoji : str | novus.Emoji
            The emoji to add to the message.
        """

        return await self._state.channel.create_reaction(
            self.channel.id,
            self.id,
            emoji,
        )

    async def remove_reaction(
            self: abc.StateSnowflakeWithChannel,
            emoji: str | Emoji,
            user: int | abc.Snowflake) -> None:
        """
        Remove a reaction from a message.

        Parameters
        ----------
        emoji : str | novus.Emoji
            The emoji to remove from the message.
        user : int | novus.abc.Snowflake
            The user whose reaction you want to remove.
        """

        # if user is ME:
        #     return await self._state.channel.delete_own_reaction(
        #         self.channel.id,
        #         self.id,
        #         emoji,
        #     )
        return await self._state.channel.delete_user_reaction(
            self.channel.id,
            self.id,
            emoji,
            try_id(user),
        )

    async def fetch_reactions(
            self: abc.StateSnowflakeWithChannel,
            emoji: str | Emoji) -> list[User]:
        """
        Get a list of users who reacted to a message.

        Parameters
        ----------
        emoji : str | novus.Emoji
            The emoji to check the reactors for.
        """

        return await self._state.channel.get_reactions(
            self.channel.id,
            self.id,
            emoji,
        )

    async def clear_reactions(
            self: abc.StateSnowflakeWithChannel,
            emoji: str | Emoji | None = None) -> None:
        """
        Remove all of the reactions for a given message.

        Parameters
        ----------
        emoji : str | novus.Emoji | None
            The specific emoji that you want to clear. If not given, all
            reactions will be cleared.
        """

        if emoji is not None:
            return await self._state.channel.delete_all_reactions_for_emoji(
                self.channel.id,
                self.id,
                emoji,
            )
        return await self._state.channel.delete_all_reactions(
            self.channel.id,
            self.id,
        )

    async def edit(
            self: abc.StateSnowflakeWithChannel,
            content: str | None = MISSING,
            *,
            tts: bool = MISSING,
            embeds: list[Embed] | None = MISSING,
            allowed_mentions: AllowedMentions = MISSING,
            components: list[ActionRow] | None = MISSING,
            message_reference: Message | None = MISSING,
            stickers: list[Sticker] | None = MISSING,
            files: list[File] | None = MISSING,
            flags: MessageFlags = MISSING) -> Message:
        """
        Edit an existing message.

        Parameters
        ----------
        content : str | None
            The content to be added to the message.
        tts : bool
            Whether the message should be sent with TTS.
        embeds : list[novus.Embed] | None
            A list of embeds to be added to the message.
        allowed_mentions : novus.AllowedMentions
            An object of users that you want to be pinged.
        components : list[novus.ActionRow] | None
            A list of components to add to the message.
        message_reference : novus.Message | None
            A message to reply to.
        stickers : list[novus.Sticker] | None
            A list of stickers to add to the message.
        files : list[novus.File] | None
            A list of files to be added to the message.
        flags : novus.MessageFlags
            Message send flags.

        Returns
        -------
        novus.Message
            The edited message.
        """

        update: dict[str, Any] = {}
        add_not_missing(update, "content", content)
        add_not_missing(update, "tts", tts)
        add_not_missing(update, "embeds", embeds)
        add_not_missing(update, "allowed_mentions", allowed_mentions)
        add_not_missing(update, "components", components)
        add_not_missing(update, "message_reference", message_reference)
        add_not_missing(update, "stickers", stickers)
        add_not_missing(update, "files", files)
        add_not_missing(update, "flags", flags)
        return await self._state.channel.edit_message(
            self.channel.id,
            self.id,
            **update,
        )

    async def pin(
            self: abc.StateSnowflakeWithChannel,
            *,
            reason: str | None = None) -> None:
        """
        Pin the message to the channel.

        Parameters
        ----------
        reason : str | None
            The reason shown in the audit log.
        """

        await self._state.channel.pin_message(
            self.channel.id,
            self.id,
            reason=reason,
        )

    async def unpin(
            self: abc.StateSnowflakeWithChannel,
            *,
            reason: str | None = None) -> None:
        """
        Unpin a message from the channel.

        Parameters
        ----------
        reason : str | None
            The reason shown in the audit log.
        """

        await self._state.channel.unpin_message(
            self.channel.id,
            self.id,
            reason=reason,
        )

    async def create_thread(
            self: abc.StateSnowflakeWithChannel,
            name: str,
            *,
            reason: str | None = None,
            auto_archive_duration: Literal[60, 1_440, 4_320, 10_080] = MISSING,
            rate_limit_per_user: int = MISSING) -> Thread:
        """
        Create a thread from the message.

        Parameters
        ----------
        name : str
            The name of the thread.
        auto_archive_duration : int
            The auto archive duration for the thread.
        rate_limit_per_user : int
            The number of seconds a user has to wait before sending another
            message.
        reason : str | None
            The reason shown in the audit log.
        """

        params: dict[str, str | int] = {}
        params["name"] = name
        add_not_missing(params, "auto_archive_duration", auto_archive_duration)
        add_not_missing(params, "rate_limit_per_user", rate_limit_per_user)
        return await self._state.channel.start_thread_from_message(
            self.channel.id,
            self.id,
            reason=reason,
            **params,
        )


class WebhookMessageAPIMixin:

    @classmethod
    async def fetch(
            cls,
            state: HTTPConnection,
            webhook: int | abc.Snowflake,
            webhook_token: str,
            message: int | abc.Snowflake) -> Message:
        """
        Get an existing message using the webhook.

        Parameters
        ----------
        state : novus.api.HTTPConnection
            The API connection.
        webhook : int | novus.abc.Snowflake
            The webhook that sent the message.
        webhook_token : str
            The token associated with the webhook.
        message : int | novus.abc.Snowflake
            The message you want to get.

        Returns
        -------
        novus.Message
            The created message.
        """

        return await state.webhook.get_webhook_message(
            try_id(webhook),
            webhook_token,
            try_id(message),
        )

    async def delete(
            self: abc.StateSnowflakeWithWebhook) -> None:
        """
        Delete a webhook message.

        Parameters
        ----------
        webhook : int | novus.abc.Snowflake
            The webhook that sent the message.
        webhook_token : str
            The token associated with the webhook.
        message : int | novus.abc.Snowflake
            The message you want to delete.
        """

        return await self._state.webhook.delete_webhook_message(
            self.webhook.id,
            self.webhook.token,  # pyright: ignore
            self.id,
        )

    async def edit(
            self: abc.StateSnowflakeWithWebhook,
            content: str | None = MISSING,
            *,
            tts: bool = MISSING,
            embeds: list[Embed] | None = MISSING,
            allowed_mentions: AllowedMentions = MISSING,
            components: list[ActionRow] | None = MISSING,
            message_reference: Message | None = MISSING,
            stickers: list[Sticker] | None = MISSING,
            files: list[File] | None = MISSING,
            flags: MessageFlags = MISSING) -> Message:
        """
        Edit an existing message sent by the webhook.

        Parameters
        ----------
        content : str | None
            The content to be added to the message.
        tts : bool
            Whether the message should be sent with TTS.
        embeds : list[novus.Embed] | None
            A list of embeds to be added to the message.
        allowed_mentions : novus.AllowedMentions
            An object of users that you want to be pinged.
        components : list[novus.ActionRow] | None
            A list of components to add to the message.
        message_reference : novus.Message | None
            A message to reply to.
        stickers : list[novus.Sticker] | None
            A list of stickers to add to the message.
        files : list[novus.File] | None
            A list of files to be added to the message.
        flags : novus.MessageFlags
            Message send flags.

        Returns
        -------
        novus.Message
            The edited message.
        """

        update: dict[str, Any] = {}
        add_not_missing(update, "content", content)
        add_not_missing(update, "tts", tts)
        add_not_missing(update, "embeds", embeds)
        add_not_missing(update, "allowed_mentions", allowed_mentions)
        add_not_missing(update, "components", components)
        add_not_missing(update, "message_reference", message_reference)
        add_not_missing(update, "stickers", stickers)
        add_not_missing(update, "files", files)
        add_not_missing(update, "flags", flags)
        return await self._state.webhook.edit_webhook_message(
            self.webhook.id,
            self.webhook.token,  # pyright: ignore
            self.id,
            **update,
        )
