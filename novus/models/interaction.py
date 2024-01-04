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
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Generic, TypeVar

from ..enums import (
    ApplicationCommandType,
    ApplicationOptionType,
    InteractionResponseType,
    InteractionType,
    Locale,
)
from ..flags import MessageFlags, Permissions
from ..utils import (
    MISSING,
    TranslatedString,
    cached_slot_property,
    generate_repr,
    try_snowflake,
    walk_components,
)
from .application_command import ApplicationCommandOption
from .channel import Channel
from .guild import BaseGuild
from .guild_member import GuildMember
from .message import Attachment, Message
from .role import Role
from .ui.action_row import ActionRow
from .ui.select_menu import SelectOption
from .user import User

if TYPE_CHECKING:
    from aiohttp import web

    from .. import flags, payloads
    from ..api import HTTPConnection
    from .application_command import ApplicationCommandChoice
    from .file import File
    from .message import AllowedMentions, Embed, WebhookMessage
    from .sticker import Sticker
    from .ui.component import InteractableComponent

__all__ = (
    'InteractionResolved',
    'InteractionData',
    'ApplicationCommandData',
    'InteractionOption',
    'ContextComandData',
    'MessageComponentData',
    'ModalSubmitData',
    'Interaction',
    'GuildInteraction',
)


class InteractionResolved:
    """
    An object containing resolved models from interactions.

    Attributes
    ----------
    users : list[novus.User]
        The users from the interaction.
    members : list[novus.GuildMember]
        The members from the interaction.
    roles : list[novus.Role]
        The roles from the interaction.
    channels : list[novus.Channel]
        The channels from the interaction.
    messages : list[novus.Message]
        The messages from the interaction.
    attachments : list[novus.Attachment]
        The attachments from the interaction.
    """

    __slots__ = (
        'state',
        'data',
        '_cs_users',
        '_cs_members',
        '_cs_roles',
        '_cs_channels',
        '_cs_messages',
        '_cs_attachments',
        'guild',
    )

    def __init__(
            self,
            *,
            state: HTTPConnection,
            data: payloads.InteractionResolved | None,
            guild: BaseGuild | None = None):
        self.state = state
        self.data = data or {}
        self.guild: BaseGuild | None = guild

    __repr__ = generate_repr(())

    @cached_slot_property("_cs_users")
    def users(self) -> dict[int, User]:
        data = self.data.get("users")
        if data is None:
            return {}
        ret: dict[int, User] = {}
        for d in data.values():
            u = User(state=self.state, data=d)
            ret[u.id] = u
        return ret

    @cached_slot_property("_cs_members")
    def members(self) -> dict[int, GuildMember]:
        data = self.data.get("members")
        if data is None:
            return {}
        ret: dict[int, GuildMember] = {}
        for k, d in data.items():
            u = GuildMember(
                state=self.state,
                data=d,
                user=self.users[int(k)],
                guild_id=self.guild.id if self.guild else None,
            )
            ret[u.id] = u
        return ret

    @cached_slot_property("_cs_roles")
    def roles(self) -> dict[int, Role]:
        data = self.data.get("roles")
        if data is None:
            return {}
        ret: dict[int, Role] = {}
        for d in data.values():
            u = Role(
                state=self.state,
                data=d,
                guild_id=self.guild.id if self.guild else None,
            )
            ret[u.id] = u
        return ret

    @cached_slot_property("_cs_channels")
    def channels(self) -> dict[int, Channel]:
        data = self.data.get("channels")
        if data is None:
            return {}
        ret: dict[int, Channel] = {}
        for d in data.values():
            u = Channel(
                state=self.state,
                data=d,
            )
            ret[u.id] = u
        return ret

    @cached_slot_property("_cs_messages")
    def messages(self) -> dict[int, Message]:
        data = self.data.get("messages")
        if data is None:
            return {}
        ret: dict[int, Message] = {}
        for d in data.values():
            u = Message(
                state=self.state,
                data=d,
            )
            ret[u.id] = u
        return ret

    @cached_slot_property("_cs_attachments")
    def attachments(self) -> dict[int, Attachment]:
        data = self.data.get("attachments")
        if data is None:
            return {}
        ret: dict[int, Attachment] = {}
        for d in data.values():
            u = Attachment(data=d)
            ret[u.id] = u
        return ret


class InteractionOption:
    """
    Data from an option in an interaction.
    """

    name: str
    type: ApplicationOptionType
    value: str | int | bool | None
    options: list[InteractionOption]
    focused: bool

    def __init__(self, *, data: payloads.InteractionDataOption):
        self.name = data['name']
        self.type = ApplicationOptionType(data['type'])
        self.value = data.get('value')
        self.options = [
            InteractionOption(data=d)
            for d in data.get("options", [])
        ]
        self.focused = data.get("focused", False)

    __repr__ = generate_repr(('name', 'type', 'value', 'options',))


class InteractionData:
    """
    Data associated with an interaction.
    """


class ApplicationCommandData(InteractionData):
    """
    Data associated with an application command interaction.

    Attributes
    ----------
    id : int
        The ID of the command that was run.
    name : str
        The name of the command that was run.
    type : CommandType
        The type of the command that was run.
    resolved : InteractionResolved
        A resolved set of models for the interaction.
    options : list[novus.ApplicationCommandOption]
        A list of options that was run.
    guild : novus.Guild | None
        The guild that the command was run in.
    """

    id: int
    name: str
    type: ApplicationCommandType
    resolved: InteractionResolved
    options: list[InteractionOption]
    guild: BaseGuild | None

    def __init__(
            self,
            *,
            parent: Interaction,
            data: payloads.ApplicationComandData):
        self.parent = parent
        self.id = try_snowflake(data["id"])
        self.name = data["name"]
        self.type = ApplicationCommandType(data["type"])
        self.guild = self.parent.guild
        self.resolved = InteractionResolved(
            state=self.parent.state,
            data=data.get("resolved"),
            guild=self.guild,
        )
        self.options = [
            InteractionOption(data=d)
            for d in data.get("options", [])
        ]

    __repr__ = generate_repr(('id', 'type',))


class ContextComandData(ApplicationCommandData):
    """
    Data associated with a context command interaction.

    Attributes
    ----------
    id : int
        The ID of the command that was run.
    name : str
        The name of the command that was run.
    type : CommandType
        The type of the command that was run.
    resolved : InteractionResolved
        A resolved set of models for the interaction.
    options : list[novus.ApplicationCommandOption]
        A list of options that was run.
    guild : novus.Guild | None
        The guild that the command was run in.
    target: novus.Message | novus.User | novus.GuildMember
        The entity that was targeted by the command.
    """

    id: int
    name: str
    type: ApplicationCommandType
    resolved: InteractionResolved
    options: list[ApplicationCommandOption]  # type: ignore  # Incompatible with supertype
    guild: BaseGuild | None
    target: Message | User | GuildMember

    def __init__(
            self,
            *,
            parent: Interaction,
            data: payloads.ApplicationComandData):
        self.parent = parent
        self.id = try_snowflake(data["id"])
        self.name = data["name"]
        self.type = ApplicationCommandType(data["type"])
        self.guild = self.parent.guild
        self.resolved = InteractionResolved(
            state=self.parent.state,
            data=data.get("resolved"),
            guild=self.guild,
        )
        self.options = [
            ApplicationCommandOption._from_data(d)
            for d in data.get("options", [])
        ]
        self.guild = self.parent.state.cache.get_guild(data.get("guild_id"))
        target_id = try_snowflake(data.get("target_id"))
        self.target = None  # pyright: ignore
        if self.type == ApplicationCommandType.message:
            for k, v in self.resolved.messages.items():
                if k == target_id:
                    self.target = v
                    break
        elif self.type == ApplicationCommandType.user:
            for k, v in self.resolved.members.items():
                if k == target_id:
                    self.target = v
                    break
            else:
                for k, v in self.resolved.users.items():
                    if k == target_id:
                        self.target = v
                        break
        assert self.target is not None

    __repr__ = generate_repr(('id', 'type', 'target',))


class MessageComponentData(InteractionData):
    """
    Data associated with a message component interaction.

    Attributes
    ----------
    custom_id : str
    component : novus.Component
    values : list[novus.SelectOption]
    """

    custom_id: str
    component: InteractableComponent
    values: list[SelectOption]

    def __init__(self, *, parent: Interaction, data: payloads.MessageComponentData):
        self.parent = parent
        self.custom_id = data["custom_id"]
        self.values = [
            SelectOption._from_data(d)
            for d in data.get("values", [])
        ]
        self.component = None  # pyright: ignore  # About to be sete again
        assert self.parent.message
        for i in walk_components(self.parent.message.components):
            if i.custom_id == self.custom_id:
                self.component = i
                break
        if self.component is None:
            raise ValueError("Missing component from interactable component")

    __repr__ = generate_repr(('component',))


class ModalSubmitData(InteractionData):
    """
    Data associated with a modal interaction.

    Attributes
    ----------
    custom_id : str
    components : list[novus.ActionRow]
    """

    custom_id: str
    components: list[ActionRow]

    def __init__(self, *, parent: Interaction, data: payloads.ModalSubmitData):
        self.parent = parent
        self.custom_id = data["custom_id"]
        self.components = [
            ActionRow._from_data(d)
            for d in data["components"]
        ]

    __repr__ = generate_repr(('custom_id',))

    def __getitem__(self, index: int) -> ActionRow:
        return self.components[index]


IData = TypeVar(
    "IData",
    None,
    ApplicationCommandData,
    ContextComandData,
    MessageComponentData,
    ModalSubmitData,
)


class Interaction(Generic[IData]):
    """
    An interaction received from Discord.

    .. note::

        Novus silently ignores the possibility of ``PING`` interactions
        existing. It is simply easier that way.

    Attributes
    ----------
    id: int
        The ID of the interaction.
    application_id: int
        The ID of the application receiving the interaction. Usually your bot's
        ID.
    type: novus.InteractionType
        The type of the interaction.
    data: ApplicationComandData | ContextComandData | MessageComponentData | ModalSubmitData | None
        The data associated with the interaction.
    guild: novus.Guild | None
        The guild that the interaction was run in.
    channel: novus.Channel
        The channel that the interaction was run in.
    user: novus.GuildMember | novus.User
        The user who ran the interaction.
    token: str
        The token associated with the interaction response.
    message: novus.Message | None
        The message associated with the interaction. Will only be set if the
        interaction was spawned from a message (ie from a component).
    app_permissions: novus.Permissions
        The application's permissions within the channel where the interaction
        was called.
    locale: novus.Locale
        The user's locale.
    guild_locale: novus.Locale | None
        The locale of the guild where the interaction was run.
    """

    __slots__ = (
        'state',
        'id',
        'application_id',
        'type',
        'data',
        'guild',
        'channel',
        'user',
        'token',
        'version',
        'message',
        'app_permissions',
        'locale',
        'guild_locale',
        '_responded',
        '_stream',
        '_stream_request',
    )

    id: int
    application_id: int
    type: InteractionType
    data: IData
    guild: BaseGuild | None
    channel: Channel
    user: GuildMember | User
    token: str
    message: Message | None
    app_permissions: Permissions
    locale: Locale
    guild_locale: Locale | None
    _stream: web.StreamResponse | None
    _stream_request: web.Request | None

    def __init__(self, *, state: HTTPConnection, data: payloads.Interaction):
        self.state = state
        self.id = try_snowflake(data["id"])
        self._stream = None
        self._stream_request = None
        self.application_id = try_snowflake(data["application_id"])
        self.type = InteractionType(data["type"])
        self.guild = self.state.cache.get_guild(data.get("guild_id"))
        if self.guild is None and data.get("guild_id"):
            self.guild = BaseGuild(state=state, data={"id": data["guild_id"]})  # pyright: ignore
        channel = self.state.cache.get_channel(data.get("channel_id"))
        if channel is None:
            self.channel = Channel.partial(self.state, data["channel_id"])
        else:
            self.channel = channel
        if "user" in data:
            self.user = User(
                state=self.state,
                data=data["user"],
            )
        elif "member" in data:
            self.user = GuildMember(
                state=self.state,
                data=data["member"],
                guild_id=self.guild.id,  # pyright: ignore
            )
        else:
            self.user = None  # pyright: ignore  # Ping interactions :(
        self.token = data["token"]
        self.version = data["version"]
        if "message" in data:
            self.message = Message(state=self.state, data=data["message"])
        else:
            self.message = None
        if "app_permissions" in data:
            self.app_permissions = Permissions(int(data["app_permissions"]))
        else:
            self.app_permissions = Permissions.all()
        self.locale = Locale(data["locale"])
        if "guild_locale" in data:
            self.guild_locale = Locale(data["guild_locale"])
        else:
            self.guild_locale = None
        data_object = None
        if "data" in data:
            data_dict = data["data"]
            if self.type == InteractionType.application_command:
                assert "type" in data_dict
                command_type = data_dict.get("type", 1)
                if command_type == ApplicationCommandType.chat_input.value:
                    data_object = ApplicationCommandData(
                        parent=self,
                        data=data_dict,  # pyright: ignore
                    )
                else:
                    data_object = ContextComandData(
                        parent=self,
                        data=data_dict,  # pyright: ignore
                    )
            if self.type == InteractionType.message_component:
                data_object = MessageComponentData(  # type: ignore
                    parent=self,
                    data=data_dict,  # pyright: ignore
                )
            if self.type == InteractionType.autocomplete:
                data_object = ApplicationCommandData(
                    parent=self,
                    data=data_dict,  # pyright: ignore
                )
            if self.type == InteractionType.modal_submit:
                data_object = ModalSubmitData(  # type: ignore
                    parent=self,
                    data=data_dict,  # pyright: ignore
                )
        self.data = data_object  # type: ignore  # Apparently this isn't valid with generics
        self._responded = False

    __repr__ = generate_repr((
        'id',
        'custom_id',
        'type',
        'guild',
        'application_id',
        'data',
    ))

    @property
    def custom_id(self) -> str | None:
        if self.data is None:
            return None
        return getattr(self.data, "custom_id", None)

    def _(
            self,
            string: str,
            guild: int | bool = 1,
            user: int | bool = 0) -> str:
        ts = TranslatedString(string, context=self, guild=guild, user=user)
        return str(ts)

    # API methods

    def _get_response_partial(self: Interaction) -> Callable[..., Awaitable[None]]:
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
            content: str = MISSING,
            *,
            tts: bool = MISSING,
            embeds: list[Embed] = MISSING,
            allowed_mentions: AllowedMentions = MISSING,
            components: list[ActionRow] = MISSING,
            message_reference: Message = MISSING,
            stickers: list[Sticker] = MISSING,
            files: list[File] = MISSING,
            flags: MessageFlags = MISSING,
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

    async def fetch_original(
            self: Interaction) -> WebhookMessage:
        """
        Get the original message associated with the interaction.
        """

        return await self.state.interaction.get_original_interaction_response(
            self.application_id,
            self.token,
        )

    async def edit_original(
            self: Interaction,
            **kwargs: Any) -> WebhookMessage:
        """
        Edit the original message associated with the interaction.
        """

        return await self.state.interaction.edit_original_interaction_response(
            self.application_id,
            self.token,
            **kwargs,
        )


class GuildInteraction(Interaction):
    """
    A type-hinting version of interactions that have all guild attributes set
    properly for you.
    """

    guild: BaseGuild
    user: GuildMember
