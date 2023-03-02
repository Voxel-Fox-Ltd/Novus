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

from typing import TYPE_CHECKING, Any
from typing_extensions import Self

from .. import enums, flags
from ..utils import generate_repr, parse_timestamp, try_snowflake, try_id
from .api_mixins.message import MessageAPIMixin
from .channel import Channel, TextChannel, Thread
from .embed import Embed
from .guild import Guild
from .guild_member import GuildMember
from .reaction import Reaction
from .sticker import Sticker
from .ui.action_row import ActionRow
from .user import User
from .role import Role

if TYPE_CHECKING:
    from datetime import datetime as dt

    from ..api import HTTPConnection
    from .. import payloads
    from . import Webhook
    from . import api_mixins as amix, abc

    AMI = bool | list[int] | list[abc.Snowflake]  # AllowedMentions init

__all__ = (
    'Message',
    'WebhookMessage',
    'AllowedMentions',
    'Attachment',
)


class Message(MessageAPIMixin):
    """
    A model representing a message from Discord.

    Attributes
    ----------
    id : int
        The ID of the message.
    channel : novus.Channel
        A snowflake channel object.
    guild : novus.Guild | None
        The guild associated with the message.

        .. note::

            If the message is fetched via the API, the guild will set to ``None``.
    author : novus.User | novus.GuildMember
        The author of the message.
    content : str
        The content of the message.
    timestamp : datetime.datetime
        When the message was sent.
    edited_timestamp : datetime.datetime | None
        When the message was last edited.
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
    interaction : novus.Interaction | None
        Data referring to the interaction if the message is associated with one.
    thread : novus.Thread | None
        The thread that was started from this message.
    components : list[novus.ActionRow]
        The components associated with the message.
    sticker_items : list[novus.Sticker]
        The stickers sent with the message.
    position : int | None
        An integer representin the approximate position in the thread.
    role_subscription_data : novus.RoleSubscription | None
        Data of the role subscription purchase.
    """

    __slots__ = (
        'state',
        'id',
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
        'guild',
    )

    id: int
    channel: TextChannel
    author: User | GuildMember
    guild: Guild | amix.GuildAPIMixin | None
    content: str
    timestamp: dt
    edited_timestamp: dt | None
    tts: bool
    mention_everyone: bool
    mentions: list[User]
    mention_roles: list[int]
    mention_channels: list[Channel]
    attachments: list[Attachment]
    embeds: list[Embed]
    reactions: list[Reaction]
    pinned: bool
    webhook_id: int | None
    type: enums.MessageType
    application_id: int | None
    flags: flags.MessageFlags
    referenced_message: Message | None
    thread: Thread | None
    components: list[ActionRow]
    sticker_items: list[Sticker]
    position: int | None

    def __init__(self, *, state: HTTPConnection, data: payloads.Message) -> None:
        self.state = state
        self.id = try_snowflake(data["id"])
        self.channel = self.state.cache.get_channel(data["channel_id"], or_object=True)  # pyright: ignore
        self.guild = None
        if "guild_id" in data:
            self.guild = self.state.cache.get_guild(data["guild_id"], or_object=True)
        self.author = User(state=self.state, data=data["author"])
        if "member" in data:
            assert self.guild
            self.author = GuildMember(
                state=self.state,
                data=data["member"],
                user=self.author,
                guild_id=self.guild.id,
            )
        self.content = data.get("content", "")
        self.timestamp = parse_timestamp(data.get("timestamp"))
        self.edited_timestamp = parse_timestamp(data.get("edited_timestamp"))
        self.tts = data.get("tts", False)
        self.mention_everyone = data.get("mention_everyone", False)
        mention_data = data.get("mentions", [])
        self.mentions = []
        for user_data in mention_data:
            user_object = User(state=self.state, data=user_data)
            if "member" in user_data:
                user_data["member"]["guild_id"] = self.guild.id  # pyright: ignore
                user_object._upgrade(user_data["member"])  # pyright: ignore
            self.mentions.append(user_object)
        self.mention_roles = [
            try_snowflake(d)
            for d in data.get("mention_roles", [])
        ]
        self.mention_channels = [
            Channel.partial(
                state=self.state,
                id=d["id"],
                type=enums.ChannelType(d["type"]),
            )
            for d in data.get("mention_channels", [])
        ]
        self.attachments = [
            Attachment(data=d)
            for d in data.get("attachments", [])
        ]
        self.embeds = [
            Embed._from_data(d)
            for d in data.get("embeds", [])
        ]
        self.reactions = [
            Reaction(state=self.state, data=d)
            for d in data.get("reactions", [])
        ]
        self.pinned = data.get("pinned")
        self.webhook_id = try_snowflake(data.get("webhook_id"))
        self.type = enums.MessageType(data.get("type", 0))
        # self.activity = data["activity"]
        # self.application = data["application"]
        self.application_id = try_snowflake(data.get("application_id"))
        self.flags = flags.MessageFlags(data.get("flags", 0))
        self.referenced_message = None
        if "referenced_message" in data and data["referenced_message"]:
            self.referenced_message = Message(
                state=self.state,
                data=data["referenced_message"],
            )
        # self.interaction = data["interaction"]
        self.thread = None
        if "thread" in data:
            assert self.guild
            self.thread = Thread(state=self.state, data=data["thread"])
        self.components = [
            ActionRow._from_data(d)
            for d in data.get("components", [])
        ]
        self.sticker_items = [
            Sticker(state=self.state, data=d)
            for d in data.get("sticker_items", [])
        ]
        self.position = data.get("position")
        # self.role_subscription_data = data["role_subscription_data"]

    __repr__ = generate_repr(('id',))


class WebhookMessage(Message):

    def __init__(
            self,
            *,
            webhook: Webhook,
            **kwargs: Any):
        super().__init__(**kwargs)
        self.webhook = webhook


class AllowedMentions:
    """
    Allowed mentions for a particular message. Have more fine-grained control
    over what and who you mention.

    Parameters
    ----------
    users : bool | list[int] | list[novus.abc.Snowflake]
        A list of users (or IDs) that you want to mention.
    roles : bool | list[int] | list[novus.abc.Snowflake]
        A list of roles (or IDs) that you want to mention.
    everyone : bool
        Whether or not you want @everyone and @here pings to be parsed.
    """

    def __init__(
            self,
            *,
            users: AMI = True,
            roles: AMI = True,
            everyone: bool = True) -> None:
        self.users: list[int] | bool
        if isinstance(users, bool):
            self.users = users
        else:
            self.users = [try_id(i) for i in users]
        self.roles: list[int] | bool
        if isinstance(roles, bool):
            self.roles = roles
        else:
            self.roles = [try_id(i) for i in roles]
        self.everyone: bool = everyone

    @classmethod
    def none(cls) -> Self:
        """
        An allowed mentions object with no pings allowed.
        """

        return cls(users=False, roles=False, everyone=False)

    @classmethod
    def only(cls, target: Role | User | GuildMember) -> Self:
        """
        Users or roles that you want to be the only parsed mention in a given
        message.

        Parameters
        ----------
        target : novus.Role | novus.User | novus.GuildMember
            The
        """

        if isinstance(target, (User, GuildMember,)):
            return cls(users=[target])
        elif isinstance(target, Role):
            return cls(roles=[target])
        else:
            raise TypeError("Only role and user types are permitted.")

    def _to_data(self) -> payloads.AllowedMentions:
        v: payloads.AllowedMentions = {"parse": []}
        if self.users:
            if isinstance(self.users, list):
                v["users"] = [str(i) for i in self.users]
            else:
                v["parse"].append("users")
        if self.roles:
            if isinstance(self.roles, list):
                v["roles"] = [str(i) for i in self.roles]
            else:
                v["parse"].append("roles")
        if self.everyone:
            v["parse"].append("everyone")
        return v


class Attachment:

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...
