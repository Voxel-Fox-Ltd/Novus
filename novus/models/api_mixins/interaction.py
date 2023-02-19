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

from ...enums import InteractionResponseType
from ...utils import MISSING

if TYPE_CHECKING:
    from ... import (
        ActionRow,
        AllowedMentions,
        ApplicationCommandChoice,
        Embed,
        File,
        Interaction,
        Message,
        Sticker,
        flags,
    )

__all__ = (
    'InteractionAPIMixin',
)


Modal = Any


class InteractionAPIMixin:

    async def pong(self: Interaction) -> None:
        """
        Send a pong interaction response.
        """

        await self.state.interaction.create_interaction_response(
            self.id,
            self.token,
            InteractionResponseType.pong,
        )

    async def send(
            self: Interaction,
            content: str = MISSING,
            *,
            tts: bool = MISSING,
            embeds: list[Embed] = MISSING,
            allowed_mentions: AllowedMentions = MISSING,
            components: list[ActionRow] = MISSING,
            message_reference: Message = MISSING,
            stickers: list[Sticker] = MISSING,
            files: list[File] = MISSING,
            flags: flags.MessageFlags = MISSING,
            ephemeral: bool = False) -> None:
        """
        Send a message associated with the interaction response.

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
        ephemeral : bool
            Whether the message should be sent so only the calling user can see
            it.
            This is ignored if this is the first message you're sending
            relating to this interaction and you've previously deferred.
        """

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
        if ephemeral is not MISSING:
            data["ephemeral"] = ephemeral

        if self._responded is False:
            await self.state.interaction.create_interaction_response(
                self.id,
                self.token,
                InteractionResponseType.channel_message_with_source,
                data,
            )
            self._responded = True
        else:
            await self.state.interaction.create_followup_message(
                self.application_id,
                self.token,
                **data,
            )
        return

    async def defer(self: Interaction) -> None:
        """
        Send a defer response.
        """

        await self.state.interaction.create_interaction_response(
            self.id,
            self.token,
            InteractionResponseType.deferred_channel_message_with_source,
        )
        self._responded = True

    async def defer_update(self: Interaction) -> None:
        """
        Send a defer update response.
        """

        await self.state.interaction.create_interaction_response(
            self.id,
            self.token,
            InteractionResponseType.deferred_update_message,
        )
        self._responded = True

    async def update(
            self: Interaction,
            *,
            content: str = MISSING,
            tts: bool = MISSING,
            embeds: list[Embed] = MISSING,
            allowed_mentions: AllowedMentions = MISSING,
            components: list[ActionRow] = MISSING,
            message_reference: Message = MISSING,
            stickers: list[Sticker] = MISSING,
            files: list[File] = MISSING,
            flags: flags.MessageFlags = MISSING) -> None:
        """
        Send an update response.

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

        await self.state.interaction.create_interaction_response(
            self.id,
            self.token,
            InteractionResponseType.update_message,
            data,
        )
        self._responded = True

    async def send_autocomplete(
            self: Interaction,
            options: list[ApplicationCommandChoice]) -> None:
        """
        Send an autocomplete response.

        Parameters
        ----------
        options : list[novus.ApplicationCommandChoice]
            A list of choices to to populate the autocomplete with.
        """

        await self.state.interaction.create_interaction_response(
            self.id,
            self.token,
            InteractionResponseType.application_command_autocomplete_result,
            {"choices": options},
        )
        self._responded = True

    async def send_modal(
            self: Interaction,
            modal: Modal) -> None:
        """
        Send a modal response. Not valid on modal interactions.

        Parameters
        ----------
        modal : novus.Modal
            The modal that you want to send.
        """

        await self.state.interaction.create_interaction_response(
            self.id,
            self.token,
            InteractionResponseType.application_command_autocomplete_result,
            modal,
        )
        self._responded = True
