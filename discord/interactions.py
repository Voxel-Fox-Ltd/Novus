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

from typing import (
    Any,
    Dict,
    List,
    Optional,
    TYPE_CHECKING,
    Tuple,
    Union,
    TypeVar,
)
import asyncio
import json

import aiohttp
from aiohttp import web

from . import utils
from .application_commands import ApplicationCommandInteractionDataOption
from .enums import try_enum, InteractionType, InteractionResponseType
from .errors import (
    InteractionResponded,
    HTTPException,
    ClientException,
    InvalidData,
)
from .channel import PartialMessageable, ChannelType, _threaded_channel_factory
from .guild import Guild
from .user import User
from .member import Member
from .role import Role
from .message import Message, Attachment
from .object import Object
from .permissions import Permissions
from .webhook.async_ import async_context, Webhook, handle_message_parameters
from .ui.models import InteractedComponent


__all__ = (
    'Interaction',
    'InteractionMessage',
    'InteractionResponse',
    'InteractionResolved',

    'CommandInteraction',
    'AutocompleteInteraction',
    'ComponentInteraction',
    'ModalInteraction',
)


if TYPE_CHECKING:
    from aiohttp import ClientSession

    from .types.interactions import (
        Interaction as InteractionPayload,
        InteractionData,
    )
    from .types.snowflake import Snowflake
    from .application_commands import ApplicationCommandOptionChoice
    from .guild import Guild
    from .state import ConnectionState
    from .file import File
    from .mentions import AllowedMentions
    from .embeds import Embed
    from .channel import (
        VoiceChannel,
        StageChannel,
        TextChannel,
        CategoryChannel,
        StoreChannel,
        PartialMessageable,
        ForumChannel,
    )
    from .threads import Thread
    from .ui.action_row import MessageComponents
    from .ui.modal import Modal

    InteractionChannel = Union[
        VoiceChannel,
        StageChannel,
        TextChannel,
        CategoryChannel,
        StoreChannel,
        Thread,
        PartialMessageable,
        ForumChannel
    ]


MISSING: Any = utils.MISSING


T = TypeVar("T", None, str)


class InteractionResolved:
    """
    A set of resolved data from an interaction.

    .. versionadded:: 0.0.3

    .. versionchanged:: 0.0.7

        Changed all list attributes to dicts.

    Attributes
    ------------
    users: Dict[:class:`int`, Union[:class:`User`, :class:`Member`]]
        The users who were mentioned in the interaction.
    members: Dict[:class:`int`, :class:`Member`]
        The members who were mentioned in the interaction.
    roles: Dict[:class:`int`, :class:`Role`]
        The roles that were mentioned in the interaction.
    channels: Dict[:class:`int`, Union[:class:`VoiceChannel`, :class:`StageChannel`, :class:`TextChannel`, :class:`CategoryChannel`, :class:`StoreChannel`, :class:`Thread`]]
        The channels that were mentioned in the interaction.
    messages: Dict[:class:`int`, :class:`Message`]
        The messages that were mentioned in the interaction.
    attachments: Dict[:class:`int`, :class:`Attachment`]
        The attachments that were sent with the payload.

        .. versionadded:: 0.0.7
    """

    __slots__ = (
        "_interaction",
        "_state",
        "_cs_users",
        "_cs_members",
        "_cs_roles",
        "_cs_channels",
        "_cs_messages",
        "_cs_attachments",
        "_data",
    )

    def __init__(
            self,
            *,
            interaction: Interaction,
            data: dict,
            state: ConnectionState):
        self._interaction = interaction
        self._state = state
        self._data = data

    @utils.cached_slot_property("_cs_users")
    def users(self) -> Dict[int, Union[User, Member]]:
        """
        Parse the user/member objects from the data.
        """

        users: Dict[int, Union[User, Member]]
        users = self.members.copy()  # type: ignore - dict update type reassign
        user_data = self._data.get("users", dict())
        member_data = self._data.get("members", dict())
        for uid, d in member_data.items():
            if int(uid) not in users:
                d.update({"user": user_data.pop(uid)})
        users.update({
            int(i): User(data=d, state=self._state)
            for i, d in user_data.items()
        })
        return users

    @utils.cached_slot_property("_cs_members")
    def members(self) -> Dict[int, Member]:
        """
        Get the member objects from an interaction resolved.
        """

        # Make an initial dict to write to
        members = {}

        # Get the raw data for the user
        user_data = self._data.get("users", dict())
        member_data = self._data.get("members", dict())

        # Put the user data inside the member data
        for uid, d in member_data.items():
            d.update({"user": user_data.pop(uid)})

        # Create the member objects
        for i, d in member_data.items():
            members[int(i)] = Member(
                data=d,
                state=self._state,
                guild=self._interaction.guild,  # type: ignore - guild might not exist
            )

        # And done
        return members

    @utils.cached_slot_property("_cs_roles")
    def roles(self) -> Dict[int, Role]:
        """
        Parse up and cache the roles.
        """

        roles = {}
        if self._interaction.guild:
            for i, d in self._data.get("roles", dict()).items():
                roles[int(i)] = Role(
                    guild=self._interaction.guild,  # type: ignore - guild might not exist
                    state=self._state,
                    data=d,
                )
        return roles

    @utils.cached_slot_property("_cs_channels")
    def channels(self) -> Dict[int, InteractionChannel]:
        channels = {}
        for _, d in self._data.get("channels", dict()).items():
            factory, ch_type = _threaded_channel_factory(d['type'])
            if factory is None:
                raise InvalidData('Unknown channel type {type} for channel ID {id}.'.format_map(d))
            if ch_type in (ChannelType.group, ChannelType.private,):
                channel = factory(
                    me=self.user,
                    data=d,
                    state=self._state,
                )
            else:
                guild = self._interaction.guild
                channel = factory(
                    guild=guild,
                    state=self._state,
                    data=d,
                )
            channels[channel.id] = channel
        return channels

    @utils.cached_slot_property("_cs_messages")
    def messages(self) -> Dict[int, Message]:
        messages = {}
        for i, d in self._data.get("messages", dict()).items():
            messages[int(i)] = Message(
                state=self._state,
                channel=self._interaction.channel,
                data=d,
            )
        return messages

    @utils.cached_slot_property("_cs_attachments")
    def attachments(self) -> Dict[int, Attachment]:
        attachments = {}
        for i, d in self._data.get("attachments", dict()).items():
            attachments[int(i)] = Attachment(
                state=self._state,
                data=d,
            )
        return attachments


class Interaction:
    """
    Represents a Discord interaction.

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
        The application ID that the interaction was for. Unless you're running multiple
        bots in one script, this will be generally useless for most people.
    user: Optional[Union[:class:`User`, :class:`Member`]]
        The user or member that sent the interaction.
    message: Optional[:class:`Message`]
        The message that this interaction was spawned from. Only present for component
        interactions.
    component: Optional[:class:`ui.InteractableComponent`]
        The component that was interacted with to spawn this interaction.
        This will be ``None`` if the interaction was created from an application command.
    values: Optional[List[:class:`str`]]
        The values that were passed back from the interaction. If this interaction
        did not give back any values then this will be ``None``. This is different from
        the values being an empty list - that would be the user did not
        provide any values for a valid component.

        .. versionchanged:: 0.0.5
            This is now a list of :class:`str` objecs instead of ``dict``.
    token: :class:`str`
        The token to continue the interaction. These are valid
        for 15 minutes.
    data: :class:`dict`
        The data from the interaction. You don't need to use this unless
        you're building your own interaction handler, or dealing with an
        interaction that isn't yet added to the library.
    resolved: :class:`InteractionResolved`
        The resolved interaction data.
    options: Optional[List[:class:`ApplicationCommandInteractionDataOption`]]
        A list of options passed in from the interaction. For commands, this
        will be the options of the command; for autocompletes this will be a
        list of the options (as filled by the user) for the command.

        .. versionadded:: 0.0.4

        .. versionchanged:: 0.0.5
            Now is a list of :class:`ApplicationCommandInteractionDataOption`
            objects instead of a raw dictionary.
    components: Optional[List[:class:`ui.InteractionComponent`]]
        The components that are returned with the interaction. This is only
        used with modals so far. This skips the base level component
        (ie the modal object) and only gives its components.

        .. versionadded:: 0.0.5
    custom_id: Optional[:class:`str`]
        The custom ID associated with the main component of this interaction.

        .. versionadded:: 0.0.5
    user_locale: :class:`str`
        The locale of the user's client.

        .. versionadded:: 0.0.6
    guild_locale: Optional[:class:`str`]
        The locale of the guild where the interaction was invoked. Will be
        ``None`` if the interaction was invoked from a DM.

        .. versionadded:: 0.0.6
    locale: :class:`str`
        Returns the user locale or the guild locale

        .. versionadded:: 0.0.6
    app_permissions: :class:`Interaction`
        The permissions for the app in the given guild.

        .. versionadded:: 0.1.5
    """

    __slots__: Tuple[str, ...] = (
        'id',
        'type',
        'guild_id',
        'channel_id',
        'data',
        'component',
        'components',
        'values',
        'application_id',
        'target_id',
        'message',
        'user',
        'token',
        'version',
        'custom_id',
        '_cs_resolved',
        '_permissions',
        '_app_permissions',
        '_state',
        '_session',
        '_original_message',
        '_cs_response',
        '_cs_followup',
        '_cs_channel',
        '_cs_command_name',
        'options',
        'user_locale',
        'guild_locale',
    )

    def __init__(self, *, data: InteractionPayload, state: ConnectionState):
        self._state: ConnectionState = state
        self._session: ClientSession = state.http._HTTPClient__session  # type: ignore
        self._original_message: Optional[InteractionMessage] = None
        self._from_data(data)

    def _from_data(self, payload: InteractionPayload):
        self.id: Snowflake = int(payload['id'])
        self.type: InteractionType = try_enum(
            InteractionType,
            payload['type'],
        )
        self.token: str = payload['token']
        self.version: int = payload['version']
        self.channel_id: Optional[int] = utils._get_as_snowflake(
            payload,
            'channel_id',
        )
        self.guild_id: Optional[int] = utils._get_as_snowflake(
            payload,
            'guild_id',
        )
        self.application_id: int = int(payload['application_id'])
        self.target_id = payload.get("target_id")

        # Parse the message object
        self.message: Optional[Message]
        try:
            self.message = Message(
                state=self._state,
                channel=self.channel,
                data=payload['message'],
            )
        except KeyError:
            self.message = None

        # The data that the interaction gave back to us - not optional,
        # but documented as optional because it supports pings, but we're
        # just gonna ignore that.
        # This contains all the data ABOUT the interaction that's given
        # back to us
        self.data: InteractionData
        try:
            self.data = payload['data']
        except KeyError:
            self.data = {}  # type: ignore

        # Parse the component that triggered the interaction -
        # this does NOT apply to modals
        self.component: Optional[InteractedComponent] = None
        try:
            if self.message:
                self.component = self.message.components.get_component(  # type: ignore - weird typing
                    self.data['custom_id'],
                )
        except (KeyError, AttributeError):
            pass

        # Parse the main custom ID
        self.custom_id: Union[str, None] = None
        if self.data:
            self.custom_id = self.data.get('custom_id')

        # Parse the given values from the component - this is only used by
        # select components
        self.values: Optional[List[str]] = None
        if self.data and 'values' in self.data:
            self.values = self.data['values']

        # Parse the returned options from the user - this is used by all application
        # commands (including autocorrect)
        self.options: Optional[List[ApplicationCommandInteractionDataOption]]
        self.options = None
        if self.data and 'options' in self.data:
            self.options = [
                ApplicationCommandInteractionDataOption(i)
                for i in self.data['options']
            ]

        # Parse the returned components - this is used by modals
        self.components: Optional[List[InteractedComponent]] = None
        if self.data and 'components' in self.data:
            self.components = [
                InteractedComponent.from_data(i)
                for i in self.data['components']
            ]

        # Parse the user and their permissions
        self.user: Union[User, Member]  # documented as optional for pings
        self._permissions: int = 0
        self._app_permissions: int = 0

        # Store the locales
        self.user_locale = payload.get("locale")
        self.guild_locale = payload.get("guild_locale")

        # Create a user/member object if we can
        if self.guild_id:
            guild = self.guild
            try:
                member = payload['member']  # type: ignore
            except KeyError:
                pass
            else:
                self.user = Member(
                    state=self._state,
                    guild=guild,  # type: ignore - possible data downgrading
                    data=member,  # type: ignore - possible data downgrading
                )
                self._permissions = int(member.get('permissions', 0))
            self._app_permissions = int(payload['app_permissions'])
        else:
            try:
                self.user = User(state=self._state, data=payload['user'])
            except KeyError:
                pass

    @property
    def locale(self) -> str:
        return self.user_locale or self.guild_locale or "en-US"

    @utils.cached_slot_property('_cs_resolved')
    def resolved(self) -> InteractionResolved:
        return InteractionResolved(
            interaction=self,
            data=(self.data or {}).copy().get("resolved", dict()),
            state=self._state,
        )

    @utils.cached_slot_property('_cs_command_name')
    def command_name(self) -> Optional[str]:
        """
        Optional[:class:`str`]: The name of the invoked command.
        Only valid for slash command interactions.
        """

        if self.data is None:
            return
        data = self.data.copy()
        command_name = data.get('name')
        try:
            while command_name:
                if "options" not in data:
                    break
                if data['options'][0]['type'] in [1, 2]:
                    data = data['options'][0]
                    command_name += f" {data['name']}"
                else:
                    break
        finally:
            return command_name

    @property
    def guild(self) -> Optional[Union[Guild, Object]]:
        """
        Optional[:class:`Guild` | :class:`Object`]:
        The guild the interaction was sent from.
        """

        v = self._state and self._state._get_guild(self.guild_id)
        if v:
            return v
        if self.guild_id:
            return Object(self.guild_id)
        return None

    @utils.cached_slot_property('_cs_channel')
    def channel(self) -> Optional[InteractionChannel]:
        """
        Optional[Union[:class:`abc.GuildChannel`, :class:`PartialMessageable`, :class:`Thread`]]:
        The channel the interaction was sent from.

        Note that due to a Discord limitation, DM channels are not resolved
        since there is no data to complete them. These are
        :class:`PartialMessageable` instead.
        """

        guild = self.guild
        channel = None
        if guild and isinstance(guild, Guild):
            channel = guild._resolve_channel(self.channel_id)
        if channel is None:
            if self.channel_id is not None:
                if self.guild_id is not None:
                    type = ChannelType.text
                else:
                    type = ChannelType.private
                return PartialMessageable(
                    state=self._state,
                    id=self.channel_id,
                    type=type,
                )
            return None
        return channel

    @property
    def permissions(self) -> Permissions:
        """
        :class:`Permissions`: The resolved permissions of the member in the
        channel, including overwrites.

        In a non-guild context where this doesn't apply, an empty
        permissions object is returned.
        """

        return Permissions(self._permissions)

    @property
    def app_permissions(self) -> Permissions:
        """
        :class:`Permissions`: The resolved permissions of the
        bot in the channel, including overwrites.

        In a non-guild context where this doesn't apply, an empty
        permissions object is returned.
        """

        return Permissions(self._app_permissions)

    @utils.cached_slot_property('_cs_response')
    def response(self) -> Union[InteractionResponse, HTTPInteractionResponse]:
        """
        :class:`InteractionResponse`: Returns an object responsible for
        handling responding to the interaction.

        A response can only be done once. If secondary messages need to be
        sent, consider using :attr:`followup` instead.
        """

        return InteractionResponse(self)

    @utils.cached_slot_property('_cs_followup')
    def followup(self) -> Webhook:
        """
        :class:`Webhook`: Returns the follow up webhook for
        follow up interactions.
        """

        payload = {
            'id': self.application_id,
            'type': 3,
            'token': self.token,
        }
        v = Webhook.from_state(data=payload, state=self._state)
        v.supports_ephemeral = True
        return v

    async def original_message(self) -> InteractionMessage:
        """
        |coro|

        Fetches the original interaction response message associated with
        the interaction.

        If the interaction response was :meth:`InteractionResponse.send_message`
        then this would return the message that was sent using that response.
        Otherwise, this would return the message that triggered the interaction.

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
        message = InteractionMessage(
            state=state,  # type: ignore
            channel=channel,  # type: ignore
            data=data,
        )
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
            allowed_mentions: Optional[AllowedMentions] = None) -> InteractionMessage:
        """
        |coro|

        Edits the original interaction response message.

        This is a lower level interface to :meth:`InteractionMessage.edit`
        in case you do not want to fetch the message and save an HTTP request.

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
            A list of files to send with the content. This cannot be mixed with
            the ``file`` parameter.
        allowed_mentions: :class:`AllowedMentions`
            Controls the mentions being processed in this message.
            See :meth:`.abc.Messageable.send` for more information.
        components: Optional[:class:`~discord.ui.MessageComponents`]
            The set of message components to update the message with. If
            ``None`` is passed then the components are removed.

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

        previous_mentions: Optional[AllowedMentions]
        previous_mentions = self._state.allowed_mentions
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
        message = InteractionMessage(
            state=self._state,
            channel=self.channel,  # type: ignore
            data=data,
        )
        return message

    async def delete_original_message(self) -> None:
        """
        |coro|

        Deletes the original interaction response message.

        This is a lower level interface to :meth:`InteractionMessage.delete`
        in case you do not want to fetch the message and save an HTTP request.

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


class CommandInteraction(Interaction):
    """
    Type-hint friendly version of the :class:`Interaction` object for
    interaction commands.
    """
    command_name: str
    custom_id: None
    component: None
    components: None
    options: List[ApplicationCommandInteractionDataOption]
    values: None


class AutocompleteInteraction(Interaction):
    """
    Type-hint friendly version of the :class:`Interaction` object for
    autocomplete interactions.
    """
    command_name: str
    custom_id: None
    component: None
    components: None
    options: List[ApplicationCommandInteractionDataOption]
    values: None


class ComponentInteraction(Interaction):
    """
    Type-hint friendly version of the :class:`Interaction` object for
    component interactions.
    """
    command_name: None
    custom_id: str
    component: InteractedComponent
    components: None
    options: None
    values: List[str]


class ModalInteraction(Interaction):
    """
    Type-hint friendly version of the :class:`Interaction` object for
    modal interactions.
    """
    command_name: None
    custom_id: str
    component: Modal
    components: List[InteractedComponent]
    options: None
    values: None


class InteractionResponse:
    """
    Represents a Discord interaction response.

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
        """
        :class:`bool`: Indicates whether an interaction response
        has been done before.

        An interaction can only be responded to once.
        """

        return self._responded

    async def defer(self, *, ephemeral: bool = False) -> None:
        """
        |coro|

        Defers the interaction response.

        This is typically used when the interaction is acknowledged
        and a secondary action will be done later.

        Parameters
        -----------
        ephemeral: :class:`bool`
            Indicates whether the deferred message will eventually
            be ephemeral.
            This only applies for interactions of type
            :attr:`InteractionType.application_command`.

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

        if data:
            data = {
                "type": defer_type,
                "data": data,
            }
        else:
            data = {
                "type": defer_type,
            }

        if defer_type:
            adapter = async_context.get()
            await adapter.create_interaction_response(
                parent.id,
                parent.token,
                session=parent._session,
                payload=data,
            )
            self._responded = True

    async def defer_update(self) -> None:
        """
        |coro|

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
            payload = {"type": defer_type}
            adapter = async_context.get()
            await adapter.create_interaction_response(
                parent.id,
                parent.token,
                session=parent._session,
                payload=payload,
            )
            self._responded = True

    async def pong(self) -> None:
        """
        |coro|

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

        data = {
            "type": InteractionResponseType.pong.value,
        }

        parent = self._parent
        if parent.type is InteractionType.ping:
            adapter = async_context.get()
            await adapter.create_interaction_response(
                parent.id,
                parent.token,
                session=parent._session,
                payload=data,
            )
            self._responded = True

    async def send_autocomplete(
            self,
            options: List[ApplicationCommandOptionChoice] = None) -> None:
        """
        |coro|

        Responds to this interaction by sending a message.

        .. versionadded:: 0.0.4

        Parameters
        -----------
        options: typing.List[:class:`ApplicationCommandOptionChoice`]
            The options that you want to send back to Discord.

        Raises
        -------
        HTTPException
            Sending the message failed.
        ValueError
            The length of ``options`` was invalid.
        InteractionResponded
            This interaction has already been responded to before.
        """

        if self._responded:
            raise InteractionResponded(self._parent)

        parent = self._parent
        payload = {
            "type": InteractionResponseType.autocomplete.value,
            "data": {
                "choices": [i.to_json() for i in options or list()],
            },
        }

        adapter = async_context.get()
        await adapter.create_interaction_response(
            parent.id,
            parent.token,
            session=parent._session,
            payload=payload,
        )

        self._responded = True

    async def send_modal(
            self,
            modal: Modal) -> None:
        """
        |coro|

        Reponds to the interaction by sending a modal back to the user.

        .. versionadded:: 0.0.5

        Parameters
        -----------
        modal: Modal
            The modal that you want to send to the user.

        Raises
        -------
        HTTPException
            Sending the message failed.
        InteractionResponded
            This interaction has already been responded to before.
        """

        if self._responded:
            raise InteractionResponded(self._parent)

        parent = self._parent
        payload = {
            "type": InteractionResponseType.modal.value,
            "data": modal.to_dict(),
        }

        adapter = async_context.get()
        await adapter.create_interaction_response(
            parent.id,
            parent.token,
            session=parent._session,
            payload=payload,
        )

        self._responded = True

    async def send_message(
            self,
            content: Optional[Any] = None,
            *,
            embed: Embed = MISSING,
            embeds: List[Embed] = MISSING,
            file: File = MISSING,
            files: List[File] = MISSING,
            components: MessageComponents = MISSING,
            tts: bool = False,
            ephemeral: bool = False,
            allowed_mentions: AllowedMentions = None) -> None:
        """
        |coro|

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
        file: :class:`File`
            The file to upload. This cannot be mixed with ``files`` parameter.
        files: List[:class:`File`]
            A list of files to send with the content. This cannot be mixed with the
            ``file`` parameter.
        tts: :class:`bool`
            Indicates if the message should be sent using text-to-speech.
        components: :class:`discord.ui.MessageComponents`
            The components to send with the messasge.
        ephemeral: :class:`bool`
            Indicates if the message should only be visible to the user who
            started the interaction.
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

        parent = self._parent
        params = handle_message_parameters(
            content=content,
            tts=tts,
            file=file,
            files=files,
            embed=embed,
            embeds=embeds,
            ephemeral=ephemeral,
            components=components,
            allowed_mentions=allowed_mentions,
            previous_allowed_mentions=parent._state.allowed_mentions,
            type=InteractionResponseType.channel_message.value,
        )

        adapter = async_context.get()
        await adapter.create_interaction_response(
            parent.id,
            parent.token,
            session=parent._session,
            payload=params.payload,
            multipart=params.multipart,
            files=params.files,
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
            allowed_mentions: Optional[AllowedMentions] = MISSING) -> None:
        """
        |coro|

        Responds to this interaction by editing the original message of
        a component interaction.

        Parameters
        -----------
        content: Optional[:class:`str`]
            The new content to replace the message with. ``None`` removes the
            content.
        embeds: List[:class:`Embed`]
            A list of embeds to edit the message with.
        embed: Optional[:class:`Embed`]
            The embed to edit the message with. ``None`` suppresses the embeds.
            This should not be mixed with the ``embeds`` parameter.
        attachments: List[:class:`Attachment`]
            A list of attachments to keep in the message. If ``[]`` is passed
            then all attachments are removed.
        components: Optional[:class:`~discord.ui.MessageComponents`]
            The updated components to update this message with. If ``None`` is
            passed then the components are removed.

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
            raise TypeError(
                'cannot mix both embed and embeds keyword arguments',
            )

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
                    payload['allowed_mentions'] = (
                        parent_state
                        .allowed_mentions
                        .merge(allowed_mentions).to_dict()
                    )
                else:
                    payload['allowed_mentions'] = allowed_mentions.to_dict()
            elif parent_state.allowed_mentions is not None:
                payload['allowed_mentions'] = (
                    parent_state
                    .allowed_mentions
                    .to_dict()
                )

        payload = {
            "type": InteractionResponseType.message_update.value,
            "data": payload,
        }

        adapter = async_context.get()
        await adapter.create_interaction_response(
            parent.id,
            parent.token,
            session=parent._session,
            payload=payload,
        )

        self._responded = True


class _MultipartWriter(object):

    def __init__(self):
        self.buffer = bytearray()

    async def write(self, data):
        self.buffer.extend(data)


class HTTPInteractionResponse(InteractionResponse):
    """
    Represents a Discord interaction response.

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
        """
        |coro|

        Defers the interaction response.

        This is typically used when the interaction is acknowledged
        and a secondary action will be done later.

        Parameters
        -----------
        ephemeral: :class:`bool`
            Indicates whether the deferred message will eventually be ephemeral.
            This only applies for interactions of type
            :attr:`InteractionType.application_command`.

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
        """
        |coro|

        Defers the interaction response.

        This is typically used when the interaction is acknowledged
        and a secondary action will be done later.

        This is only usable if the interaction spawned from a component
        interaction.

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
        """
        |coro|

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
            file: File = MISSING,
            files: List[File] = MISSING,
            components: MessageComponents = MISSING,
            tts: bool = False,
            ephemeral: bool = False,
            allowed_mentions: AllowedMentions = None) -> None:
        """
        |coro|

        Responds to this interaction by sending a message.

        Parameters
        -----------
        content: Optional[:class:`str`]
            The content of the message to send.
        embeds: List[:class:`Embed`]
            A list of embeds to send with the content. Maximum of 10. This
            cannot be mixed with the ``embed`` parameter.
        embed: :class:`Embed`
            The rich embed for the content to send. This cannot be mixed with
            ``embeds`` parameter.
        file: :class:`File`
            The file to upload. This cannot be mixed with ``files`` parameter.
        files: List[:class:`File`]
            A list of files to send with the content. This cannot be mixed with
            the ``file`` parameter.
        tts: :class:`bool`
            Indicates if the message should be sent using text-to-speech.
        components: :class:`discord.ui.MessageComponents`
            The components to send with the messasge.
        ephemeral: :class:`bool`
            Indicates if the message should only be visible to the user who
            started the interaction.
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

        params = handle_message_parameters(
            content=content,
            tts=tts,
            file=file,
            files=files,
            embed=embed,
            embeds=embeds,
            ephemeral=ephemeral,
            components=components,
            allowed_mentions=allowed_mentions,
            previous_allowed_mentions=self._parent._state.allowed_mentions,
            type=InteractionResponseType.channel_message.value,
        )

        payload = params.payload
        multipart = params.multipart
        files = params.files

        headers = {}
        to_send = None
        if payload is not None:
            headers['Content-Type'] = 'application/json'
            to_send = utils._to_json(payload).encode()

        for file in files or list():
            file.reset(seek=0)

        if multipart:
            form_data = aiohttp.FormData()
            for p in multipart:
                form_data.add_field(**p)
            writer = _MultipartWriter()
            payload = form_data()
            await payload.write(writer)
            to_send = writer.buffer
            headers = payload.headers

        assert to_send

        self._aiohttp_response.headers.update(headers)
        await self._aiohttp_response.prepare(self._aiohttp_request)
        await self._aiohttp_response.write(to_send)
        await self._aiohttp_response.write_eof()

        self._responded = True

    async def send_autocomplete(
            self,
            options: List[ApplicationCommandOptionChoice] = None) -> None:
        """
        |coro|

        Responds to this interaction by sending a message.

        Parameters
        -----------
        options: typing.List[:class:`ApplicationCommandOptionChoice`]
            The options that you want to send back to Discord.

        Raises
        -------
        HTTPException
            Sending the message failed.
        ValueError
            The length of ``options`` was invalid.
        InteractionResponded
            This interaction has already been responded to before.
        """

        if self._responded:
            raise InteractionResponded(self._parent)

        parent = self._parent
        payload = {
            "type": InteractionResponseType.autocomplete.value,
            "data": {
                "choices": [i.to_json() for i in options or list()],
            },
        }

        self._aiohttp_response.headers["Content-Type"] = "application/json"
        await self._aiohttp_response.prepare(self._aiohttp_request)
        await self._aiohttp_response.write(json.dumps(payload).encode())
        await self._aiohttp_response.write_eof()

        self._responded = True

    async def send_modal(
            self,
            modal: Modal) -> None:
        """
        |coro|

        Reponds to the interaction by sending a modal back to the user.

        .. versionadded:: 0.0.5

        Parameters
        -----------
        modal: Modal
            The modal that you want to send to the user.

        Raises
        -------
        HTTPException
            Sending the message failed.
        InteractionResponded
            This interaction has already been responded to before.
        """

        if self._responded:
            raise InteractionResponded(self._parent)

        parent = self._parent
        payload = {
            "type": InteractionResponseType.modal.value,
            "data": modal.to_dict(),
        }

        self._aiohttp_response.headers["Content-Type"] = "application/json"
        await self._aiohttp_response.prepare(self._aiohttp_request)
        await self._aiohttp_response.write(json.dumps(payload).encode())
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
            allowed_mentions: Optional[AllowedMentions] = MISSING) -> None:
        """
        |coro|

        Responds to this interaction by editing the original message of
        a component interaction.

        Parameters
        -----------
        content: Optional[:class:`str`]
            The new content to replace the message with. ``None`` removes the
            content.
        embeds: List[:class:`Embed`]
            A list of embeds to edit the message with.
        embed: Optional[:class:`Embed`]
            The embed to edit the message with. ``None`` suppresses the embeds.
            This should not be mixed with the ``embeds`` parameter.
        attachments: List[:class:`Attachment`]
            A list of attachments to keep in the message. If ``[]`` is passed
            then all attachments are removed.
        components: Optional[:class:`~discord.ui.MessageComponents`]
            The updated components to update this message with. If ``None`` is
            passed then the components are removed.

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
            raise TypeError(
                'cannot mix both embed and embeds keyword arguments',
            )

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
                    payload['allowed_mentions'] = (
                        parent_state
                        .allowed_mentions
                        .merge(allowed_mentions)
                        .to_dict()
                    )
                else:
                    payload['allowed_mentions'] = allowed_mentions.to_dict()
            elif parent_state.allowed_mentions is not None:
                payload['allowed_mentions'] = (
                    parent_state
                    .allowed_mentions
                    .to_dict()
                )

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

    __slots__ = (
        '_parent',
        '_interaction',
    )

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
    """
    Represents the original interaction response message.

    This allows you to edit or delete the message associated with
    the interaction response. To retrieve this object see
    :meth:`Interaction.original_message`.

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
            allowed_mentions: Optional[AllowedMentions] = None) -> InteractionMessage:
        """
        |coro|

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
            A list of files to send with the content. This cannot be mixed with
            the ``file`` parameter.
        allowed_mentions: :class:`AllowedMentions`
            Controls the mentions being processed in this message.
            See :meth:`.abc.Messageable.send` for more information.
        components: Optional[:class:`~discord.ui.MessageComponents`]
            The updated components to update this message with. If ``None`` is
            passed then the components are removed.

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
        """
        |coro|

        Deletes the message.

        Parameters
        -----------
        delay: Optional[:class:`float`]
            If provided, the number of seconds to wait before deleting the
            message. The waiting is done in the background and deletion
            failures are ignored.

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
