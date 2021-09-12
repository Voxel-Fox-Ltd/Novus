# -*- coding: utf-8 -*-

"""
The MIT License (MIT)

Copyright (c) 2015-2021 Rapptz
Copyright (c) 2021-present Kae Bartlett

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, TYPE_CHECKING, Tuple, Union
import asyncio
import json

from aiohttp import web

from . import utils
from .enums import try_enum, InteractionType, InteractionResponseType
from .errors import InteractionResponded, HTTPException, ClientException, InvalidData
from .channel import PartialMessageable, ChannelType, _threaded_channel_factory

from .user import User
from .member import Member
from .role import Role
from .message import Message, Attachment
from .object import Object
from .permissions import Permissions
from .webhook.async_ import async_context, Webhook, handle_message_parameters

__all__ = (
    'Interaction',
    'InteractionMessage',
    'InteractionResponse',
    'InteractionResolved',
)

if TYPE_CHECKING:
    from .types.interactions import (
        Interaction as InteractionPayload,
        InteractionData,
    )
    from .guild import Guild
    from .state import ConnectionState
    from .file import File
    from .mentions import AllowedMentions
    from aiohttp import ClientSession
    from .embeds import Embed
    from .ui.action_row import MessageComponents
    from .channel import VoiceChannel, StageChannel, TextChannel, CategoryChannel, StoreChannel, PartialMessageable
    from .threads import Thread

    InteractionChannel = Union[
        VoiceChannel, StageChannel, TextChannel, CategoryChannel, StoreChannel, Thread, PartialMessageable
    ]

MISSING: Any = utils.MISSING


class InteractionResolved:
    """
    A set of resolved data from an interaction.

    .. versionadded:: 0.0.3

    Attributes
    ------------
    users: List[Union[:class:`User`, :class:`Member`]]
        The users who were mentioned in the interaction.
    members: List[:class:`Member`]
        The members who were mentioned in the interaction.
    roles: List[:class:`Role`]
        The roles that were mentioned in the interaction.
    channels: List[Union[:class:`VoiceChannel`, :class:`StageChannel`, :class:`TextChannel`, :class:`CategoryChannel`, :class:`StoreChannel`, :class:`Thread`]]
        The channels that were mentioned in the interaction.
    message: List[:class:`Message`]
        The messages that were mentioned in the interaction.
    """

    def __init__(self, *, interaction, data: dict, state: ConnectionState):
        self.users: List[Union[User, Member]] = []
        self.members: List[Member] = []
        self.roles: List[Role] = []
        self.channels: List[InteractionChannel] = []
        self.messages: List[Message] = []
        self._interaction: Interaction = interaction
        self._state = state
        self._from_data(data)

    def _from_data(self, data: dict):

        # Parse user data
        user_data = data.get("users", dict())
        member_data = data.get("members", dict())
        for uid, d in member_data.items():
            d.update({"user": user_data.pop(uid)})
        if self._interaction.guild:
            self.members.extend(Member(data=d, state=self._state, guild=self._interaction.guild) for _, d in member_data.items())
        self.users.extend(User(data=d, state=self._state) for _, d in user_data.items())
        self.users.extend(self.members)

        # Parse role data
        if self._interaction.guild:
            for rid, d in data.get("roles", dict()).items():
                self.roles.append(Role(guild=self._interaction.guild, state=self._state, data=d))

        # Parse channel data
        for cid, d in data.get("channels", dict()).items():
            factory, ch_type = _threaded_channel_factory(d['type'])
            if factory is None:
                raise InvalidData('Unknown channel type {type} for channel ID {id}.'.format_map(d))
            if ch_type in (ChannelType.group, ChannelType.private):
                channel = factory(me=self.user, data=data, state=self._connection) # type: ignore
            else:
                guild_id = int(data['guild_id']) # type: ignore
                guild = self._interaction.guild
                channel = factory(guild=guild, state=self._connection, data=data) # type: ignore
            self.channels.append(channel)

        # Parse messages
        for mid, d in data.get("messages", dict()).items():
            self.messages.append(Message(state=self._state, channel=self._interaction.channel, data=d))


class Interaction:
    """Represents a Discord interaction.

    An interaction happens when a user does an action that needs to
    be notified. Current examples are slash commands and components.

    Attributes
    -----------
    id: :class:`int`
        The interaction's ID.
    type: :class:`InteractionType`
        The interaction type.
    guild_id: Optional[:class:`int`]
        The guild ID the interaction was sent from.
    channel_id: Optional[:class:`int`]
        The channel ID the interaction was sent from.
    application_id: :class:`int`
        The application ID that the interaction was for.
    user: Optional[Union[:class:`User`, :class:`Member`]]
        The user or member that sent the interaction.
    message: Optional[:class:`Message`]
        The message that sent this interaction.
    component: Optional[:class:`BaseComponent`]
        The component that was interacted with to spawn this interaction.
        This may be `None` if the interaction was created from a slash
        command.
    values: Optional[List[:class:`str`]]
        The values that were passed back from the interaction. If this interaction
        did not give back any values then this will ne `None`. This is different from
        the values being an empty list - that would be the user did not
        provide any values for a valid component.
    token: :class:`str`
        The token to continue the interaction. These are valid
        for 15 minutes.
    data: :class:`dict`
        The raw interaction data.
    resolved: :class:`InteractionResolved`
        The resolved interaction data.
    """

    __slots__: Tuple[str, ...] = (
        'id',
        'type',
        'guild_id',
        'channel_id',
        'data',
        'component',
        'values',
        'application_id',
        'message',
        'user',
        'token',
        'version',
        'resolved',
        '_permissions',
        '_state',
        '_session',
        '_original_message',
        '_cs_response',
        '_cs_followup',
        '_cs_channel',
        '_cs_command_name',
    )

    def __init__(self, *, data: InteractionPayload, state: ConnectionState):
        self._state: ConnectionState = state
        self._session: ClientSession = state.http._HTTPClient__session
        self._original_message: Optional[InteractionMessage] = None
        self._from_data(data)

    def _from_data(self, data: InteractionPayload):
        self.id: int = int(data['id'])
        self.type: InteractionType = try_enum(InteractionType, data['type'])
        self.data: Optional[InteractionData] = data.get('data')
        self.token: str = data['token']
        self.version: int = data['version']
        self.channel_id: Optional[int] = utils._get_as_snowflake(data, 'channel_id')
        self.guild_id: Optional[int] = utils._get_as_snowflake(data, 'guild_id')
        self.application_id: int = int(data['application_id'])

        self.message: Optional[Message]
        try:
            self.message = Message(state=self._state, channel=self.channel, data=data['message'])  # type: ignore
        except KeyError:
            self.message = None

        try:
            if self.message:
                self.component = self.message.components.get_component(data['data']['custom_id'])
            else:
                self.component = None
        except KeyError:
            self.component = None

        try:
            self.values = data['data']['values']
        except KeyError:
            self.values = None

        self.user: Optional[Union[User, Member]] = None
        self._permissions: int = 0

        # TODO: there's a potential data loss here
        if self.guild_id:
            guild = self.guild or Object(id=self.guild_id)
            try:
                member = data['member']  # type: ignore
            except KeyError:
                pass
            else:
                self.user = Member(state=self._state, guild=guild, data=member)  # type: ignore
                self._permissions = int(member.get('permissions', 0))
        else:
            try:
                self.user = User(state=self._state, data=data['user'])
            except KeyError:
                pass

        # Parse the resolved data
        self.resolved = InteractionResolved(interaction=self, data=(self.data or {}).copy().get("resolved", dict()), state=self._state)

    @utils.cached_slot_property('_cs_command_name')
    def command_name(self) -> Optional[str]:
        """Optional[:class:`str`]: The name of the invoked command. Only valid for slash command interactions."""

        if self.data is None:
            return
        if self.type != InteractionType.application_command:
            return
        data = self.data.copy()
        command_name = data.get('name')
        while command_name:
            if "options" not in data:
                break
            if data['options'][0]['type'] in [1, 2]:
                data = data['options'][0]
                command_name += f" {data['name']}"
            else:
                break
        return command_name

    @property
    def guild(self) -> Optional[Guild]:
        """Optional[:class:`Guild`]: The guild the interaction was sent from."""
        return self._state and self._state._get_guild(self.guild_id)

    @utils.cached_slot_property('_cs_channel')
    def channel(self) -> Optional[InteractionChannel]:
        """Optional[Union[:class:`abc.GuildChannel`, :class:`PartialMessageable`, :class:`Thread`]]: The channel the interaction was sent from.

        Note that due to a Discord limitation, DM channels are not resolved since there is
        no data to complete them. These are :class:`PartialMessageable` instead.
        """
        guild = self.guild
        channel = guild and guild._resolve_channel(self.channel_id)
        if channel is None:
            if self.channel_id is not None:
                type = ChannelType.text if self.guild_id is not None else ChannelType.private
                return PartialMessageable(state=self._state, id=self.channel_id, type=type)
            return None
        return channel

    @property
    def permissions(self) -> Permissions:
        """:class:`Permissions`: The resolved permissions of the member in the channel, including overwrites.

        In a non-guild context where this doesn't apply, an empty permissions object is returned.
        """
        return Permissions(self._permissions)

    @utils.cached_slot_property('_cs_response')
    def response(self) -> Union[InteractionResponse, HTTPInteractionResponse]:
        """:class:`InteractionResponse`: Returns an object responsible for handling responding to the interaction.

        A response can only be done once. If secondary messages need to be sent, consider using :attr:`followup`
        instead.
        """
        return InteractionResponse(self)

    @utils.cached_slot_property('_cs_followup')
    def followup(self) -> Webhook:
        """:class:`Webhook`: Returns the follow up webhook for follow up interactions."""
        payload = {
            'id': self.application_id,
            'type': 3,
            'token': self.token,
        }
        v = Webhook.from_state(data=payload, state=self._state)
        v.supports_ephemeral = True
        return v

    async def original_message(self) -> InteractionMessage:
        """|coro|

        Fetches the original interaction response message associated with the interaction.

        If the interaction response was :meth:`InteractionResponse.send_message` then this would
        return the message that was sent using that response. Otherwise, this would return
        the message that triggered the interaction.

        Repeated calls to this will return a cached value.

        Raises
        -------
        HTTPException
            Fetching the original response message failed.
        ClientException
            The channel for the message could not be resolved.

        Returns
        --------
        InteractionMessage
            The original interaction response message.
        """

        if self._original_message is not None:
            return self._original_message

        # TODO: fix later to not raise?
        channel = self.channel
        if channel is None:
            raise ClientException('Channel for message could not be resolved')

        adapter = async_context.get()
        data = await adapter.get_original_interaction_response(
            application_id=self.application_id,
            token=self.token,
            session=self._session,
        )
        state = _InteractionMessageState(self, self._state)
        message = InteractionMessage(state=state, channel=channel, data=data)  # type: ignore
        self._original_message = message
        return message

    async def edit_original_message(
        self,
        *,
        content: Optional[str] = MISSING,
        embeds: List[Embed] = MISSING,
        embed: Optional[Embed] = MISSING,
        file: File = MISSING,
        files: List[File] = MISSING,
        components: Optional[MessageComponents] = MISSING,
        allowed_mentions: Optional[AllowedMentions] = None,
    ) -> InteractionMessage:
        """|coro|

        Edits the original interaction response message.

        This is a lower level interface to :meth:`InteractionMessage.edit` in case
        you do not want to fetch the message and save an HTTP request.

        This method is also the only way to edit the original message if
        the message sent was ephemeral.

        Parameters
        ------------
        content: Optional[:class:`str`]
            The content to edit the message with or ``None`` to clear it.
        embeds: List[:class:`Embed`]
            A list of embeds to edit the message with.
        embed: Optional[:class:`Embed`]
            The embed to edit the message with. ``None`` suppresses the embeds.
            This should not be mixed with the ``embeds`` parameter.
        file: :class:`File`
            The file to upload. This cannot be mixed with ``files`` parameter.
        files: List[:class:`File`]
            A list of files to send with the content. This cannot be mixed with the
            ``file`` parameter.
        allowed_mentions: :class:`AllowedMentions`
            Controls the mentions being processed in this message.
            See :meth:`.abc.Messageable.send` for more information.
        components: Optional[:class:`~discord.ui.MessageComponents`]
            The set of message components to update the message with. If ``None`` is passed then
            the components are removed.

        Raises
        -------
        HTTPException
            Editing the message failed.
        Forbidden
            Edited a message that is not yours.
        TypeError
            You specified both ``embed`` and ``embeds`` or ``file`` and ``files``
        ValueError
            The length of ``embeds`` was invalid.

        Returns
        --------
        :class:`InteractionMessage`
            The newly edited message.
        """

        previous_mentions: Optional[AllowedMentions] = self._state.allowed_mentions
        params = handle_message_parameters(
            content=content,
            file=file,
            files=files,
            embed=embed,
            embeds=embeds,
            components=components,
            allowed_mentions=allowed_mentions,
            previous_allowed_mentions=previous_mentions,
        )
        adapter = async_context.get()
        data = await adapter.edit_original_interaction_response(
            self.application_id,
            self.token,
            session=self._session,
            payload=params.payload,
            multipart=params.multipart,
            files=params.files,
        )

        # The message channel types should always match
        message = InteractionMessage(state=self._state, channel=self.channel, data=data)  # type: ignore
        return message

    async def delete_original_message(self) -> None:
        """|coro|

        Deletes the original interaction response message.

        This is a lower level interface to :meth:`InteractionMessage.delete` in case
        you do not want to fetch the message and save an HTTP request.

        Raises
        -------
        HTTPException
            Deleting the message failed.
        Forbidden
            Deleted a message that is not yours.
        """
        adapter = async_context.get()
        await adapter.delete_original_interaction_response(
            self.application_id,
            self.token,
            session=self._session,
        )


class InteractionResponse:
    """Represents a Discord interaction response.

    This type can be accessed through :attr:`Interaction.response`.
    """

    __slots__: Tuple[str, ...] = (
        '_responded',
        '_parent',
    )

    def __init__(self, parent: Interaction):
        self._parent: Interaction = parent
        self._responded: bool = False

    def is_done(self) -> bool:
        """:class:`bool`: Indicates whether an interaction response has been done before.

        An interaction can only be responded to once.
        """
        return self._responded

    async def defer(self, *, ephemeral: bool = False) -> None:
        """|coro|

        Defers the interaction response.

        This is typically used when the interaction is acknowledged
        and a secondary action will be done later.

        Parameters
        -----------
        ephemeral: :class:`bool`
            Indicates whether the deferred message will eventually be ephemeral.
            This only applies for interactions of type :attr:`InteractionType.application_command`.

        Raises
        -------
        HTTPException
            Deferring the interaction failed.
        InteractionResponded
            This interaction has already been responded to before.
        """
        if self._responded:
            raise InteractionResponded(self._parent)

        defer_type: int = 0
        data: Optional[Dict[str, Any]] = None
        parent = self._parent
        defer_type = InteractionResponseType.deferred_channel_message.value
        if ephemeral:
            data = {'flags': 64}

        if defer_type:
            adapter = async_context.get()
            await adapter.create_interaction_response(
                parent.id, parent.token, session=parent._session, type=defer_type, data=data
            )
            self._responded = True

    async def defer_update(self) -> None:
        """|coro|

        Defers the interaction response.

        This is typically used when the interaction is acknowledged
        and a secondary action will be done later.

        This is only usable if the interaction spawned from a component interaction.

        Raises
        -------
        HTTPException
            Deferring the interaction failed.
        InteractionResponded
            This interaction has already been responded to before.
        """
        if self._responded:
            raise InteractionResponded(self._parent)

        defer_type: int = 0
        data: Optional[Dict[str, Any]] = None
        parent = self._parent
        defer_type = InteractionResponseType.deferred_message_update.value

        if defer_type:
            adapter = async_context.get()
            await adapter.create_interaction_response(
                parent.id, parent.token, session=parent._session, type=defer_type, data=data
            )
            self._responded = True

    async def pong(self) -> None:
        """|coro|

        Pongs the ping interaction.

        This should rarely be used.

        Raises
        -------
        HTTPException
            Ponging the interaction failed.
        InteractionResponded
            This interaction has already been responded to before.
        """
        if self._responded:
            raise InteractionResponded(self._parent)

        parent = self._parent
        if parent.type is InteractionType.ping:
            adapter = async_context.get()
            await adapter.create_interaction_response(
                parent.id, parent.token, session=parent._session, type=InteractionResponseType.pong.value
            )
            self._responded = True

    async def send_message(
        self,
        content: Optional[Any] = None,
        *,
        embed: Embed = MISSING,
        embeds: List[Embed] = MISSING,
        components: MessageComponents = MISSING,
        tts: bool = False,
        ephemeral: bool = False,
        allowed_mentions: AllowedMentions = None,
    ) -> None:
        """|coro|

        Responds to this interaction by sending a message.

        Parameters
        -----------
        content: Optional[:class:`str`]
            The content of the message to send.
        embeds: List[:class:`Embed`]
            A list of embeds to send with the content. Maximum of 10. This cannot
            be mixed with the ``embed`` parameter.
        embed: :class:`Embed`
            The rich embed for the content to send. This cannot be mixed with
            ``embeds`` parameter.
        tts: :class:`bool`
            Indicates if the message should be sent using text-to-speech.
        components: :class:`discord.ui.MessageComponents`
            The components to send with the messasge.
        ephemeral: :class:`bool`
            Indicates if the message should only be visible to the user who started the interaction.
        allowed_mentions: :class:`AllowedMentions`
            The allowed mentions that should be sent with the message.

        Raises
        -------
        HTTPException
            Sending the message failed.
        TypeError
            You specified both ``embed`` and ``embeds``.
        ValueError
            The length of ``embeds`` was invalid.
        InteractionResponded
            This interaction has already been responded to before.
        """
        if self._responded:
            raise InteractionResponded(self._parent)

        payload: Dict[str, Any] = {
            'tts': tts,
        }

        if embed is not MISSING and embeds is not MISSING:
            raise TypeError('cannot mix embed and embeds keyword arguments')

        if embed is not MISSING:
            embeds = [embed]

        if embeds:
            if len(embeds) > 10:
                raise ValueError('embeds cannot exceed maximum of 10 elements')
            payload['embeds'] = [e.to_dict() for e in embeds]

        if content is not None:
            payload['content'] = str(content)

        if ephemeral:
            payload['flags'] = 64

        if components is not MISSING:
            payload['components'] = components.to_dict()

        parent = self._parent
        parent_state = parent._state

        if allowed_mentions is not None:
            if parent_state.allowed_mentions is not None:
                allowed_mentions = parent_state.allowed_mentions.merge(allowed_mentions).to_dict()
            else:
                allowed_mentions = allowed_mentions.to_dict()
        else:
            allowed_mentions = parent_state.allowed_mentions and parent_state.allowed_mentions.to_dict()

        adapter = async_context.get()
        await adapter.create_interaction_response(
            parent.id,
            parent.token,
            session=parent._session,
            type=InteractionResponseType.channel_message.value,
            data=payload,
        )

        self._responded = True

    async def edit_message(
        self,
        *,
        content: Optional[Any] = MISSING,
        embed: Optional[Embed] = MISSING,
        embeds: List[Embed] = MISSING,
        attachments: List[Attachment] = MISSING,
        components: Optional[MessageComponents] = MISSING,
        allowed_mentions: Optional[AllowedMentions] = MISSING,
    ) -> None:
        """|coro|

        Responds to this interaction by editing the original message of
        a component interaction.

        Parameters
        -----------
        content: Optional[:class:`str`]
            The new content to replace the message with. ``None`` removes the content.
        embeds: List[:class:`Embed`]
            A list of embeds to edit the message with.
        embed: Optional[:class:`Embed`]
            The embed to edit the message with. ``None`` suppresses the embeds.
            This should not be mixed with the ``embeds`` parameter.
        attachments: List[:class:`Attachment`]
            A list of attachments to keep in the message. If ``[]`` is passed
            then all attachments are removed.
        components: Optional[:class:`~discord.ui.MessageComponents`]
            The updated components to update this message with. If ``None`` is passed then
            the components are removed.

        Raises
        -------
        HTTPException
            Editing the message failed.
        TypeError
            You specified both ``embed`` and ``embeds``.
        InteractionResponded
            This interaction has already been responded to before.
        """
        if self._responded:
            raise InteractionResponded(self._parent)

        parent = self._parent
        msg = parent.message
        state = parent._state
        message_id = msg.id if msg else None
        if parent.type is not InteractionType.component:
            return

        payload = {}
        if content is not MISSING:
            if content is None:
                payload['content'] = None
            else:
                payload['content'] = str(content)

        if embed is not MISSING and embeds is not MISSING:
            raise TypeError('cannot mix both embed and embeds keyword arguments')

        if embed is not MISSING:
            if embed is None:
                embeds = []
            else:
                embeds = [embed]

        if embeds is not MISSING:
            payload['embeds'] = [e.to_dict() for e in embeds]

        if attachments is not MISSING:
            payload['attachments'] = [a.to_dict() for a in attachments]

        if components is not MISSING:
            if components is None:
                payload['components'] = []
            else:
                payload['components'] = components.to_dict()

        if allowed_mentions is not MISSING:
            parent_state = self._parent._state
            if allowed_mentions:
                if parent_state.allowed_mentions is not None:
                    payload['allowed_mentions'] = parent_state.allowed_mentions.merge(allowed_mentions).to_dict()
                else:
                    payload['allowed_mentions'] = allowed_mentions.to_dict()
            elif parent_state.allowed_mentions is not None:
                payload['allowed_mentions'] = parent_state.allowed_mentions.to_dict()

        adapter = async_context.get()
        await adapter.create_interaction_response(
            parent.id,
            parent.token,
            session=parent._session,
            type=InteractionResponseType.message_update.value,
            data=payload,
        )

        self._responded = True


class HTTPInteractionResponse(InteractionResponse):
    """Represents a Discord interaction response.

    This type can be accessed through :attr:`Interaction.response`.
    """

    __slots__: Tuple[str, ...] = (
        '_responded',
        '_parent',
        '_aiohttp_request',
        '_aiohttp_response',
    )

    def __init__(self, aiohttp_response: web.Request, parent: Interaction):
        super().__init__(parent)
        self._aiohttp_request: web.Request = aiohttp_response
        self._aiohttp_response: web.StreamResponse = web.StreamResponse()

    async def defer(self, *, ephemeral: bool = False) -> None:
        """|coro|

        Defers the interaction response.

        This is typically used when the interaction is acknowledged
        and a secondary action will be done later.

        Parameters
        -----------
        ephemeral: :class:`bool`
            Indicates whether the deferred message will eventually be ephemeral.
            This only applies for interactions of type :attr:`InteractionType.application_command`.

        Raises
        -------
        HTTPException
            Deferring the interaction failed.
        InteractionResponded
            This interaction has already been responded to before.
        """
        if self._responded:
            raise InteractionResponded(self._parent)

        defer_type: int = 0
        data: Optional[Dict[str, Any]] = None
        defer_type = InteractionResponseType.deferred_channel_message.value
        if ephemeral:
            data = {'flags': 64}

        if defer_type:
            payload = {"type": defer_type}
            if data:
                payload["data"] = data
            self._aiohttp_response.headers["Content-Type"] = "application/json"
            await self._aiohttp_response.prepare(self._aiohttp_request)
            await self._aiohttp_response.write(json.dumps(payload).encode())
            await self._aiohttp_response.write_eof()
            self._responded = True

    async def defer_update(self) -> None:
        """|coro|

        Defers the interaction response.

        This is typically used when the interaction is acknowledged
        and a secondary action will be done later.

        This is only usable if the interaction spawned from a component interaction.

        Raises
        -------
        HTTPException
            Deferring the interaction failed.
        InteractionResponded
            This interaction has already been responded to before.
        """
        if self._responded:
            raise InteractionResponded(self._parent)

        defer_type: int = 0
        defer_type = InteractionResponseType.deferred_message_update.value

        if defer_type:
            payload = {"type": defer_type}
            self._aiohttp_response.headers["Content-Type"] = "application/json"
            await self._aiohttp_response.prepare(self._aiohttp_request)
            await self._aiohttp_response.write(json.dumps(payload).encode())
            await self._aiohttp_response.write_eof()
            self._responded = True

    async def pong(self) -> None:
        """|coro|

        Pongs the ping interaction.

        This should rarely be used.

        Raises
        -------
        HTTPException
            Ponging the interaction failed.
        InteractionResponded
            This interaction has already been responded to before.
        """
        if self._responded:
            raise InteractionResponded(self._parent)

        parent = self._parent
        if parent.type is InteractionType.ping:
            payload = {"type": InteractionResponseType.pong.value}
            self._aiohttp_response.headers["Content-Type"] = "application/json"
            await self._aiohttp_response.prepare(self._aiohttp_request)
            await self._aiohttp_response.write(json.dumps(payload).encode())
            await self._aiohttp_response.write_eof()
            self._responded = True

    async def send_message(
        self,
        content: Optional[Any] = None,
        *,
        embed: Embed = MISSING,
        embeds: List[Embed] = MISSING,
        components: MessageComponents = MISSING,
        tts: bool = False,
        ephemeral: bool = False,
        allowed_mentions: AllowedMentions = None,
    ) -> None:
        """|coro|

        Responds to this interaction by sending a message.

        Parameters
        -----------
        content: Optional[:class:`str`]
            The content of the message to send.
        embeds: List[:class:`Embed`]
            A list of embeds to send with the content. Maximum of 10. This cannot
            be mixed with the ``embed`` parameter.
        embed: :class:`Embed`
            The rich embed for the content to send. This cannot be mixed with
            ``embeds`` parameter.
        tts: :class:`bool`
            Indicates if the message should be sent using text-to-speech.
        components: :class:`discord.ui.MessageComponents`
            The components to send with the messasge.
        ephemeral: :class:`bool`
            Indicates if the message should only be visible to the user who started the interaction.
        allowed_mentions: :class:`AllowedMentions`
            The allowed mentions that should be sent with the message.

        Raises
        -------
        HTTPException
            Sending the message failed.
        TypeError
            You specified both ``embed`` and ``embeds``.
        ValueError
            The length of ``embeds`` was invalid.
        InteractionResponded
            This interaction has already been responded to before.
        """
        if self._responded:
            raise InteractionResponded(self._parent)

        payload: Dict[str, Any] = {
            'tts': tts,
        }

        if embed is not MISSING and embeds is not MISSING:
            raise TypeError('cannot mix embed and embeds keyword arguments')

        if embed is not MISSING:
            embeds = [embed]

        if embeds:
            if len(embeds) > 10:
                raise ValueError('embeds cannot exceed maximum of 10 elements')
            payload['embeds'] = [e.to_dict() for e in embeds]

        if content is not None:
            payload['content'] = str(content)

        if ephemeral:
            payload['flags'] = 64

        if components is not MISSING:
            payload['components'] = components.to_dict()

        parent = self._parent
        parent_state = parent._state

        if allowed_mentions is not None:
            if parent_state.allowed_mentions is not None:
                allowed_mentions = parent_state.allowed_mentions.merge(allowed_mentions).to_dict()
            else:
                allowed_mentions = allowed_mentions.to_dict()
        else:
            allowed_mentions = parent_state.allowed_mentions and parent_state.allowed_mentions.to_dict()

        data = {
            "type": InteractionResponseType.channel_message.value,
            "data": payload,
        }
        self._aiohttp_response.headers["Content-Type"] = "application/json"
        await self._aiohttp_response.prepare(self._aiohttp_request)
        await self._aiohttp_response.write(json.dumps(data).encode())
        await self._aiohttp_response.write_eof()

        self._responded = True

    async def edit_message(
        self,
        *,
        content: Optional[Any] = MISSING,
        embed: Optional[Embed] = MISSING,
        embeds: List[Embed] = MISSING,
        attachments: List[Attachment] = MISSING,
        components: Optional[MessageComponents] = MISSING,
        allowed_mentions: Optional[AllowedMentions] = MISSING,
    ) -> None:
        """|coro|

        Responds to this interaction by editing the original message of
        a component interaction.

        Parameters
        -----------
        content: Optional[:class:`str`]
            The new content to replace the message with. ``None`` removes the content.
        embeds: List[:class:`Embed`]
            A list of embeds to edit the message with.
        embed: Optional[:class:`Embed`]
            The embed to edit the message with. ``None`` suppresses the embeds.
            This should not be mixed with the ``embeds`` parameter.
        attachments: List[:class:`Attachment`]
            A list of attachments to keep in the message. If ``[]`` is passed
            then all attachments are removed.
        components: Optional[:class:`~discord.ui.MessageComponents`]
            The updated components to update this message with. If ``None`` is passed then
            the components are removed.

        Raises
        -------
        HTTPException
            Editing the message failed.
        TypeError
            You specified both ``embed`` and ``embeds``.
        InteractionResponded
            This interaction has already been responded to before.
        """
        if self._responded:
            raise InteractionResponded(self._parent)

        parent = self._parent
        msg = parent.message
        state = parent._state
        message_id = msg.id if msg else None
        if parent.type is not InteractionType.component:
            return

        payload = {}
        if content is not MISSING:
            if content is None:
                payload['content'] = None
            else:
                payload['content'] = str(content)

        if embed is not MISSING and embeds is not MISSING:
            raise TypeError('cannot mix both embed and embeds keyword arguments')

        if embed is not MISSING:
            if embed is None:
                embeds = []
            else:
                embeds = [embed]

        if embeds is not MISSING:
            payload['embeds'] = [e.to_dict() for e in embeds]

        if attachments is not MISSING:
            payload['attachments'] = [a.to_dict() for a in attachments]

        if components is not MISSING:
            if components is None:
                payload['components'] = []
            else:
                payload['components'] = components.to_dict()

        if allowed_mentions is not MISSING:
            parent_state = self._parent._state
            if allowed_mentions:
                if parent_state.allowed_mentions is not None:
                    payload['allowed_mentions'] = parent_state.allowed_mentions.merge(allowed_mentions).to_dict()
                else:
                    payload['allowed_mentions'] = allowed_mentions.to_dict()
            elif parent_state.allowed_mentions is not None:
                payload['allowed_mentions'] = parent_state.allowed_mentions.to_dict()

        data = {
            "type": InteractionResponseType.message_update.value,
            "data": payload,
        }
        self._aiohttp_response.headers["Content-Type"] = "application/json"
        await self._aiohttp_response.prepare(self._aiohttp_request)
        await self._aiohttp_response.write(json.dumps(data).encode())
        await self._aiohttp_response.write_eof()

        self._responded = True


class _InteractionMessageState:
    __slots__ = ('_parent', '_interaction')

    def __init__(self, interaction: Interaction, parent: ConnectionState):
        self._interaction: Interaction = interaction
        self._parent: ConnectionState = parent

    def _get_guild(self, guild_id):
        return self._parent._get_guild(guild_id)

    def store_user(self, data):
        return self._parent.store_user(data)

    def create_user(self, data):
        return self._parent.create_user(data)

    @property
    def http(self):
        return self._parent.http

    def __getattr__(self, attr):
        return getattr(self._parent, attr)


class InteractionMessage(Message):
    """Represents the original interaction response message.

    This allows you to edit or delete the message associated with
    the interaction response. To retrieve this object see :meth:`Interaction.original_message`.

    This inherits from :class:`discord.Message` with changes to
    :meth:`edit` and :meth:`delete` to work.
    """

    __slots__ = ()
    _state: _InteractionMessageState

    async def edit(
        self,
        content: Optional[str] = MISSING,
        embeds: List[Embed] = MISSING,
        embed: Optional[Embed] = MISSING,
        file: File = MISSING,
        files: List[File] = MISSING,
        components: Optional[MessageComponents] = MISSING,
        allowed_mentions: Optional[AllowedMentions] = None,
    ) -> InteractionMessage:
        """|coro|

        Edits the message.

        Parameters
        ------------
        content: Optional[:class:`str`]
            The content to edit the message with or ``None`` to clear it.
        embeds: List[:class:`Embed`]
            A list of embeds to edit the message with.
        embed: Optional[:class:`Embed`]
            The embed to edit the message with. ``None`` suppresses the embeds.
            This should not be mixed with the ``embeds`` parameter.
        file: :class:`File`
            The file to upload. This cannot be mixed with ``files`` parameter.
        files: List[:class:`File`]
            A list of files to send with the content. This cannot be mixed with the
            ``file`` parameter.
        allowed_mentions: :class:`AllowedMentions`
            Controls the mentions being processed in this message.
            See :meth:`.abc.Messageable.send` for more information.
        components: Optional[:class:`~discord.ui.MessageComponents`]
            The updated components to update this message with. If ``None`` is passed then
            the components are removed.

        Raises
        -------
        HTTPException
            Editing the message failed.
        Forbidden
            Edited a message that is not yours.
        TypeError
            You specified both ``embed`` and ``embeds`` or ``file`` and ``files``
        ValueError
            The length of ``embeds`` was invalid.

        Returns
        ---------
        :class:`InteractionMessage`
            The newly edited message.
        """
        return await self._state._interaction.edit_original_message(
            content=content,
            embeds=embeds,
            embed=embed,
            file=file,
            files=files,
            components=components,
            allowed_mentions=allowed_mentions,
        )

    async def delete(self, *, delay: Optional[float] = None) -> None:
        """|coro|

        Deletes the message.

        Parameters
        -----------
        delay: Optional[:class:`float`]
            If provided, the number of seconds to wait before deleting the message.
            The waiting is done in the background and deletion failures are ignored.

        Raises
        ------
        Forbidden
            You do not have proper permissions to delete the message.
        NotFound
            The message was deleted already.
        HTTPException
            Deleting the message failed.
        """

        if delay is not None:

            async def inner_call(delay: float = delay):
                await asyncio.sleep(delay)
                try:
                    await self._state._interaction.delete_original_message()
                except HTTPException:
                    pass

            asyncio.create_task(inner_call())
        else:
            await self._state._interaction.delete_original_message()
