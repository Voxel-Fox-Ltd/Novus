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

    @classmethod
    def filtered_component(cls, match_string: str) -> WEL[Interaction]:
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

    # "Application command permissions update": None

    # "Auto moderation rule create": None

    # "Auto moderation rule update": None

    # "Auto moderation rule delete": None

    # "Auto moderation action execution": None

    @classmethod
    def channel_create(cls, func: W[Channel]) -> EL:
        return EventListener("CHANNEL_CREATE", func)

    @classmethod
    def channel_update(cls, func: W2[Channel, Channel]) -> EL:
        return EventListener("CHANNEL_UPDATE", func)

    @classmethod
    def channel_delete(cls, func: W[Channel]) -> EL:
        return EventListener("CHANNEL_DELETE", func)

    @classmethod
    def thread_create(cls, func: W[Thread]) -> EL:
        return EventListener("THREAD_CREATE", func)

    @classmethod
    def thread_update(cls, func: W[Thread]) -> EL:
        return EventListener("THREAD_UPDATE", func)

    # "Thread delete": None

    # "Thread list sync": None

    # "Thread member update": None

    # "THREAD_MEMBERS_UPDATE": self._handle_thread_member_list_update

    @classmethod
    def guild_create(cls, func: W[Guild]) -> EL:
        return EventListener("GUILD_CREATE", func)

    @classmethod
    def guild_update(cls, func: W2[Guild, Guild]) -> EL:
        return EventListener("GUILD_UPDATE", func)

    @classmethod
    def guild_delete(cls, func: W[Guild]) -> EL:
        return EventListener("GUILD_DELETE", func)

    @classmethod
    def audit_log_create(cls, func: W[AuditLog]) -> EL:
        return EventListener("GUILD_AUDIT_LOG_ENTRY_CREATE", func)

    @classmethod
    def user_ban(cls, func: W2[Guild, User | GuildMember]) -> EL:
        return EventListener("GUILD_BAN_ADD", func)

    @classmethod
    def user_unban(cls, func: W2[Guild, User]) -> EL:
        return EventListener("GUILD_BAN_REMOVE", func)

    @classmethod
    def emojis_update(cls, func: W2[Guild, list[Emoji]]) -> EL:
        return EventListener("GUILD_EMOJIS_UPDATE", func)

    @classmethod
    def stickers_update(cls, func: W2[Guild, list[Sticker]]) -> EL:
        return EventListener("GUILD_STICKERS_UPDATE", func)

    @classmethod
    def guild_member_add(cls, func: W[GuildMember]) -> EL:
        return EventListener("GUILD_MEMBER_ADD", func)

    @classmethod
    def guild_member_remove(cls, func: W2[Guild, User | GuildMember]) -> EL:
        return EventListener("GUILD_MEMBER_REMOVE", func)

    @classmethod
    def guild_member_update(cls, func: W2[GuildMember, GuildMember]) -> EL:
        return EventListener("GUILD_MEMBER_UPDATE", func)

    @classmethod
    def role_create(cls, func: W[Role]) -> EL:
        return EventListener("GUILD_ROLE_CREATE", func)

    @classmethod
    def role_update(cls, func: W[Role, Role]) -> EL:
        return EventListener("GUILD_ROLE_UPDATE", func)

    @classmethod
    def role_delete(cls, func: W[Role]) -> EL:
        return EventListener("GUILD_ROLE_DELETE", func)

    # "Guild scheduled event create": None

    # "Guild scheduled event update": None

    # "Guild scheduled event delete": None

    # "Guild scheduled event user add": None

    # "Guild scheduled event user remove": None

    # "INTERACTION_CREATE": self._handle_interaction

    # "INVITE_CREATE": self._handle_invite_create

    # "INVITE_DELETE": self._handle_invite_delete

    @classmethod
    def message(cls, func: W[Message]) -> EL:
        return EventListener("MESSAGE_CREATE", func)

    @classmethod
    def message_update(cls, func: W2[Message | None, Message]) -> EL:
        return EventListener("MESSAGE_UPDATE", func)

    @classmethod
    def message_delete(cls, func: W2[TextChannel, Message]) -> EL:
        return EventListener("MESSAGE_DELETE", func)

    # "Message delete bulk": None

    # "MESSAGE_REACTION_ADD": self._handle_message_reaction_add

    # "MESSAGE_REACTION_REMOVE": self._handle_message_reaction_remove

    # "MESSAGE_REACTION_REMOVE_ALL": self._handle_message_reaction_remove_all

    # "MESSAGE_REACTION_REMOVE_EMOJI": self._handle_message_reaction_remove_all_emoji

    # "PRESENCE_UPDATE": self._handle_presence_update

    # "Stage instance create": None

    # "Stage instance update": None

    # "Stage instance delete": None

    # "TYPING_START": self._handle_typing

    # "User update": None

    # "VOICE_STATE_UPDATE": self._handle_voice_state

    # "Voice server update": None

    # "Webhooks update": None

    @staticmethod
    def __call__(
            event_name: str,
            predicate: Callable[..., bool] | None = None) -> WEL:
        def wrapper(func: Callable[..., AA]) -> EL:
            return EventListener(event_name, func, predicate)
        return wrapper  # pyright: ignore


event = EventBuilder()
