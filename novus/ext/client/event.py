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
from typing import TYPE_CHECKING, Any, Callable, TypeAlias, TypeVar

import novus
from novus.models.audit_log import AuditLogEntry
from novus.models.invite import Invite
from novus.models.reaction import Reaction

if TYPE_CHECKING:
    from novus.models import (
        Channel,
        Interaction,
        Message,
        MessageComponentData,
        TextChannel,
        Guild,
        AuditLog,
        User,
        GuildMember,
        Emoji,
        Sticker,
        Role,
        BaseGuild,
    )

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

    async def run(self, *args, **kwargs) -> None:
        await self.func(self.owner, *args, **kwargs)


Self: TypeAlias = Any  # Named Any
AA = Awaitable[Any]  # Any awaitable
EL: TypeAlias = EventListener
T = TypeVar("T")
T2 = TypeVar("T2")
T3 = TypeVar("T3")
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

        def wrapper(func: W[Interaction]) -> EL:
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
    def component(cls, func: W[Interaction[MessageComponentData]]) -> EL:
        return EventListener(
            "INTERACTION_CREATE",
            func,
            lambda i: i.type == novus.InteractionType.message_component,
        )

    @classmethod
    def modal(cls, func: W[Interaction[MessageComponentData]]) -> EL:
        return EventListener(
            "INTERACTION_CREATE",
            func,
            lambda i: i.type == novus.InteractionType.modal_submit,
        )

    @classmethod
    def command(cls, func: W[Interaction[MessageComponentData]]) -> EL:
        return EventListener(
            "INTERACTION_CREATE",
            func,
            lambda i: i.type == novus.InteractionType.application_command,
        )

    @classmethod
    def autocomplete(cls, func: W[Interaction[MessageComponentData]]) -> EL:
        return EventListener(
            "INTERACTION_CREATE",
            func,
            lambda i: i.type == novus.InteractionType.autocomplete,
        )

    @classmethod
    def raw_guild_create(cls, func: W[int]):
        return EventListener("RAW_GUILD_CREATE", func)

    @classmethod
    def guild_create(cls, func: W[Guild]):
        return EventListener("GUILD_CREATE", func)

    @classmethod
    def raw_guild_update(cls, func: W[Guild]):
        return EventListener("RAW_GUILD_UPDATE", func)

    @classmethod
    def guild_update(cls, func: W2[Guild, Guild]):
        return EventListener("GUILD_UPDATE", func)

    @classmethod
    def raw_guild_delete(cls, func: W[int]):
        return EventListener("RAW_GUILD_DELETE", func)

    @classmethod
    def guild_delete(cls, func: W[Guild]):
        return EventListener("GUILD_DELETE", func)

    @classmethod
    def raw_typing(cls, func: W2[int, int]):
        return EventListener("RAW_TYPING", func)

    @classmethod
    def typing(cls, func: W2[Channel, User | GuildMember]):
        return EventListener("TYPING", func)

    @classmethod
    def message(cls, func: W[Message]):
        return EventListener("MESSAGE_CREATE", func)

    @classmethod
    def raw_message_edit(cls, func: W[Message]):
        return EventListener("RAW_MESSAGE_UPDATE", func)

    @classmethod
    def message_edit(cls, func: W2[Message, Message]):
        return EventListener("MESSAGE_UPDATE", func)

    @classmethod
    def raw_message_delete(cls, func: W2[int, int]):
        return EventListener("RAW_MESSAGE_DELETE", func)

    @classmethod
    def message_delete(cls, func: W[Message]):
        return EventListener("MESSAGE_DELETE", func)

    @classmethod
    def channel_create(cls, func: W[Channel]):
        return EventListener("CHANNEL_CREATE", func)

    @classmethod
    def raw_channel_update(cls, func: W[Channel]):
        return EventListener("RAW_CHANNEL_UPDATE", func)

    @classmethod
    def channel_update(cls, func: W2[Channel, Channel]):
        return EventListener("CHANNEL_UPDATE", func)

    @classmethod
    def channel_delete(cls, func: W[Channel]):
        return EventListener("CHANNEL_DELETE", func)

    @classmethod
    def guild_ban_add(cls, func: W2[BaseGuild, User | GuildMember]):
        return EventListener("GUILD_BAN_ADD", func)

    @classmethod
    def guild_ban_remove(cls, func: W2[BaseGuild, User]):
        return EventListener("GUILD_BAN_REMOVE", func)

    @classmethod
    def invite_create(cls, func: W[Invite]):
        return EventListener("INVITE_CREATE", func)

    @classmethod
    def invite_delete(cls, func: W2[Invite, str]):
        return EventListener("INVITE_DELETE", func)

    @classmethod
    def role_create(cls, func: W[Role]):
        return EventListener("ROLE_CREATE", func)

    @classmethod
    def raw_role_update(cls, func: W[Role]):
        return EventListener("RAW_ROLE_UPDATE", func)

    @classmethod
    def role_update(cls, func: W2[Role, Role]):
        return EventListener("ROLE_UPDATE", func)

    @classmethod
    def raw_role_delete(cls, func: W2[int, int]):
        return EventListener("RAW_ROLE_DELETE", func)

    @classmethod
    def role_delete(cls, func: W[Role]):
        return EventListener("ROLE_DELETE", func)

    @classmethod
    def guild_member_add(cls, func: W[GuildMember]):
        return EventListener("GUILD_MEMBER_ADD", func)

    @classmethod
    def raw_guild_member_update(cls, func: W[GuildMember]):
        return EventListener("RAW_GUILD_MEMBER_UPDATE", func)

    @classmethod
    def guild_member_update(cls, func: W2[GuildMember, GuildMember]):
        return EventListener("GUILD_MEMBER_UPDATE", func)

    @classmethod
    def raw_guild_member_remove(cls, func: W2[int, int]):
        return EventListener("RAW_GUILD_MEMBER_REMOVE", func)

    @classmethod
    def guild_member_remove(cls, func: W2[BaseGuild, GuildMember | User]):
        return EventListener("GUILD_MEMBER_REMOVE", func)

    @classmethod
    def reaction_add(cls, func: W2[User | GuildMember | int, Reaction]):
        return EventListener("REACTION_ADD", func)

    @classmethod
    def reaction_remove(cls, func: W2[User | GuildMember | int, Reaction]):
        return EventListener("REACTION_REMOVE", func)

    @classmethod
    def audit_log_entry(cls, func: W[AuditLogEntry]):
        return EventListener("AUDIT_LOG_ENTRY", func)


event = EventBuilder()
