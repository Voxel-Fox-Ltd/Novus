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

from typing import TYPE_CHECKING, Any, Literal

from typing_extensions import Self, override

from .. import flags
from ..utils import (
    MISSING,
    DiscordDatetime,
    add_not_missing,
    generate_repr,
    parse_timestamp,
    try_id,
    try_snowflake,
)
from .abc import Hashable
from .channel import Channel
from .embed import Embed
from .emoji import PartialEmoji
from .file import File
from .guild import BaseGuild, Guild
from .guild_member import GuildMember
from .reaction import Reaction
from .role import Role
from .sticker import Sticker
from .ui.action_row import ActionRow
from .user import User

if TYPE_CHECKING:
    from .. import payloads
    from ..api import HTTPConnection
    from . import abc
    from .webhook import Webhook

    AMI = bool | list[int] | list[abc.Snowflake]  # AllowedMentions init

__all__ = (
    'Message',
    'MessageInteraction',
    'WebhookMessage',
    'AllowedMentions',
    'Attachment',
)


class MessageInteraction:
    """
    An interaction attached to a message.

    Attributes
    ----------
    id : int
        The ID of the interaction.
    type : int
        The type of the interaction.

        .. seealso:: `novus.InteractionType`
    name : str
        The name of the invoked application command.
    user : novus.GuildMember | novus.User
        The user who invoked the interaction.
    """

    def __init__(self, *, state: HTTPConnection, data: payloads.MessageInteraction, guild: Guild | None):
        self.id = try_snowflake(data["id"])
        self.type = data["type"]
        self.name = data["name"]
        cached_user = state.cache.get_user(data["user"]["id"])
        if cached_user is not None:
            user = cached_user._update(data["user"])
        else:
            user = User(state=state, data=data["user"])
        if "member" in data:
            cached_guild = guild
            if isinstance(cached_guild, Guild):
                cached_member = cached_guild.get_member(user.id)
                if cached_member:
                    user = cached_member._update(data["member"])
                else:
                    user = GuildMember(state=state, data=data["member"], user=user, guild_id=cached_guild.id)
            elif guild:
                user = GuildMember(state=state, data=data["member"], user=user, guild_id=guild.id)
        self.user = user


class Message(Hashable):
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
    type : int
        The type of the message.

        .. seealso:: `novus.MessageType`
    activity : novus.MessageActivity | None
        The message activity attached to the object.
    application : novus.Application | None
        The application sent with RPC chat embeds.
    application_id : int | None
        If the message is an interaction, or application-owned webhook, this
        is the ID of the application.
    message_reference : novus.MessageReference | None
        Data showing the source of a crosspost, channel follow, pin, or reply.
    interaction : novus.MessageInteraction | None
        Interaction data associated with the message.
    flags : novus.MessageFlags
        The message flags.
    referenced_message : novus.Message | None
        The message associated with the reference.
    interaction : novus.Interaction | None
        Data referring to the interaction if the message is associated with one.
    thread : novus.Channel | None
        The thread that was started from this message.
    components : list[novus.ActionRow]
        The components associated with the message.
    sticker_items : list[novus.Sticker]
        The stickers sent with the message.
    position : int | None
        An integer representin the approximate position in the thread.
    role_subscription_data : novus.RoleSubscription | None
        Data of the role subscription purchase.
    jump_url : str
        A URL to jump to the message.
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
        'interaction',
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
    channel: Channel
    author: User | GuildMember
    guild: BaseGuild | None
    content: str
    timestamp: DiscordDatetime
    edited_timestamp: DiscordDatetime | None
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
    type: int
    application_id: int | None
    interaction: MessageInteraction | None
    flags: flags.MessageFlags
    referenced_message: Message | None
    thread: Channel | None
    components: list[ActionRow]
    sticker_items: list[Sticker]
    position: int | None

    def __init__(
            self,
            *,
            state: HTTPConnection,
            data: payloads.Message) -> None:
        self.state = state
        self.id = try_snowflake(data["id"])
        channel = self.state.cache.get_channel(data["channel_id"])
        if channel is None:
            channel = Channel.partial(self.state, data["channel_id"])
        self.channel = channel
        self.guild = None
        if "guild_id" in data:
            self.guild = self.state.cache.get_guild(data["guild_id"])
            if self.guild is None:
                self.guild = BaseGuild(state=self.state, data={"id": data["guild_id"]})

        # Get author user
        author = self.state.cache.get_user(data["author"]["id"])
        if author is None:
            self.author = User(state=self.state, data=data["author"])
        else:
            self.author = author._update(data["author"])

        # Try upgrade author to member
        if "member" in data:
            assert "guild_id" in data
            try:
                member = self.guild.get_member(self.author.id)  # pyright: ignore
            except AttributeError:
                member = None
            if member is None:
                self.author = GuildMember(
                    state=self.state,
                    data=data["member"],
                    user=self.author,
                    guild_id=data["guild_id"],
                )
            else:
                self.author = member._update(data["member"])
        self._update(data)

    __repr__ = generate_repr(('id',))

    @property
    def jump_url(self) -> str:
        guild_id = self.guild.id if self.guild else "@me"
        return f"https://discord.com/channels/{guild_id}/{self.channel.id}/{self.id}"

    def _update(self, data: payloads.Message) -> Self:
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
                user_data["member"]["guild_id"] = self.guild.id  # type: ignore
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
                type=int(d["type"]),
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
            Reaction(state=self.state, data=d, message_id=self.id, channel_id=self.channel.id)
            for d in data.get("reactions", [])
        ]
        self.pinned = data.get("pinned")
        self.webhook_id = try_snowflake(data.get("webhook_id"))
        self.type = data.get("type", 0)
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
        self.interaction = None
        if "interaction" in data:
            self.interaction = MessageInteraction(state=self.state, data=data["interaction"], guild=self.guild)
        self.thread = None
        if "thread" in data:
            assert self.guild
            self.thread = Channel(state=self.state, data=data["thread"])
        self.components = [
            ActionRow._from_data(d)
            for d in data.get("components", [])
        ]
        self.sticker_items = [
            Sticker(state=self.state, data=d)
            for d in data.get("sticker_items", [])
        ]
        self.position = data.get("position")  # position of message in a thread
        # self.role_subscription_data = data["role_subscription_data"]
        return self

    # API methods

    @classmethod
    async def create(
            cls,
            state: HTTPConnection,
            channel: int | abc.Snowflake,
            content: str = MISSING,
            *,
            tts: bool = MISSING,
            embeds: list[Embed] = MISSING,
            allowed_mentions: AllowedMentions = MISSING,
            components: list[ActionRow] = MISSING,
            message_reference: Message = MISSING,
            stickers: list[Sticker] = MISSING,
            files: list[File] = MISSING,
            flags: flags.MessageFlags = MISSING) -> Message:
        """
        Send a message to the given channel.

        .. seealso:: :func:`novus.Channel.send`

        Parameters
        ----------
        state : novus.api.HTTPConnection
            The API connection.
        channel : int | novus.abc.Snowflake
            The channel to send the message to.
        content : str
            The content to be added to the message.
        tts : bool
            Whether the message should be sent with TTS.
        embeds : list[novus.Embed]
            A list of embeds to be added to the message.
        allowed_mentions : novus.AllowedMentions
            An object of users that you want to be pinged.
        components : list[novus.ActionRow]
            A list of components to add to the message.
        message_reference : novus.Message
            A message to reply to.
        stickers : list[novus.Sticker]
            A list of stickers to add to the message.
        files : list[novus.File]
            A list of files to be added to the message.
        flags : novus.MessageFlags
            Message send flags.

        Returns
        -------
        novus.Message
            The created message.
        """

        update: dict[str, Any] = {}
        add_not_missing(update, "content", content)
        add_not_missing(update, "tts", tts)
        add_not_missing(update, "embeds", embeds)
        add_not_missing(update, "allowed_mentions", allowed_mentions)
        add_not_missing(update, "components", components)
        add_not_missing(update, "message_reference", message_reference)
        add_not_missing(update, "stickers", stickers)
        add_not_missing(update, "files", files)
        add_not_missing(update, "flags", flags)
        return await state.channel.create_message(
            try_id(channel),
            **update,
        )

    @classmethod
    async def fetch(
            cls,
            state: HTTPConnection,
            channel: int | abc.Snowflake,
            message: int | abc.Snowflake) -> Message:
        """
        Get an existing message.

        .. seealso:: :func:`novus.Channel.fetch_message`

        Parameters
        ----------
        state : novus.api.HTTPConnection
            The API connection.
        channel : int | novus.abc.Snowflake
            The channel to send the message to.
        message : int | novus.abc.Snowflake
            The message you want to get.

        Returns
        -------
        novus.Message
            The created message.
        """

        return await state.channel.get_channel_message(
            try_id(channel),
            try_id(message),
        )

    async def delete(
            self: abc.StateSnowflakeWithChannel,
            *,
            reason: str | None = None) -> None:
        """
        Delete a message.

        Parameters
        ----------
        reason: str | None
            The reason to be added to the audit log.
        """

        return await self.state.channel.delete_message(
            self.channel.id,
            self.id,
            reason=reason,
        )

    async def crosspost(self: abc.StateSnowflakeWithChannel) -> Message:
        """
        Crosspost a message.
        """

        return await self.state.channel.crosspost_message(
            self.channel.id,
            self.id,
        )

    async def add_reaction(
            self: abc.StateSnowflakeWithChannel,
            emoji: str | PartialEmoji) -> None:
        """
        Add a reaction to a message.

        Parameters
        ----------
        emoji : str | novus.PartialEmoji
            The emoji to add to the message.
        """

        return await self.state.channel.create_reaction(
            self.channel.id,
            self.id,
            emoji,
        )

    async def remove_reaction(
            self: abc.StateSnowflakeWithChannel,
            emoji: str | PartialEmoji,
            user: int | abc.Snowflake) -> None:
        """
        Remove a reaction from a message.

        Parameters
        ----------
        emoji : str | novus.PartialEmoji
            The emoji to remove from the message.
        user : int | novus.abc.Snowflake
            The user whose reaction you want to remove.
        """

        # if user is ME:
        #     return await self.state.channel.delete_own_reaction(
        #         self.channel.id,
        #         self.id,
        #         emoji,
        #     )
        return await self.state.channel.delete_user_reaction(
            self.channel.id,
            self.id,
            emoji,
            try_id(user),
        )

    async def fetch_reactions(
            self: abc.StateSnowflakeWithChannel,
            emoji: str | PartialEmoji) -> list[User]:
        """
        Get a list of users who reacted to a message.

        Parameters
        ----------
        emoji : str | novus.PartialEmoji
            The emoji to check the reactors for.
        """

        return await self.state.channel.get_reactions(
            self.channel.id,
            self.id,
            emoji,
        )

    async def clear_reactions(
            self: abc.StateSnowflakeWithChannel,
            emoji: str | PartialEmoji | None = None) -> None:
        """
        Remove all of the reactions for a given message.

        Parameters
        ----------
        emoji : str | novus.PartialEmoji | None
            The specific emoji that you want to clear. If not given, all
            reactions will be cleared.
        """

        if emoji is not None:
            return await self.state.channel.delete_all_reactions_for_emoji(
                self.channel.id,
                self.id,
                emoji,
            )
        return await self.state.channel.delete_all_reactions(
            self.channel.id,
            self.id,
        )

    async def edit(
            self: abc.StateSnowflakeWithChannel,
            content: str | None = MISSING,
            *,
            tts: bool = MISSING,
            embeds: list[Embed] | None = MISSING,
            allowed_mentions: AllowedMentions = MISSING,
            components: list[ActionRow] | None = MISSING,
            message_reference: Message | None = MISSING,
            stickers: list[Sticker] | None = MISSING,
            files: list[File] | None = MISSING,
            attachments: list[Attachment] | None = MISSING,
            flags: flags.MessageFlags = MISSING) -> Message:
        """
        Edit an existing message.

        Parameters
        ----------
        content : str | None
            The content to be added to the message.
        tts : bool
            Whether the message should be sent with TTS.
        embeds : list[novus.Embed] | None
            A list of embeds to be added to the message.
        allowed_mentions : novus.AllowedMentions
            An object of users that you want to be pinged.
        components : list[novus.ActionRow] | None
            A list of components to add to the message.
        message_reference : novus.Message | None
            A message to reply to.
        stickers : list[novus.Sticker] | None
            A list of stickers to add to the message.
        files : list[novus.File] | None
            A list of files to be appended to the message.
        attachments : list[novus.Attachment] | None
            A list of attachments currently on the message to keep.
        flags : novus.MessageFlags
            Message send flags.

        Returns
        -------
        novus.Message
            The edited message.
        """

        update: dict[str, Any] = {}
        add_not_missing(update, "content", content)
        add_not_missing(update, "tts", tts)
        add_not_missing(update, "embeds", embeds)
        add_not_missing(update, "allowed_mentions", allowed_mentions)
        add_not_missing(update, "components", components)
        add_not_missing(update, "message_reference", message_reference)
        add_not_missing(update, "stickers", stickers)
        add_not_missing(update, "files", files)
        add_not_missing(update, "flags", flags)
        add_not_missing(update, "attachments", attachments)
        return await self.state.channel.edit_message(
            self.channel.id,
            self.id,
            **update,
        )

    async def pin(
            self: abc.StateSnowflakeWithChannel,
            *,
            reason: str | None = None) -> None:
        """
        Pin the message to the channel.

        Parameters
        ----------
        reason : str | None
            The reason shown in the audit log.
        """

        await self.state.channel.pin_message(
            self.channel.id,
            self.id,
            reason=reason,
        )

    async def unpin(
            self: abc.StateSnowflakeWithChannel,
            *,
            reason: str | None = None) -> None:
        """
        Unpin a message from the channel.

        Parameters
        ----------
        reason : str | None
            The reason shown in the audit log.
        """

        await self.state.channel.unpin_message(
            self.channel.id,
            self.id,
            reason=reason,
        )

    async def create_thread(
            self: abc.StateSnowflakeWithChannel,
            name: str,
            *,
            reason: str | None = None,
            auto_archive_duration: Literal[60, 1_440, 4_320, 10_080] = MISSING,
            rate_limit_per_user: int = MISSING) -> Channel:
        """
        Create a thread from the message.

        Parameters
        ----------
        name : str
            The name of the thread.
        auto_archive_duration : int
            The auto archive duration for the thread.
        rate_limit_per_user : int
            The number of seconds a user has to wait before sending another
            message.
        reason : str | None
            The reason shown in the audit log.
        """

        params: dict[str, str | int] = {}
        params["name"] = name
        add_not_missing(params, "auto_archive_duration", auto_archive_duration)
        add_not_missing(params, "rate_limit_per_user", rate_limit_per_user)
        return await self.state.channel.start_thread_from_message(
            self.channel.id,
            self.id,
            reason=reason,
            **params,  # pyright: ignore
        )


class WebhookMessage(Message):

    def __init__(
            self,
            *,
            webhook: Webhook,
            **kwargs: Any):
        super().__init__(**kwargs)
        self.webhook = webhook

    # API methods

    @override
    @classmethod
    async def fetch(  # type: ignore
            cls,
            state: HTTPConnection,
            webhook: int | abc.Snowflake,
            webhook_token: str,
            message: int | abc.Snowflake) -> WebhookMessage:
        """
        Get an existing message using the webhook.

        Parameters
        ----------
        state : novus.api.HTTPConnection
            The API connection.
        webhook : int | novus.abc.Snowflake
            The webhook that sent the message.
        webhook_token : str
            The token associated with the webhook.
        message : int | novus.abc.Snowflake
            The message you want to get.

        Returns
        -------
        novus.Message
            The created message.
        """

        return await state.webhook.get_webhook_message(
            try_id(webhook),
            webhook_token,
            try_id(message),
        )

    @override
    async def delete(  # type: ignore
            self: abc.StateSnowflakeWithWebhook) -> None:
        """
        Delete a webhook message.

        Parameters
        ----------
        webhook : int | novus.abc.Snowflake
            The webhook that sent the message.
        webhook_token : str
            The token associated with the webhook.
        message : int | novus.abc.Snowflake
            The message you want to delete.
        """

        return await self.state.webhook.delete_webhook_message(
            self.webhook.id,
            self.webhook.token,  # pyright: ignore
            self.id,
        )

    @override
    async def edit(
            self: abc.StateSnowflakeWithWebhook,
            content: str | None = MISSING,
            *,
            tts: bool = MISSING,
            embeds: list[Embed] | None = MISSING,
            allowed_mentions: AllowedMentions = MISSING,
            components: list[ActionRow] | None = MISSING,
            message_reference: Message | None = MISSING,
            stickers: list[Sticker] | None = MISSING,
            files: list[File] | None = MISSING,
            attachments: list[Attachment] | None = MISSING,
            flags: flags.MessageFlags = MISSING) -> Message:
        """
        Edit an existing message sent by the webhook.

        Parameters
        ----------
        content : str | None
            The content to be added to the message.
        tts : bool
            Whether the message should be sent with TTS.
        embeds : list[novus.Embed] | None
            A list of embeds to be added to the message.
        allowed_mentions : novus.AllowedMentions
            An object of users that you want to be pinged.
        components : list[novus.ActionRow] | None
            A list of components to add to the message.
        message_reference : novus.Message | None
            A message to reply to.
        stickers : list[novus.Sticker] | None
            A list of stickers to add to the message.
        files : list[novus.File] | None
            A list of files to be appended to the message.
        attachments : list[novus.Attachment] | None
            A list of attachments currently on the message to keep.
        flags : novus.MessageFlags
            Message send flags.

        Returns
        -------
        novus.Message
            The edited message.
        """

        update: dict[str, Any] = {}
        add_not_missing(update, "content", content)
        add_not_missing(update, "tts", tts)
        add_not_missing(update, "embeds", embeds)
        add_not_missing(update, "allowed_mentions", allowed_mentions)
        add_not_missing(update, "components", components)
        add_not_missing(update, "message_reference", message_reference)
        add_not_missing(update, "stickers", stickers)
        add_not_missing(update, "files", files)
        add_not_missing(update, "attachments", attachments)
        add_not_missing(update, "flags", flags)
        return await self.state.webhook.edit_webhook_message(
            self.webhook.id,
            self.webhook.token,  # pyright: ignore
            self.id,
            **update,
        )


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
            users: AMI = False,
            roles: AMI = False,
            everyone: bool = False) -> None:
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
    def all(cls) -> Self:
        """
        An allowed mentions object with all pings allowed.
        """

        return cls(users=True, roles=True, everyone=True)

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
        elif isinstance(target, Role):  # pyright: ignore[reportUnnecessaryIsInstance]
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
    """
    An attachment sent with a message.

    Attributes
    ----------
    id : int
        The ID of the attachment.
    filename : str
        The filename for the attachment.
    size : int
        The size of the attachment.
    url : str
        A URL to the attachment on the CDN.
    proxy_url : str
        A proxy URL to the attachment on the CDN.
    """

    def __init__(self, data: payloads.Attachment) -> None:
        self.id = try_snowflake(data["id"])
        self.filename = data["filename"]
        self.size = data["size"]
        self.url = data["url"]
        self.proxy_url = data["proxy_url"]

    def _to_data(self) -> dict[str, str]:
        return {
            "id": self.id,  # pyright: ignore
        }

    def __str__(self) -> str:
        return self.url
