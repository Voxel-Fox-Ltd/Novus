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

from collections import OrderedDict
from typing import TYPE_CHECKING, Any, Literal, overload

from ..models.channel import Channel
from ..models.guild import Guild
from ..models.message import Message
from ..models.object import Object

if TYPE_CHECKING:
    from .. import DMChannel, Emoji, GuildChannel, ScheduledEvent, Sticker, User
    from ._http import HTTPConnection

__all__ = (
    'APICache',
)


class MaxLenDict(OrderedDict):

    def __init__(self, *, max_size: int):
        self.max_size = max_size
        super().__init__()

    def __setitem__(self, __key: Any, __value: Any) -> None:
        super().__setitem__(__key, __value)
        while len(self) > self.max_size:
            self.popitem(last=False)


class APICache:

    def __init__(self, parent: HTTPConnection):
        self.parent = parent
        self.user: User | None = None
        self.application_id: int | None = None

        self.guilds: dict[int, Guild] = {}
        self.users: dict[int, User] = {}
        self.channels: dict[int, Channel] = {}
        self.emojis: dict[int, Emoji] = {}
        self.stickers: dict[int, Sticker] = {}
        self.events: dict[int, ScheduledEvent] = {}
        self.messages: dict[int, Message] = MaxLenDict(max_size=1_000)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} " + (
            f"user={self.user!r} "
            f"application_id={self.application_id!r} "
            f"guilds[{len(self.guilds)}] "
            f"users[{len(self.users)}] "
            f"channels[{len(self.channels)}] "
            f"emojis[{len(self.emojis)}] "
            f"stickers[{len(self.stickers)}] "
            f"events[{len(self.events)}]"
        ).strip() + ">"

    @staticmethod
    def do_nothing(instance: Any, *items: Any) -> None:
        pass

    def add_guilds(self, *items: Guild) -> None:
        for i in items:
            self.guilds[i.id] = i

    def add_users(self, *items: User) -> None:
        for i in items:
            self.users[i.id] = i

    def add_channels(self, *items: Channel) -> None:
        for i in items:
            self.channels[i.id] = i

    def add_emojis(self, *items: Emoji) -> None:
        for i in items:
            if i.id is None:
                continue
            self.emojis[i.id] = i

    def add_stickers(self, *items: Sticker) -> None:
        for i in items:
            self.stickers[i.id] = i

    def add_events(self, *items: ScheduledEvent) -> None:
        for i in items:
            self.events[i.id] = i

    def add_messages(self, *items: Message) -> None:
        for i in items:
            self.messages[i.id] = i

    @overload
    def get_guild(self, id: int | str, or_object: Literal[True] = ...) -> Guild:
        ...

    @overload
    def get_guild(self, id: int | str, or_object: Literal[False] = ...) -> Guild | None:
        ...

    def get_guild(self, id: int | str, or_object: bool = False) -> Guild | None:
        v = self.guilds.get(int(id))
        if v:
            return v
        if or_object is False:
            return None
        return Object.with_api((Guild,), id, state=self.parent)

    @overload
    def get_user(self, id: int | str, or_object: Literal[True] = ...) -> User:
        ...

    @overload
    def get_user(self, id: int | str, or_object: Literal[False] = ...) -> User | None:
        ...

    def get_user(self, id: int | str, or_object: bool = False) -> User | None:
        v = self.users.get(int(id))
        if v:
            return v
        if or_object is False:
            return None
        return Object.with_api((User,), id, state=self.parent)

    @overload
    def get_channel(self, id: int | str, or_object: Literal[True] = ...) -> GuildChannel | DMChannel:
        ...

    @overload
    def get_channel(self, id: int | str, or_object: Literal[False] = ...) -> GuildChannel | DMChannel | None:
        ...

    def get_channel(self, id: int | str, or_object: bool = False) -> GuildChannel | DMChannel | None:
        v = self.channels.get(int(id))
        if v:
            return v  # pyright: ignore
        if or_object is False:
            return None
        return Object.with_api((Channel,), id, state=self.parent)  # pyright: ignore

    def get_emoji(self, id: int | str) -> Emoji | None:
        return self.emojis.get(int(id))

    def get_sticker(self, id: int | str) -> Sticker | None:
        return self.stickers.get(int(id))

    def get_event(self, id: int | str) -> ScheduledEvent | None:
        return self.events.get(int(id))

    @overload
    def get_message(self, id: int | str, or_object: Literal[True] = ...) -> Message:
        ...

    @overload
    def get_message(self, id: int | str, or_object: Literal[False] = ...) -> Message | None:
        ...

    def get_message(self, id: int | str, or_object: bool = False) -> Message | None:
        v = self.messages.get(int(id))
        if v:
            return v
        if or_object is False:
            return None
        return Object.with_api((Message,), id, state=self.parent)

    def clear(self) -> None:
        self.user = None
        self.application_id = None
        self.guilds.clear()
        self.users.clear()
        self.channels.clear()
        self.messages.clear()
        self.emojis.clear()
        self.stickers.clear()
        self.events.clear()
