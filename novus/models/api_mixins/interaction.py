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
from typing import TYPE_CHECKING, Any

from ...enums import InteractionResponseType, InteractionType
from ...flags import MessageFlags
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
        Modal,
        Sticker,
        WebhookMessage,
        flags,
    )
    from ...utils import TranslatedString

__all__ = (
    'InteractionAPIMixin',
)


class InteractionAPIMixin:

    def _get_response_partial(self: Interaction):
        if self._stream is None:
            return functools.partial(
                self.state.interaction.create_interaction_response,
                self.id,
                self.token,
            )
        else:
            return functools.partial(
                self.state.interaction.create_interaction_response_for_writer,
                self._stream,
                self._stream_request,  # pyright: ignore
            )

    async def pong(self: Interaction) -> None:
        """
        Send a pong interaction response.
        """

        await self._get_response_partial()(InteractionResponseType.pong)

    async def send(
            self: Interaction,
            content: str | TranslatedString = MISSING,
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
        if flags is MISSING:
            data["flags"] = MessageFlags()
        else:
            data["flags"] = flags
        if ephemeral:
            data["flags"].ephemeral = True

        if self._responded is False:
            await self._get_response_partial()(
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

    async def defer(self: Interaction, *, ephemeral: bool = False) -> None:
        """
        Send a defer response.
        """

        data = None
        if ephemeral:
            data = {"flags": MessageFlags(ephemeral=True)}
        await self._get_response_partial()(
            InteractionResponseType.deferred_channel_message_with_source,
            data,
        )
        self._responded = True

    async def defer_update(self: Interaction) -> None:
        """
        Send a defer update response.
        """

        t = InteractionResponseType.deferred_channel_message_with_source
        if self.type == InteractionType.message_component:
            t = InteractionResponseType.deferred_update_message
        await self._get_response_partial()(t)
        self._responded = True

    async def update(
            self: Interaction,
            *,
            content: str | None = MISSING,
            tts: bool = MISSING,
            embeds: list[Embed] | None = MISSING,
            allowed_mentions: AllowedMentions | None = MISSING,
            components: list[ActionRow] | None = MISSING,
            message_reference: Message | None = MISSING,
            stickers: list[Sticker] | None = MISSING,
            files: list[File] | None = MISSING,
            flags: flags.MessageFlags | None = MISSING) -> None:
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

        await self._get_response_partial()(
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

        await self._get_response_partial()(
            InteractionResponseType.application_command_autocomplete_result,
            {"choices": options},
        )
        self._responded = True

    async def send_modal(
            self: Interaction,
            *,
            title: str,
            custom_id: str,
            components: list[ActionRow]) -> None:
        """
        Send a modal response. Not valid on modal interactions.

        Parameters
        ----------
        title : str
            The title to be shown in the modal.
        custom_id : str
            The custom ID of the modal.
        components : list[novus.ActionRow]
            The components shown in the modal.
        """

        await self._get_response_partial()(
            InteractionResponseType.modal,
            {
                "title": title,
                "custom_id": custom_id,
                "components": [i._to_data() for i in components],
            },
        )
        self._responded = True

    async def delete_original(self: Interaction) -> None:
        """
        Delete the original message that is associated with the interaction.
        """

        await self.state.interaction.delete_original_interaction_response(
            self.application_id,
            self.token,
        )

    async def fetch_original(self: Interaction) -> WebhookMessage:
        """
        Get the original message associated with the interaction.
        """

        return await self.state.interaction.get_original_interaction_response(
            self.application_id,
            self.token,
        )

    async def edit_original(self: Interaction, **kwargs: Any) -> WebhookMessage:
        """
        Edit the original message associated with the interaction.
        """

        return await self.state.interaction.edit_original_interaction_response(
            self.application_id,
            self.token,
            **kwargs,
        )
