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

from typing import TYPE_CHECKING, Any

from .. import enums, flags
from ..utils import generate_repr, parse_timestamp, try_snowflake
from .api_mixins.message import MessageAPIMixin
from .channel import channel_builder
from .embed import Embed
from .object import Object
from .sticker import Sticker
from .user import User

if TYPE_CHECKING:
    from datetime import datetime as dt

    from .. import Channel, Thread
    from ..api import HTTPConnection
    from ..payloads import Message as MessagePayload

__all__ = (
    'Message',
    'AllowedMentions',
    'Attachment',
    'Reaction',
)


class Message(MessageAPIMixin):
    """
    A model representing a message from Discord.

    Attributes
    ----------
    id : int
        The ID of the message.
    channel_id : int
        The ID of the channel that the message was sent in.
    channel : novus.abc.Snowflake
        A snowflake channel object.
    author : novus.User
        The author of the message.
    content : str
        The content of the message.
    timestamp : datetime.datetime
        When the message was sent.
    edited_timestamp : datetime.datetime | None
    tts : bool
        Whether or not the message was sent with TTS.
    mention_everyone : bool
        Whehter the message mentions everyone.
    mentions : list[novus.User]
        A list of users who were mentioned in the message.
    mention_roles : list[int]
        A list of role IDs that were mentioned in the message.
    mention_channels : list[novus.Channel]
        A list of channels that mentioned in the message.
    attachments : list[novus.Attachment]
        A list of attachments on the message.
    embeds : list[novus.Embed]
        A list of embeds on the message.
    reactions : list[novus.Reaction]
        A list of reactions on the message.
    pinned : bool
        If the message is pinned.
    webhook_id : int | None
        If the message was sent by a webhook, this would be the webhook's ID.
    type : novus.MessageType
        The type of the message.
    activity : novus.MessageActivity | None
        The message activity attached to the object.
    application : novus.Application | None
        The application sent with RPC chat embeds.
    application_id : int | None
        If the message is an interaction, or application-owned webhook, this
        is the ID of the application.
    message_reference : novus.MessageReference | None
        Data showing the source of a crosspost, channel follow, pin, or reply.
    flags : novus.MessageFlags
        The message flags.
    referenced_message : novus.Message | None
        The message associated with the reference.
    interaction : novus.MessageInteraction | None
        Data referring to the interaction if the message is associated with one.
    thread : novus.Thread | None
        The thread that was started from this message.
    components : novus.MessageComponents | None
        The components associated with the message.
    sticker_items : list[novus.Sticker]
        The stickers sent with the message.
    position : int | None
        An integer representin the approximate position in the thread.
    role_subscription_data : novus.RoleSubscription | None
        Data of the role subscription purchase.
    """

    __slots__ = (
        '_state',
        'id',
        'channel_id',
        'channel',
        'author',
        'content',
        'timestamp',
        'edited_timestamp',
        'tts',
        'mention_everyone',
        'mentions',
        'mention_roles',
        'mention_channels',
        'attachments',
        'embeds',
        'reactions',
        'pinned',
        'webhook_id',
        'type',
        'activity',
        'application',
        'application_id',
        'message_reference',
        'flags',
        'referenced_message',
        'interaction',
        'thread',
        'components',
        'sticker_items',
        'stickers',
        'position',
        'role_subscription_data',
    )

    def __init__(self, *, state: HTTPConnection, data: MessagePayload) -> None:
        self._state = state
        self.id: int = try_snowflake(data["id"])
        self.channel_id: int = try_snowflake(data["channel_id"])
        self.channel: Object = Object(self.channel_id, state=self._state)
        self.author: User = User(state=self._state, data=data["author"])
        self.content: str = data.get("content", "")
        self.timestamp: dt = parse_timestamp(data.get("timestamp"))
        self.edited_timestamp: dt | None = parse_timestamp(data.get("edited_timestamp"))
        self.tts: bool = data.get("tts", False)
        self.mention_everyone: bool = data.get("mention_everyone", False)
        self.mentions: list[User] = [
            User(state=self._state, data=d)
            for d in data.get("mentions", [])
        ]
        self.mention_roles: list[int] = [
            try_snowflake(d)
            for d in data.get("mention_roles", [])
        ]
        self.mention_channels: list[Channel] = [
            channel_builder(state=self._state, data=d)  # pyright: ignore
            for d in data.get("mention_channels", [])
        ]
        self.attachments: list[Attachment] = [
            Attachment(data=d)
            for d in data["attachments"]
        ]
        self.embeds: list[Embed] = [
            Embed._from_data(d)
            for d in data.get("embeds", [])
        ]
        self.reactions: list[Reaction] = [
            Reaction(data=d)
            for d in data.get("reactions", [])
        ]
        self.pinned: bool = data.get("pinned")
        self.webhook_id: int | None = try_snowflake(data.get("webhook_id"))
        self.type: enums.MessageType = enums.MessageType(data["type"])
        # self.activity = data["activity"]
        # self.application = data["application"]
        self.application_id: int | None = try_snowflake(data.get("application_id"))
        self.flags: flags.MessageFlags = flags.MessageFlags(data.get("flags", 0))
        self.referenced_message: Message | None = None
        if "referenced_message" in data and data["referenced_message"]:
            self.referenced_message = Message(
                state=self._state,
                data=data["referenced_message"],
            )
        # self.interaction = data["interaction"]
        self.thread: Thread | None = None
        if "thread" in data:
            self.thread = channel_builder(
                state=self._state,
                data=data["thread"],
            )  # pyright: ignore
        # self.components = data["components"]
        self.sticker_items: list[Sticker] = [
            Sticker(state=self._state, data=d, guild=None)  # pyright: ignore
            for d in data.get("sticker_items", [])
        ]
        self.position: int | None = data.get("position")
        # self.role_subscription_data = data["role_subscription_data"]

    __repr__ = generate_repr(('id',))


class AllowedMentions:

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...


class Attachment:

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...


class Reaction:

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...
