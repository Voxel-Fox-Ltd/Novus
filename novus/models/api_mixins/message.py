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

from ...utils import ME, MISSING, add_not_missing, try_id

if TYPE_CHECKING:
    from ...api import HTTPConnection
    from ...flags import MessageFlags
    from .. import AllowedMentions, Channel, Embed, Emoji, File, Guild, Sticker, User, abc
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
            components: list[Any] = MISSING,
            message_reference: Message = MISSING,
            stickers: list[Sticker] = MISSING,
            files: list[File] = MISSING,
            flags: MessageFlags = MISSING) -> Message:
        """
        Send a message to the given channel.

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
        components : list[novus.Component]
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
            user: int | abc.Snowflake | ME) -> None:
        """
        Remove a reaction from a message.

        Parameters
        ----------
        emoji : str | novus.Emoji
            The emoji to remove from the message.
        user : int | novus.abc.Snowflake | novus.utils.ME
            The user whose reaction you want to remove.
        """

        if user is ME:
            return await self._state.channel.delete_own_reaction(
                self.channel.id,
                self.id,
                emoji,
            )
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
            content: str = MISSING,
            *,
            tts: bool = MISSING,
            embeds: list[Embed] = MISSING,
            allowed_mentions: AllowedMentions = MISSING,
            components: list[Any] = MISSING,
            message_reference: Message = MISSING,
            stickers: list[Sticker] = MISSING,
            files: list[File] = MISSING,
            flags: MessageFlags = MISSING) -> Message:
        """
        Edit an existing message.

        Parameters
        ----------
        content : str
            The content to be added to the message.
        tts : bool
            Whether the message should be sent with TTS.
        embeds : list[novus.Embed]
            A list of embeds to be added to the message.
        allowed_mentions : novus.AllowedMentions
            An object of users that you want to be pinged.
        components : list[novus.Component]
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
