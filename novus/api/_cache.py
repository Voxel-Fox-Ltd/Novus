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
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .. import Channel, Emoji, Guild, Message, ScheduledEvent, Sticker, User
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

    __slots__ = (
        'parent',
        'user',
        'application_id',
        'guilds',
        'users',
        'channels',
        'emojis',
        'stickers',
        'events',
        'messages',
    )

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

    def clear(self) -> None:
        self.user = None
        self.application_id = None
        self.guilds.clear()
        self.users.clear()
        self.channels.clear()
        self.emojis.clear()
        self.stickers.clear()
        self.events.clear()
