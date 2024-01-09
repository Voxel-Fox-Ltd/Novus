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
        MessageComponentData,
        ModalSubmitData,
        Role,
        User,
    )
    DMMessage: TypeAlias = t.DMMessage
    GuildMessage: TypeAlias = t.GuildMessage

__all__ = (
    'event',
    'EventListener',
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
WEL = Callable[[Callable[[Self, T], Any]], EL]  # Wrapped event listener


class EventBuilder:

    __slots__ = ()

    @staticmethod
    def __call__(
            event_name: str,
            predicate: Callable[..., bool] | None = None) -> WEL:
        def wrapper(func: Callable[..., AA]) -> EL:
            return EventListener(event_name, func, predicate)
        return wrapper  # pyright: ignore

    @classmethod
    def filtered_component(cls, match_string: str) -> WEL[Interaction]:
        """
        Match an component or modal interaction based on a regex
        match with its custom ID.

        Parameters
        ----------
        match_string : str
            The regex that should match with the component's custom
            ID.
        """

        def wrapper(func: W[Interaction] | W[t.ComponentGI]) -> EL:
            return EventListener(
                "INTERACTION_CREATE",
                func,
                lambda i: bool(
                    i.type in [
                        novus.InteractionType.message_component,
                        novus.InteractionType.modal_submit,
                    ]
                    and i.custom_id
                    and re.search(match_string, i.custom_id)
                ),
            )
        return wrapper

    @classmethod
    def ready(cls, func: W0) -> EL:
        return EventListener("READY", func)

    @classmethod
    def component(cls, func: W[Interaction[MessageComponentData]]) -> EL:
        return EventListener(
            "INTERACTION_CREATE",
            func,
            lambda i: i.type == novus.InteractionType.message_component,
        )

    @classmethod
    def modal(cls, func: W[Interaction[ModalSubmitData]]) -> EL:
        return EventListener(
            "INTERACTION_CREATE",
            func,
            lambda i: i.type == novus.InteractionType.modal_submit,
        )

    @classmethod
    def command(
            cls,
            func: Union[W[Interaction[ContextComandData]],
                        W[Interaction[ApplicationCommandData]],
                        W[Interaction[ContextComandData] | Interaction[ApplicationCommandData]],
                        W[Interaction[ContextComandData | ApplicationCommandData]]]) -> EL:
        return EventListener(
            "INTERACTION_CREATE",
            func,
            lambda i: i.type == novus.InteractionType.application_command,
        )

    @classmethod
    def autocomplete(cls, func: W[Interaction[ApplicationCommandData]]) -> EL:
        return EventListener(
            "INTERACTION_CREATE",
            func,
            lambda i: i.type == novus.InteractionType.autocomplete,
        )

    @classmethod
    def raw_guild_create(cls, func: W[int]) -> EL:
        return EventListener("RAW_GUILD_CREATE", func)

    @classmethod
    def guild_create(cls, func: W[Guild]) -> EL:
        return EventListener("GUILD_CREATE", func)

    @classmethod
    def raw_guild_update(cls, func: W[Guild]) -> EL:
        return EventListener("RAW_GUILD_UPDATE", func)

    @classmethod
    def guild_update(cls, func: W2[Guild, Guild]) -> EL:
        return EventListener("GUILD_UPDATE", func)

    @classmethod
    def raw_guild_delete(cls, func: W[int]) -> EL:
        return EventListener("RAW_GUILD_DELETE", func)

    @classmethod
    def guild_delete(cls, func: W[Guild]) -> EL:
        return EventListener("GUILD_DELETE", func)

    @classmethod
    def raw_typing(cls, func: W2[int, int]) -> EL:
        return EventListener("RAW_TYPING", func)

    @classmethod
    def typing(cls, func: W2[Channel, User | GuildMember]) -> EL:
        return EventListener("TYPING", func)

    @classmethod
    def message(cls, func: W[Message]) -> EL:
        return EventListener("MESSAGE_CREATE", func)

    @classmethod
    def guild_message(cls, func: W[GuildMessage]) -> EL:
        return EventListener("MESSAGE_CREATE", func, lambda m: m.guild is not None)

    @classmethod
    def dm_message(cls, func: W[DMMessage]) -> EL:
        return EventListener("MESSAGE_CREATE", func, lambda m: m.guild is None)

    @classmethod
    def raw_message_edit(cls, func: W[Message]) -> EL:
        return EventListener("RAW_MESSAGE_UPDATE", func)

    @classmethod
    def message_edit(cls, func: W2[Message, Message]) -> EL:
        return EventListener("MESSAGE_UPDATE", func)

    @classmethod
    def raw_message_delete(cls, func: W2[int, int]) -> EL:
        return EventListener("RAW_MESSAGE_DELETE", func)

    @classmethod
    def message_delete(cls, func: W[Message]) -> EL:
        return EventListener("MESSAGE_DELETE", func)

    @classmethod
    def channel_create(cls, func: W[Channel]) -> EL:
        return EventListener("CHANNEL_CREATE", func)

    @classmethod
    def raw_channel_update(cls, func: W[Channel]) -> EL:
        return EventListener("RAW_CHANNEL_UPDATE", func)

    @classmethod
    def channel_update(cls, func: W2[Channel, Channel]) -> EL:
        return EventListener("CHANNEL_UPDATE", func)

    @classmethod
    def channel_delete(cls, func: W[Channel]) -> EL:
        return EventListener("CHANNEL_DELETE", func)

    @classmethod
    def guild_ban_add(cls, func: W2[BaseGuild, User | GuildMember]) -> EL:
        return EventListener("GUILD_BAN_ADD", func)

    @classmethod
    def guild_ban_remove(cls, func: W2[BaseGuild, User]) -> EL:
        return EventListener("GUILD_BAN_REMOVE", func)

    @classmethod
    def invite_create(cls, func: W[Invite]) -> EL:
        return EventListener("INVITE_CREATE", func)

    @classmethod
    def invite_delete(cls, func: W2[Invite, str]) -> EL:
        return EventListener("INVITE_DELETE", func)

    @classmethod
    def role_create(cls, func: W[Role]) -> EL:
        return EventListener("ROLE_CREATE", func)

    @classmethod
    def raw_role_update(cls, func: W[Role]) -> EL:
        return EventListener("RAW_ROLE_UPDATE", func)

    @classmethod
    def role_update(cls, func: W2[Role, Role]) -> EL:
        return EventListener("ROLE_UPDATE", func)

    @classmethod
    def raw_role_delete(cls, func: W2[int, int]) -> EL:
        return EventListener("RAW_ROLE_DELETE", func)

    @classmethod
    def role_delete(cls, func: W[Role]) -> EL:
        return EventListener("ROLE_DELETE", func)

    @classmethod
    def guild_member_add(cls, func: W[GuildMember]) -> EL:
        return EventListener("GUILD_MEMBER_ADD", func)

    @classmethod
    def raw_guild_member_update(cls, func: W[GuildMember]) -> EL:
        return EventListener("RAW_GUILD_MEMBER_UPDATE", func)

    @classmethod
    def guild_member_update(cls, func: W2[GuildMember, GuildMember]) -> EL:
        return EventListener("GUILD_MEMBER_UPDATE", func)

    @classmethod
    def raw_guild_member_remove(cls, func: W2[int, int]) -> EL:
        return EventListener("RAW_GUILD_MEMBER_REMOVE", func)

    @classmethod
    def guild_member_remove(cls, func: W2[BaseGuild, GuildMember | User]) -> EL:
        return EventListener("GUILD_MEMBER_REMOVE", func)

    @classmethod
    def reaction_add(cls, func: W2[User | GuildMember | int, Reaction]) -> EL:
        return EventListener("REACTION_ADD", func)

    @classmethod
    def reaction_remove(cls, func: W2[User | GuildMember | int, Reaction]) -> EL:
        return EventListener("REACTION_REMOVE", func)

    @classmethod
    def audit_log_entry(cls, func: W[AuditLogEntry]) -> EL:
        return EventListener("AUDIT_LOG_ENTRY", func)


event = EventBuilder()
