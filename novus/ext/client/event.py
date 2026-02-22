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
from collections.abc import Awaitable
from typing import TYPE_CHECKING, Any, Callable, TypeAlias, TypeVar, Union

import novus
from novus.models.audit_log import AuditLogEntry
from novus.models.invite import Invite
from novus.models.reaction import Reaction

if TYPE_CHECKING:
    from novus import types as t
    from novus.models import (  # AuditLog,; Emoji,; Sticker,
        ApplicationCommandData,
        BaseGuild,
        Channel,
        ContextComandData,
        Guild,
        GuildMember,
        Interaction,
        Message,
        ModalSubmitData,
        Role,
        User,
    )
    DMMessage: TypeAlias = t.DMMessage
    GuildMessage: TypeAlias = t.GuildMessage

__all__ = (
    "event",
    "EventListener",
    "EventBuilder",
)


class EventListener:
    """
    An object that listens for an event.
    """

    __slots__ = (
        'event',
        'func',
        'predicate',
        'owner',
    )

    def __init__(
            self,
            event_name: str,
            func: Callable[..., Awaitable[Any]],
            predicate: Callable[..., bool] | None = None) -> None:
        self.event = event_name
        self.func: Callable[..., Awaitable[Any]] = func
        self.predicate: Callable[..., bool] = lambda *x: True
        if predicate:
            self.predicate = predicate
        self.owner: Any = None

    async def run(self, *args: Any, **kwargs: Any) -> None:
        await self.func(self.owner, *args, **kwargs)


Self: TypeAlias = Any  # Named Any
AA = Awaitable[Any]  # Any awaitable
EL: TypeAlias = EventListener
T = TypeVar("T")
T2 = TypeVar("T2")
T3 = TypeVar("T3")
W0 = Callable[[Self], AA]  # Wrapper
W = Callable[[Self, T], AA]  # Wrapper
W2 = Callable[[Self, T, T2], AA]  # Wrapper
W3 = Callable[[Self, T, T2, T3], AA]  # Wrapper
WEL = Callable[[Callable[[Self, Any], AA]], EL]  # Wrapped event listener


class EventBuilder:

    __slots__ = ()

    @staticmethod
    def __call__(
            event_name: str,
            predicate: Callable[..., bool] | None = None) -> WEL:
        """
        Capture any event by its name.

        This function is *not* stable, as raw gateway events are captured and processed by the
        library in order to construct the high level objects that are passed to event listeners.
        This means that if you capture a raw gateway event, you will be bypassing all of the
        processing that the library does, and you will be receiving the raw payloads from the
        gateway. This can be useful for debugging or for capturing events that are not yet
        supported by the library, but it is not recommended for general use.

        Parameters
        ----------
        event_name : str
            The name of the event to capture. This is the same as the event name
            used in the gateway, case sensitive.

        Example
        -------
        >>> @client.event("MESSAGE_CREATE")
        >>> async def event_capture(self, payload):
        >>>     pass
        """

        def wrapper(func: Callable[..., AA]) -> EL:
            return EventListener(event_name, func, predicate)
        return wrapper  # pyright: ignore

    @classmethod
    def filtered_component(cls, match_string: str) -> WEL:
        """
        Match an component or modal interaction based on a regex
        match with its custom ID.

        Parameters
        ----------
        match_string : str
            The regex that should match with the component's custom
            ID.

        Examples
        --------
        >>> @client.event.filtered_component("CUSTOM_ID_GOES_HERE")
        >>> async def button_press(self, interaction: novus.Interaction):
        >>>     pass

        >>> @client.event.filtered_component(r"^my_button_\\d+$")
        >>> async def button_press(self, interaction: novus.Interaction):
        >>>     pass
        """

        def wrapper(func: W[t.ComponentGI | t.ComponentI]) -> EL:
            return EventListener(
                "INTERACTION_CREATE",
                func,
                lambda i: bool(
                    i.type in [
                        novus.InteractionType.MESSAGE_COMPONENT,
                        novus.InteractionType.MODAL_SUBMIT,
                    ]
                    and i.custom_id
                    and re.search(match_string, i.custom_id)
                ),
            )
        return wrapper

    @classmethod
    def ready(cls, func: W0) -> EL:
        """
        Capture the ready event from the gateway.

        Example
        -------
        >>> @client.event.ready
        >>> async def on_ready(self):
        >>>     print("Ready!")
        """
        return EventListener("READY", func)

    @classmethod
    def component(cls, func: W[t.ComponentI] | W[t.ComponentGI]) -> EL:
        """
        Capture a component interaction from the gateway or interaction webhook.

        Example
        -------
        >>> @client.event.component
        >>> async def button_press(self, interaction: novus.Interaction):
        >>>     pass
        """

        return EventListener(
            "INTERACTION_CREATE",
            func,
            lambda i: i.type == novus.InteractionType.MESSAGE_COMPONENT,
        )

    @classmethod
    def modal(cls, func: W[Interaction[ModalSubmitData]]) -> EL:
        """
        Capture a modal submit interaction from the gateway or interaction webhook.

        Example
        -------
        >>> @client.event.modal
        >>> async def modal_submit(self, interaction: novus.Interaction):
        >>>     pass
        """

        return EventListener(
            "INTERACTION_CREATE",
            func,
            lambda i: i.type == novus.InteractionType.MODAL_SUBMIT,
        )

    @classmethod
    def command(
            cls,
            func: Union[W[Interaction[ContextComandData]],
                        W[Interaction[ApplicationCommandData]],
                        W[Interaction[ContextComandData] | Interaction[ApplicationCommandData]],
                        W[Interaction[ContextComandData | ApplicationCommandData]]]) -> EL:
        """
        Capture a command interaction from the gateway or interaction webhook.

        Example
        -------
        >>> @client.event.command
        >>> async def command(self, interaction: novus.Interaction):
        >>>     pass
        """

        return EventListener(
            "INTERACTION_CREATE",
            func,
            lambda i: i.type == novus.InteractionType.APPLICATION_COMMAND,
        )

    @classmethod
    def autocomplete(cls, func: W[Interaction[ApplicationCommandData]]) -> EL:
        """
        Capture an autocomplete interaction from the gateway or interaction webhook.

        .. seealso:: :meth:`novus.ext.client.Command.autocomplete`

        Example
        -------
        >>> @client.event.autocomplete
        >>> async def autocomplete(self, interaction: novus.Interaction):
        >>>     pass
        """

        return EventListener(
            "INTERACTION_CREATE",
            func,
            lambda i: i.type == novus.InteractionType.AUTOCOMPLETE,
        )

    @classmethod
    def raw_guild_create(cls, func: W[int]) -> EL:
        """
        Capture the raw guild create event from the gateway.

        This is useful for when you want to capture the guild create event before the library has
        processed it, or if you want to capture the raw payload from the gateway for debugging
        purposes.

        Example
        -------
        >>> @client.event.raw_guild_create
        >>> async def on_raw_guild_create(self, guild_id: int):
        >>>     pass
        """
        return EventListener("RAW_GUILD_CREATE", func)

    @classmethod
    def guild_create(cls, func: W[Guild]) -> EL:
        """
        Capture the guild create event from the gateway.

        Example
        -------
        >>> @client.event.guild_create
        >>> async def on_guild_create(self, guild: novus.Guild):
        >>>     pass
        """

        return EventListener("GUILD_CREATE", func)

    @classmethod
    def raw_guild_update(cls, func: W[Guild]) -> EL:
        """
        Capture the raw guild update event from the gateway.

        This is useful for when you want to capture the guild update event before the library has
        processed it, or if you want to capture the raw payload from the gateway for debugging
        purposes.

        Example
        -------
        >>> @client.event.raw_guild_update
        >>> async def on_raw_guild_update(self, guild: novus.Guild):
        >>>     pass
        """

        return EventListener("RAW_GUILD_UPDATE", func)

    @classmethod
    def guild_update(cls, func: W2[Guild, Guild]) -> EL:
        """
        Capture the guild update event from the gateway.

        Example
        -------
        >>> @client.event.guild_update
        >>> async def on_guild_update(self, before: novus.Guild, after: novus.Guild):
        >>>     pass
        """

        return EventListener("GUILD_UPDATE", func)

    @classmethod
    def raw_guild_delete(cls, func: W[int]) -> EL:
        """
        Capture the raw guild delete event from the gateway.

        This is useful for when you want to capture the guild delete event before the library has
        processed it, or if you want to capture the raw payload from the gateway for debugging
        purposes.

        Example
        -------
        >>> @client.event.raw_guild_delete
        >>> async def on_raw_guild_delete(self, guild_id: int):
        >>>     pass
        """

        return EventListener("RAW_GUILD_DELETE", func)

    @classmethod
    def guild_delete(cls, func: W[Guild]) -> EL:
        """
        Capture the guild delete event from the gateway.

        Example
        -------
        >>> @client.event.guild_delete
        >>> async def on_guild_delete(self, guild: novus.Guild):
        >>>     pass
        """

        return EventListener("GUILD_DELETE", func)

    @classmethod
    def raw_typing(cls, func: W2[int, int]) -> EL:
        """
        Capture the raw typing event from the gateway.

        This is useful for when you want to capture the typing event before the library has
        processed it, or if you want to capture the raw payload from the gateway for debugging
        purposes.

        Example
        -------
        >>> @client.event.raw_typing
        >>> async def on_raw_typing(self, channel_id: int, user_id: int):
        >>>     pass
        """

        return EventListener("RAW_TYPING", func)

    @classmethod
    def typing(cls, func: W2[Channel, User | GuildMember]) -> EL:
        """
        Capture the typing event from the gateway.

        Example
        -------
        >>> @client.event.typing
        >>> async def on_typing(self, channel: novus.Channel, user: novus.User | novus.GuildMember):
        >>>     pass
        """
        return EventListener("TYPING", func)

    @classmethod
    def message(cls, func: W[Message]) -> EL:
        """
        Capture the message create event from the gateway.

        Example
        -------
        >>> @client.event.message
        >>> async def on_message(self, message: novus.Message):
        >>>     pass
        """

        return EventListener("MESSAGE_CREATE", func)

    @classmethod
    def guild_message(cls, func: W[GuildMessage]) -> EL:
        """
        Capture the message create event from the gateway for messages sent in guilds.

        Example
        -------
        >>> @client.event.guild_message
        >>> async def on_guild_message(self, message: novus.Message):
        >>>     pass
        """

        return EventListener("MESSAGE_CREATE", func, lambda m: m.guild is not None)

    @classmethod
    def dm_message(cls, func: W[DMMessage]) -> EL:
        """
        Capture the message create event from the gateway for messages sent in DMs.

        Example
        -------
        >>> @client.event.dm_message
        >>> async def on_dm_message(self, message: novus.Message):
        >>>     pass
        """

        return EventListener("MESSAGE_CREATE", func, lambda m: m.guild is None)

    @classmethod
    def raw_message_edit(cls, func: W[Message]) -> EL:
        """
        Capture the raw message update event from the gateway.

        This is useful for when you want to capture the message update event before the library has
        processed it, or if you want to capture the raw payload from the gateway for debugging
        purposes.

        Example
        -------
        >>> @client.event.raw_message_edit
        >>> async def on_raw_message_edit(self, message: novus.Message):
        >>>     pass
        """

        return EventListener("RAW_MESSAGE_UPDATE", func)

    @classmethod
    def message_edit(cls, func: W2[Message, Message]) -> EL:
        """
        Capture the message update event from the gateway.

        Example
        -------
        >>> @client.event.message_edit
        >>> async def on_message_edit(self, before: novus.Message, after: novus.Message):
        >>>     pass
        """

        return EventListener("MESSAGE_UPDATE", func)

    @classmethod
    def raw_message_delete(cls, func: W2[int, int]) -> EL:
        """
        Capture the raw message delete event from the gateway.

        This is useful for when you want to capture the message delete event before the library has
        processed it, or if you want to capture the raw payload from the gateway for debugging
        purposes.

        Example
        -------
        >>> @client.event.raw_message_delete
        >>> async def on_raw_message_delete(self, message_id: int, channel_id: int):
        >>>     pass
        """

        return EventListener("RAW_MESSAGE_DELETE", func)

    @classmethod
    def message_delete(cls, func: W[Message]) -> EL:
        """
        Capture the message delete event from the gateway.

        Example
        -------
        >>> @client.event.message_delete
        >>> async def on_message_delete(self, message: novus.Message):
        >>>     pass
        """

        return EventListener("MESSAGE_DELETE", func)

    @classmethod
    def channel_create(cls, func: W[Channel]) -> EL:
        """
        Capture the channel create event from the gateway.

        Example
        -------
        >>> @client.event.channel_create
        >>> async def on_channel_create(self, channel: novus.Channel):
        >>>     pass
        """

        return EventListener("CHANNEL_CREATE", func)

    @classmethod
    def raw_channel_update(cls, func: W[Channel]) -> EL:
        """
        Capture the raw channel update event from the gateway.

        This is useful for when you want to capture the channel update event before the library has
        processed it, or if you want to capture the raw payload from the gateway for debugging
        purposes.

        Example
        -------
        >>> @client.event.raw_channel_update
        >>> async def on_raw_channel_update(self, channel: novus.Channel):
        >>>     pass
        """

        return EventListener("RAW_CHANNEL_UPDATE", func)

    @classmethod
    def channel_update(cls, func: W2[Channel, Channel]) -> EL:
        """
        Capture the channel update event from the gateway.

        Example
        -------
        >>> @client.event.channel_update
        >>> async def on_channel_update(self, before: novus.Channel, after: novus.Channel):
        >>>     pass
        """

        return EventListener("CHANNEL_UPDATE", func)

    @classmethod
    def channel_delete(cls, func: W[Channel]) -> EL:
        """
        Capture the channel delete event from the gateway.

        Example
        -------
        >>> @client.event.channel_delete
        >>> async def on_channel_delete(self, channel: novus.Channel):
        >>>     pass
        """

        return EventListener("CHANNEL_DELETE", func)

    @classmethod
    def guild_ban_add(cls, func: W2[BaseGuild, User | GuildMember]) -> EL:
        """
        Capture a user being banned from a guild.

        Example
        -------
        >>> @client.event.guild_ban_add
        >>> async def on_guild_ban_add(
        ...         self,
        ...         guild: novus.BaseGuild,
        ...         user: novus.User | novus.GuildMember):
        >>>     pass
        """

        return EventListener("GUILD_BAN_ADD", func)

    @classmethod
    def guild_ban_remove(cls, func: W2[BaseGuild, User]) -> EL:
        """
        Capture a user being unbanned from a guild.

        Example
        -------
        >>> @client.event.guild_ban_remove
        >>> async def on_guild_ban_remove(self, guild: novus.BaseGuild, user: novus.User):
        >>>     pass
        """

        return EventListener("GUILD_BAN_REMOVE", func)

    @classmethod
    def invite_create(cls, func: W[Invite]) -> EL:
        """
        Capture the invite create event from the gateway.

        Example
        -------
        >>> @client.event.invite_create
        >>> async def on_invite_create(self, invite: novus.Invite):
        >>>     pass
        """

        return EventListener("INVITE_CREATE", func)

    @classmethod
    def invite_delete(cls, func: W2[Invite, str]) -> EL:
        """
        Capture the invite delete event from the gateway.

        Example
        -------
        >>> @client.event.invite_delete
        >>> async def on_invite_delete(self, invite: novus.Invite, code: str):
        >>>     pass
        """

        return EventListener("INVITE_DELETE", func)

    @classmethod
    def role_create(cls, func: W[Role]) -> EL:
        """
        Capture the role create event from the gateway.

        Example
        -------
        >>> @client.event.role_create
        >>> async def on_role_create(self, role: novus.Role):
        >>>     pass
        """

        return EventListener("ROLE_CREATE", func)

    @classmethod
    def raw_role_update(cls, func: W[Role]) -> EL:
        """
        Capture the raw role update event from the gateway.

        This is useful for when you want to capture the role update event before the library has
        processed it, or if you want to capture the raw payload from the gateway for debugging
        purposes.

        Example
        -------
        >>> @client.event.raw_role_update
        >>> async def on_raw_role_update(self, role: novus.Role):
        >>>     pass
        """

        return EventListener("RAW_ROLE_UPDATE", func)

    @classmethod
    def role_update(cls, func: W2[Role, Role]) -> EL:
        """
        Capture the role update event from the gateway.

        Example
        -------
        >>> @client.event.role_update
        >>> async def on_role_update(self, before: novus.Role, after: novus.Role):
        >>>     pass
        """

        return EventListener("ROLE_UPDATE", func)

    @classmethod
    def raw_role_delete(cls, func: W2[int, int]) -> EL:
        """
        Capture the raw role delete event from the gateway.

        This is useful for when you want to capture the role delete event before the library has
        processed it, or if you want to capture the raw payload from the gateway for debugging
        purposes.

        Example
        -------
        >>> @client.event.raw_role_delete
        >>> async def on_raw_role_delete(self, role_id: int, guild_id: int):
        >>>     pass
        """

        return EventListener("RAW_ROLE_DELETE", func)

    @classmethod
    def role_delete(cls, func: W[Role]) -> EL:
        """
        Capture the role delete event from the gateway.

        Example
        -------
        >>> @client.event.role_delete
        >>> async def on_role_delete(self, role: novus.Role):
        >>>     pass
        """

        return EventListener("ROLE_DELETE", func)

    @classmethod
    def guild_member_add(cls, func: W[GuildMember]) -> EL:
        """
        Capture a user joining a guild.

        Example
        -------
        >>> @client.event.guild_member_add
        >>> async def on_guild_member_add(self, member: novus.GuildMember):
        >>>     pass
        """

        return EventListener("GUILD_MEMBER_ADD", func)

    @classmethod
    def raw_guild_member_update(cls, func: W[GuildMember]) -> EL:
        """
        Capture the raw guild member update event from the gateway.

        This is useful for when you want to capture the guild member update event before the
        library has processed it, or if you want to capture the raw payload from the gateway for
        debugging purposes.

        Example
        -------
        >>> @client.event.raw_guild_member_update
        >>> async def on_raw_guild_member_update(self, member: novus.GuildMember):
        >>>     pass
        """

        return EventListener("RAW_GUILD_MEMBER_UPDATE", func)

    @classmethod
    def guild_member_update(cls, func: W2[GuildMember, GuildMember]) -> EL:
        """
        Capture the guild member update event from the gateway.

        Example
        -------
        >>> @client.event.guild_member_update
        >>> async def on_guild_member_update(
        ...         self,
        ...         before: novus.GuildMember,
        ...         after: novus.GuildMember):
        >>>     pass
        """

        return EventListener("GUILD_MEMBER_UPDATE", func)

    @classmethod
    def raw_guild_member_remove(cls, func: W2[int, int]) -> EL:
        """
        Capture the raw guild member remove event from the gateway.

        This is useful for when you want to capture the guild member remove event before the
        library has processed it, or if you want to capture the raw payload from the gateway for
        debugging purposes.

        Example
        -------
        >>> @client.event.raw_guild_member_remove
        >>> async def on_raw_guild_member_remove(self, user_id: int, guild_id: int):
        >>>     pass
        """

        return EventListener("RAW_GUILD_MEMBER_REMOVE", func)

    @classmethod
    def guild_member_remove(cls, func: W2[BaseGuild, GuildMember | User]) -> EL:
        """
        Capture a user leaving a guild.

        Example
        -------
        >>> @client.event.guild_member_remove
        >>> async def on_guild_member_remove(
        ...         self,
        ...         guild: novus.BaseGuild,
        ...         member: novus.GuildMember | novus.User):
        >>>     pass
        """

        return EventListener("GUILD_MEMBER_REMOVE", func)

    @classmethod
    def reaction_add(cls, func: W2[User | GuildMember | int, Reaction]) -> EL:
        """
        Capture the reaction add event from the gateway.

        Example
        -------
        >>> @client.event.reaction_add
        >>> async def on_reaction_add(
        ...        self,
        ...        user: novus.User | novus.GuildMember,
        ...        reaction: novus.Reaction):
        >>>     pass
        """

        return EventListener("REACTION_ADD", func)

    @classmethod
    def reaction_remove(cls, func: W2[User | GuildMember | int, Reaction]) -> EL:
        """
        Capture the reaction remove event from the gateway.

        Example
        -------
        >>> @client.event.reaction_remove
        >>> async def on_reaction_remove(
        ...         self,
        ...         user: novus.User | novus.GuildMember,
        ...         reaction: novus.Reaction):
        >>>     pass
        """

        return EventListener("REACTION_REMOVE", func)

    @classmethod
    def audit_log_entry(cls, func: W[AuditLogEntry]) -> EL:
        """
        Capture the audit log entry create event from the gateway.

        Example
        -------
        >>> @client.event.audit_log_entry
        >>> async def on_audit_log_entry(self, entry: novus.AuditLogEntry):
        >>>     pass
        """

        return EventListener("AUDIT_LOG_ENTRY", func)


event = EventBuilder()
