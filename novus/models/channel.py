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

import asyncio
import logging
from typing import TYPE_CHECKING, Any, Literal, Type, overload

from ..enums import ChannelType, PermissionOverwriteType
from ..flags import Permissions
from ..utils import (
    MISSING,
    add_not_missing,
    generate_repr,
    parse_timestamp,
    try_id,
    try_snowflake,
)
from .abc import Hashable, Messageable
from .user import User

if TYPE_CHECKING:
    from datetime import datetime as dt

    from .. import payloads
    from ..api import HTTPConnection
    from ..enums import ForumLayout, ForumSortOrder
    from ..flags import ChannelFlags, MessageFlags
    from . import abc
    from .embed import Embed
    from .emoji import PartialEmoji
    from .file import File
    from .guild import BaseGuild
    from .guild_member import GuildMember, ThreadMember
    from .invite import Invite
    from .message import AllowedMentions, Message
    from .role import Role
    from .ui.action_row import ActionRow
    from ..utils.types import AnySnowflake

__all__ = (
    'PermissionOverwrite',
    'Channel',
    'GuildChannel',
    'GuildTextChannel',
    'DMChannel',
    'GroupDMChannel',
    'Thread',
    'TextChannel',
    'VoiceChannel',
    'ForumTag',
    'GuildVoiceChannel',
    'GuildStageChannel',
    'GuildCategory',
    'GuildAnnouncementChannel',
    'GuildForumChannel',
)


log = logging.getLogger("novus.channel")


def channel_factory(
        channel_type: int) -> Type[Channel]:
    """
    Return the correct channel object given the channel type.
    """

    match channel_type:
        case ChannelType.guild_text.value:
            return GuildTextChannel
        case ChannelType.dm.value:
            return DMChannel
        case ChannelType.guild_voice.value:
            return GuildVoiceChannel
        case ChannelType.group_dm.value:
            return GroupDMChannel
        case ChannelType.guild_category.value:
            return GuildCategory
        case ChannelType.guild_announcement.value:
            return GuildAnnouncementChannel
        case ChannelType.announcement_thread.value:
            return GuildAnnouncementChannel
        case ChannelType.public_thread.value:
            return Thread
        case ChannelType.private_thread.value:
            return Thread
        case ChannelType.guild_stage_voice.value:
            return GuildStageChannel
        # case ChannelType.guild_directory.value:
        #     return Channel  # bots should never receive these
        case ChannelType.guild_forum.value:
            return GuildForumChannel
        case _:
            log.warning(
                "Unknown channel type %s"
                % channel_type
            )
            return TextChannel


def channel_builder(
        *,
        state: HTTPConnection,
        data: payloads.Channel,
        guild_id: int | None = None) -> Channel:
    """
    Create a channel object given its data.
    """

    factory = channel_factory(data['type'])
    if guild_id:
        return factory(state=state, data=data, guild_id=guild_id)  # type: ignore
    return factory(state=state, data=data)


class PermissionOverwrite:
    """
    A class representing a permission overwrite for a guild channel.

    Parameters
    ----------
    id : int
        The ID of the target.
    type : novus.PermissionOverwriteType
        The type of the target.
    allow : novus.Permissions
        The permissions that the target is explicitly allowed.
    deny : novus.Permissions
        The permissions that the target is explicitly denied.

    Attributes
    ----------
    id : int
        The ID of the target.
    type : novus.PermissionOverwriteType
        The type of the target.
    allow : novus.Permissions
        The permissions that the target is explicitly allowed.
    deny : novus.Permissions
        The permissions that the target is explicitly denied.
    """

    __slots__ = (
        'id',
        'type',
        'allow',
        'deny',
    )

    def __init__(
            self,
            id: AnySnowflake,
            type: PermissionOverwriteType,
            *,
            allow: Permissions = Permissions(),
            deny: Permissions = Permissions()):
        self.id = try_id(id)
        self.type = type
        self.allow = allow
        self.deny = deny

    __repr__ = generate_repr(('id', 'type', 'allow', 'deny',))

    def _to_data(self) -> payloads.ChannelOverwrite:
        return {
            "id": str(self.id),
            "type": self.type.value,
            "allow": str(self.allow.value),
            "deny": str(self.deny.value),
        }


class Channel(Hashable):
    """
    The base channel object that all other channels inherit from. This is also
    the object that will be returned if there is an unknown channel type.

    Attributes
    ----------
    id : int
        The ID of the channel.
    type : novus.ChannelType
        The type of the channel.
    guild : novus.abc.Snowflake | None
        The guild that the channel is attached to.
    raw : dict
        The raw data used to construct the channel object.
    """

    id: int
    type: ChannelType
    raw: payloads.Channel
    guild: BaseGuild | None

    def __init__(self, *, state: HTTPConnection, data: payloads.Channel):
        self.state = state
        self.id = try_snowflake(data['id'])
        self.type = ChannelType(data.get('type', 0))
        self.raw = data
        if "guild" in self.__slots__:
            self.guild = None

    __repr__ = generate_repr(('id',))

    @property
    def mention(self) -> str:
        return f"<#{self.id}>"

    @classmethod
    def partial(
            cls,
            state: HTTPConnection,
            id: int | str,
            type: ChannelType = ChannelType.guild_text) -> TextChannel:
        """
        Create a partial channel object that you can use to run API methods on.

        Parameters
        ----------
        state : novus.api.HTTPConnection
            The API connection.
        id : int
            The ID of the channel.

        Returns
        -------
        novus.TextChannel
            A created channel object.
        """

        return TextChannel(
            state=state,
            data={"id": id, "type": type.value}  # pyright: ignore
        )

    # API methods

    @classmethod
    async def fetch(
            cls,
            state: HTTPConnection,
            id: int | abc.Snowflake) -> Channel:
        """
        Fetch a channel from the API.

        Parameters
        ----------
        state : novus.api.HTTPConnection
            The API connection.
        id : int | novus.abc.Snowflake
            The ID of the channel you want to fetch.

        Returns
        -------
        novus.Channel
            The channel instance.
        """

        return await state.channel.get_channel(try_id(id))


class Typing:

    def __init__(self, state: HTTPConnection, channel: int | abc.Snowflake):
        self.state = state
        self.channel = channel
        self.typing_loop: asyncio.Task | None = None

    async def send_typing_loop(self) -> None:
        """
        Loop forever in a "send typing then wait 10 seconds" hellscape.
        """

        channel_id = try_id(self.channel)
        while True:
            await self.state.channel.trigger_typing_indicator(channel_id)
            await asyncio.sleep(8)

    async def __aenter__(self) -> None:
        self.typing_loop = asyncio.create_task(self.send_typing_loop())

    async def __aexit__(self, *_args: Any) -> None:
        if self.typing_loop is not None:
            self.typing_loop.cancel()


class TextChannel(Channel, Messageable):
    """
    An abstract channel class.

    Represents any channel that implements a ``send`` method.
    """

    state: HTTPConnection
    id: int
    type: ChannelType

    # API methods

    async def fetch_messages(
            self,
            *,
            limit: int = 100,
            around: int | abc.Snowflake | Message = MISSING,
            before: int | abc.Snowflake | Message = MISSING,
            after: int | abc.Snowflake | Message = MISSING) -> list[Message]:
        """
        Get a number of messages from the channel.

        Parameters
        ----------
        limit : int
            The number of messages that you want to get. Maximum 100.
        around : int | novus.abc.Snowflake
            Get messages around this ID.
            Only one of ``around``, ``before``, and ``after`` can be set.
        before : int | novus.abc.Snowflake
            Get messages before this ID.
            Only one of ``around``, ``before``, and ``after`` can be set.
        after : int | novus.abc.Snowflake
            Get messages after this ID.
            Only one of ``around``, ``before``, and ``after`` can be set.

        Returns
        -------
        list[novus.Message]
            The messages that were retrieved.
        """

        params: dict[str, int] = {}
        add_not_missing(params, "limit", limit)
        add_not_missing(params, "around", around, try_id)
        add_not_missing(params, "before", before, try_id)
        add_not_missing(params, "after", after, try_id)
        return await self.state.channel.get_channel_messages(
            self.id,
            **params,
        )

    async def fetch_message(self, id: int | abc.Snowflake) -> Message:
        """
        Get a single message from the channel.

        .. seealso:: :func:`novus.Message.fetch`

        Parameters
        ----------
        id : int | novus.abc.Snowflake
            The message that you want to get.

        Returns
        -------
        novus.Message
            The retrieved message.
        """

        return await self.state.channel.get_channel_message(
            self.id,
            try_id(id),
        )

    async def trigger_typing(self: abc.StateSnowflake) -> None:
        """
        Send a typing indicator to the channel.
        """

        await self.state.channel.trigger_typing_indicator(self.id)

    def typing(self) -> Typing:
        """
        A typing context manager.

        .. examples::

            async with channel.typing():
                ...
        """

        return Typing(self.state, self)

    async def fetch_pinned_messages(self: abc.StateSnowflake) -> list[Message]:
        """
        Get a list of pinned messages in the channel.
        """

        return await self.state.channel.get_pinned_messages(self.id)


class VoiceChannel(Channel):
    """
    An abstract channel class.

    Represents any channel that has voice capability.
    """

    state: HTTPConnection
    id: int
    type: ChannelType


class DMChannel(TextChannel):
    """
    A channel associated with a user's DMs.
    """

    __slots__ = (
        'state',
        'id',
        'type',
        'raw',
    )

    state: HTTPConnection
    id: int
    type: ChannelType


class GroupDMChannel(TextChannel):
    """
    A channel associated with a group DM.
    """

    __slots__ = (
        'state',
        'id',
        'type',
        'raw',
    )

    state: HTTPConnection
    id: int
    type: ChannelType


class GuildChannel(Channel):
    """
    An abstract channel class.

    Any channel inside of a guild.
    """

    id: int
    guild: BaseGuild
    position: int
    overwrites: list[PermissionOverwrite]
    name: str
    topic: str | None
    nsfw: bool
    last_message_id: int | None
    parent: Channel | None
    rate_limit_per_user: int | None

    def __init__(
            self,
            *,
            state: HTTPConnection,
            data: payloads.Channel,
            guild_id: int | None = None):
        super().__init__(state=state, data=data)
        del self.raw  # Not needed for known types
        guild_id = try_snowflake(data.get('guild_id')) or guild_id
        if guild_id is None:
            raise ValueError("Missing guild ID from guild channel %s" % data)
        self.guild = self.state.cache.get_guild(guild_id)
        self.position = data.get('position', 0)
        self.overwrites = [
            PermissionOverwrite(
                id=int(d['id']),
                type=PermissionOverwriteType(d['type']),
                allow=Permissions(int(d['allow'])),
                deny=Permissions(int(d['deny'])),
            )
            for d in data.get('permission_overwrites', list())
        ]
        if "name" not in data:
            raise TypeError(
                "Missing channel name from channel payload %s"
                % data
            )
        self.name = data['name']
        self.topic = data.get('topic', None)
        self.nsfw = data.get('nsfw', False)
        self.last_message_id = try_snowflake(data.get('last_message_id'))
        parent_id = try_snowflake(data.get('parent_id'))
        self.parent = None
        if parent_id:
            self.parent = self.state.cache.get_channel(parent_id)
        self.rate_limit_per_user = data.get('rate_limit_per_user')

    __repr__ = generate_repr(('id', 'guild', 'name',))

    def __str__(self) -> str:
        return f"#{self.name}"

    # API methods

    async def edit(
            self: abc.StateSnowflake,
            *,
            reason: str | None = None,
            name: str = MISSING,
            position: int = MISSING,
            topic: str = MISSING,
            nsfw: bool = MISSING,
            rate_limit_per_user: int = MISSING,
            bitrate: int = MISSING,
            user_limit: int = MISSING,
            default_auto_archive_duration: Literal[60, 1_440, 4_320, 10_080] = MISSING,
            default_thread_rate_limit_per_user: int = MISSING,
            archived: bool = MISSING,
            auto_archive_duration: Literal[60, 1_440, 4_320, 10_080] = MISSING,
            locked: bool = MISSING,
            invitable: bool = MISSING,
            flags: ChannelFlags = MISSING,
            default_sort_order: ForumSortOrder = MISSING,
            default_forum_layout: ForumLayout = MISSING,
            parent: abc.Snowflake | Channel = MISSING,
            type: ChannelType = MISSING,
            overwrites: list[PermissionOverwrite] = MISSING,
            available_tags: list[ForumTag] = MISSING,
            default_reaction_emoji: str | PartialEmoji = MISSING,
            applied_tags: list[int | ForumTag] = MISSING) -> Channel:
        """
        Edit the instance of the channel.

        Parameters
        ----------
        name : str
            The name of the channel.
        position : int
            The position of the channel.
        topic : str
            The topic for the channel.
            Only applies to text channels.
        nsfw : bool
            Whether or not the channel should be marked as NSFW.
        rate_limit_per_user : int
            The rate limit (in seconds) for the channel.
        bitrate : int
            The bitrate for the channel.
            Only applies to voice channels.
        user_limit : int
            The user limit for the channel.
            Only applies to voice channels.
        default_auto_archive_duration : int
            The default auto archive duration for the channel.
            Only applies to forum channels.

            .. note::

                Only accepts the values 60, 1_440, 4_320, and 10_080.
        default_thread_rate_limit_per_user : int
            The rate limit (in seconds) for the channel.
        archived : bool
            If the channel is archived.
            Only applies to threads.
        auto_archive_duration : int
            The default auto archive duration for the channel.
            Only applies to forum channels.

            .. note::

                Only accepts the values 60, 1_440, 4_320, and 10_080.
        locked : bool
            If the channel is locked.
            Only applies to threads.
        invitable : bool
            If non-moderators can add other non-moderators to a thread.
            Only applies to private thread channels.
        flags : novus.ChannelFlags
            The flags applied to the channel.
            Only applies to forum channels and threads within forum channels.
        default_sort_order : novus.ForumSortOrder
            The sort order of the forum.
            Only applies to forum channels.
        default_forum_layout : novus.ForumLayout
            The layout of the forum.
            Only applies to forum channels.
        parent : novus.abc.Snowflake
            A parent channel.
        type : novus.ChannelType
            The channel type.
        overwrites : list[novus.PermissionOverwrite]
            A list of permission overwrites for the channel.
        available_tags : list[novus.ForumTag]
            A list of tags available.
            Only applies to forum channels.
        default_reaction_emoji : str | novus.PartialEmoji
            The default reaction for each thread.
            Only applies to forum channels.
        applied_tags : list[novus.ForumTag]
            A list of tags applied to the channel.
            Only applies to threads within forums.
        reason : str | None
            The reason added to the entry, if one was given.
        """

        params: dict[str, Any] = {}
        add_not_missing(params, "name", name)
        add_not_missing(params, "position", position)
        add_not_missing(params, "topic", topic)
        add_not_missing(params, "nsfw", nsfw)
        add_not_missing(params, "rate_limit_per_user", rate_limit_per_user)
        add_not_missing(params, "bitrate", bitrate)
        add_not_missing(params, "user_limit", user_limit)
        add_not_missing(params, "default_auto_archive_duration", default_auto_archive_duration)
        add_not_missing(params, "default_thread_rate_limit_per_user", default_thread_rate_limit_per_user)
        add_not_missing(params, "archived", archived)
        add_not_missing(params, "auto_archive_duration", auto_archive_duration)
        add_not_missing(params, "locked", locked)
        add_not_missing(params, "invitable", invitable)
        add_not_missing(params, "flags", flags)
        add_not_missing(params, "default_sort_order", default_sort_order)
        add_not_missing(params, "default_forum_layout", default_forum_layout)
        add_not_missing(params, "parent", parent)
        add_not_missing(params, "type", type)
        add_not_missing(params, "overwrites", overwrites)
        add_not_missing(params, "available_tags", available_tags)
        add_not_missing(params, "default_reaction_emoji", default_reaction_emoji)
        add_not_missing(params, "applied_tags", applied_tags)
        return await self.state.channel.modify_channel(
            self.id,
            reason=reason,
            **params,
        )

    async def delete(
            self: abc.StateSnowflake,
            *,
            reason: str | None = None) -> None:
        """
        Delete the channel instance.

        Parameters
        ----------
        reason : str | None
            The reason shown in the audit log, if the channel is a guild
            channel.
        """

        await self.state.channel.delete_channel(self.id, reason=reason)

    async def fetch_invites(self: abc.StateSnowflake) -> list[Invite]:
        """
        Get a list of invites to the channel.

        Returns
        -------
        list[novus.Invite]
            A list of invites for the channel.
        """

        return await self.state.channel.get_channel_invites(self.id)

    async def create_invite(
            self: abc.StateSnowflake,
            *,
            reason: str | None = None,
            max_age: int = 86_400,
            max_uses: int = 0,
            temporary: bool = False,
            unique: bool = False) -> Invite:
        """
        Delete multiple messages at once.

        Parameters
        ----------
        max_age : int
            The duration of the invite (in seconds) before expiry, or ``0`` for
            never.
            Cannot be larger than ``604_800``.
        max_uses : int
            A maximum number of uses for the invite, or ``0`` for unlimited.
            Cannot be larger than ``100``.
        temporary : bool
            Whether the invite only grants temporary membership to the guild.
        unique : bool
            If you want to reuse a similar invite.
        reason : str | None
            The reason shown in the audit log.

        Returns
        -------
        novus.Invite
            The created invite.
        """

        return await self.state.channel.create_channel_invite(
            self.id,
            reason=reason,
            **{
                "max_age": max_age,
                "max_uses": max_uses,
                "temporary": temporary,
                "unique": unique,
            }
        )

    async def remove_overwrite(
            self: abc.StateSnowflake,
            target: int | abc.Snowflake | Role | User | GuildMember,
            *,
            reason: str | None = None) -> None:
        """
        Remove a specific overwrite in the channel.

        Parameters
        ----------
        target : int | novus.abc.Snowflake | novus.Role | novus.User | novus.GuildMember
            The overwrite that you want to remove.
        reason : str | None
            The reason shown in the audit log.
        """

        await self.state.channel.delete_channel_permission(
            self.id,
            try_id(target),
            reason=reason,
        )

    async def create_overwrite(
            self: abc.StateSnowflake,
            target: int | abc.Snowflake | Role | User | GuildMember,
            *,
            reason: str | None = None,
            allow: Permissions = MISSING,
            deny: Permissions = MISSING,
            overwrite_type: Type[Role] | Type[User] | Type[GuildMember] = MISSING) -> None:
        """
        Create a permission overwrite for a given channel.

        Parameters
        ----------
        target : int | novus.abc.Snowflake | novus.Role | novus.User | novus.GuildMember
            The overwrite that you want to add.
        allow : flags.Permissions
            The permissions you want to explicitly grant to the target.
        deny : flags.Permissions
            The permissions you wan tto explicitly deny from the target.
        reason : str | None
            The reason shown in the audit log.
        """

        params: dict[str, Any] = {}
        add_not_missing(params, "allow", allow)
        add_not_missing(params, "deny", deny)
        target = try_id(target)
        if overwrite_type is MISSING:
            overwrite_type = type(target)  # pyright: ignore

        await self.state.channel.edit_channel_permissions(
            self.id,
            target,
            reason=reason,
            **params,
            type=overwrite_type,
        )


class GuildTextChannel(GuildChannel, TextChannel):
    """
    A text channel inside of a guild.

    Attributes
    ----------
    id : int
        The ID of the channel.
    type : novus.ChannelType
        The type of the channel.
    guild : novus.BaseGuild | None
        The ID of the guild associated with the channel. May be ``None`` for
        some channel objects received over gateway guild dispatches.
    position: int
        The sorting position of the channel (relative to its parent container).
    overwrites: list[novus.PermissionOverwrite]
        The permission overwrites assoicated with this channel.
    name : str
        The name of the channel.
    topic : str | None
        The topic set in the channel.
    nsfw : bool
        Whether or not the channel is marked as NSFW.
    last_message_id : int | None
        The ID of the last message sent in the channel. May or may not point to
        an existing or valid message or thread.
    parent : novus.Channel | None
        The parent container channel.
    rate_limit_per_user: int | None
        The amount of seconds a user has to wait before sending another
        message.
    """

    __slots__ = (
        'state',
        'id',
        'type',
        'guild',
        'position',
        'overwrites',
        'name',
        'topic',
        'nsfw',
        'last_message_id',
        'parent',
        'rate_limit_per_user',
    )

    # API methods

    async def bulk_delete_messages(
            self: abc.StateSnowflake,
            messages: list[int | abc.Snowflake],
            *,
            reason: str | None = None) -> None:
        """
        Delete multiple messages at once.

        Parameters
        ----------
        messages : list[int | novus.abc.Snowflake]
            A list of the messages that you want to delete.
        reason : str | None
            The reason shown in the audit log.
        """

        await self.state.channel.bulk_delete_messages(
            self.id,
            reason=reason,
            message_ids=[try_id(i) for i in messages],
        )

    async def create_thread(
            self: abc.StateSnowflake,
            name: str,
            type: ChannelType,
            *,
            reason: str | None = None,
            invitable: bool = MISSING,
            rate_limit_per_user: int) -> Thread:
        """
        Create a thread that is not connected to an existing message.

        Parameters
        ----------
        name : str
            The name of the thread.
        type : novus.enums.ChannelType
            The type of the channel.
        invitable : bool
            Whether non-moderators can add other non-moderators to a thread -
            only available when creating private threads.
        rate_limit_per_user : int
            The amount of seconds that a user has to wait before sending
            another message.
        reason : str | None
            The reason shown in the audit log.
        """

        params: dict[str, Any] = {}
        params["name"] = name
        params["type"] = type
        add_not_missing(params, "invitable", invitable)
        add_not_missing(params, "rate_limit_per_user", rate_limit_per_user)
        return await self.state.channel.start_thread_without_message(
            self.id,
            reason=reason,
            **params,
        )


class GuildVoiceChannel(GuildTextChannel, VoiceChannel):
    """
    A voice channel inside of a guild.

    Attributes
    ----------
    id : int
        The ID of the channel.
    type : novus.ChannelType
        The type of the channel.
    guild : novus.BaseGuild
        The ID of the guild associated with the channel. May be ``None`` for
        some channel objects received over gateway guild dispatches.
    position: int
        The sorting position of the channel (relative to its parent container).
    overwrites: list[novus.PermissionOverwrite]
        The permission overwrites assoicated with this channel.
    name : str
        The name of the channel.
    topic : str | None
        The topic set in the channel.
    nsfw : bool
        Whether or not the channel is marked as NSFW.
    last_message_id : int | None
        The ID of the last message sent in the channel. May or may not point to
        an existing or valid message or thread.
    parent : novus.Channel | None
        The parent container channel.
    rate_limit_per_user: int | None
        The amount of seconds a user has to wait before sending another
        message.
    bitrate : int
        The bitrate (in bits) of the voice channel.
    user_limit : int | None
        The user limit of the voice channel.
    """

    __slots__ = (
        'state',
        'id',
        'type',
        'guild',
        'position',
        'overwrites',
        'name',
        'topic',
        'nsfw',
        'last_message_id',
        'parent',
        'rate_limit_per_user',
        'bitrate',
        'user_limit',
    )

    bitrate: int
    user_limit: int | None

    def __init__(
            self,
            *,
            state: HTTPConnection,
            data: payloads.Channel,
            guild_id: int | None = None):
        super().__init__(state=state, data=data, guild_id=guild_id)
        self.bitrate = data.get("bitrate", 0)
        self.user_limit = data.get("user_limit")


class GuildStageChannel(GuildChannel, VoiceChannel):
    """
    A stage channel within a guild.
    """


class GuildCategory(GuildChannel):
    """
    A guild category channel.
    """


class GuildAnnouncementChannel(GuildTextChannel):
    """
    An announcement channel within a guild.
    """

    async def follow(
            self: abc.StateSnowflake,
            destination: int | abc.Snowflake | Channel) -> None:
        """
        Follow an announcement channel to send messages to the specific target
        channel.

        Parameters
        ----------
        destination : int | novus.abc.Snowflake
            The channel you want to send the announcements to.
        """

        await self.state.channel.delete_channel_permission(
            self.id,
            try_id(destination),
        )


class GuildForumChannel(GuildChannel):
    """
    A forum channel within a guild.
    """


class Thread(GuildTextChannel):
    """
    A model representing a thread.
    """

    __slots__ = (
        'state',
        'id',
        'type',
        'guild',
        'position',
        'overwrites',
        'name',
        'topic',
        'nsfw',
        'last_message_id',
        'parent',
        'rate_limit_per_user',
        '_members',
        'owner',
        'member_count',
        'message_count',
        'total_message_sent',
        'applied_tags',
        'archived',
        'auto_archive_duration',
        'archive_timestamp',
        'locked',
    )

    owner: GuildMember | User
    member_count: int
    message_count: int
    total_message_sent: int
    applied_tags: list[int]
    archived: bool
    auto_archive_duration: int
    archive_timestamp: dt | None
    locked: bool

    def __init__(
            self,
            *,
            state: HTTPConnection,
            data: payloads.Channel,
            guild_id: int | None = None):
        super().__init__(state=state, data=data, guild_id=guild_id)
        self._members: dict[int, ThreadMember] = {}
        assert "owner_id" in data
        try:
            self.owner = self.guild.get_member(data["owner_id"])  # pyright: ignore
            if self.owner is None:
                raise ValueError
        except (AttributeError, ValueError):
            self.owner = self.state.cache.get_user(data["owner_id"])
        self.member_count = data.get("member_count", 0)
        self.message_count = data.get("message_count", 0)
        self.total_message_sent = data.get("total_message_sent", 0)
        self.applied_tags = []
        metadata = data.get("thread_metadata", {})
        self.archived = metadata.get("archived", False)
        self.auto_archive_duration = metadata.get("auto_archive_duration", 0)
        self.archive_timestamp = parse_timestamp(metadata.get("archive_timestamp"))
        self.locked = metadata.get("locked", False)

    def _add_member(self, member: ThreadMember) -> None:
        self._members[member.id] = member

    def _remove_member(self, id: int | str) -> None:
        self._members.pop(try_snowflake(id), None)

    @property
    def members(self) -> list[ThreadMember]:
        return list(self._members.values())

    # API methods

    async def create_thread(
            self: abc.StateSnowflake,
            name: str,
            *,
            reason: str | None = None,
            auto_archive_duration: Literal[60, 1_440, 4_320, 10_080] = MISSING,
            rate_limit_per_user: int = MISSING,
            applied_tags: list[int | ForumTag],
            content: str = MISSING,
            embeds: list[Embed] = MISSING,
            allowed_mentions: AllowedMentions = MISSING,
            components: list[ActionRow] = MISSING,
            files: list[File] = MISSING,
            flags: MessageFlags = MISSING) -> Thread:
        """
        Create a thread that is not connected to an existing message.

        Parameters
        ----------
        name : str
            The name of the thread.
        type : novus.enums.ChannelType
            The type of the channel.
        invitable : bool
            Whether non-moderators can add other non-moderators to a thread -
            only available when creating private threads.
        rate_limit_per_user : int
            The amount of seconds that a user has to wait before sending
            another message.
        reason : str | None
            The reason shown in the audit log.
        """

        params: dict[str, Any] = {}
        params["name"] = name
        add_not_missing(params, "auto_archive_duration", auto_archive_duration)
        add_not_missing(params, "rate_limit_per_user", rate_limit_per_user)
        add_not_missing(params, "applied_tags", applied_tags)

        message: dict[str, Any] = {}
        add_not_missing(message, "content", content)
        add_not_missing(message, "embeds", embeds)
        add_not_missing(message, "allowed_mentions", allowed_mentions)
        add_not_missing(message, "components", components)
        add_not_missing(message, "files", files)
        add_not_missing(message, "flags", flags)
        params["message"] = message

        return await self.state.channel.start_thread_without_message(
            self.id,
            reason=reason,
            **params,
        )

    async def join_thread(self: abc.StateSnowflake) -> None:
        """
        Adds the current user to a thread.
        """

        await self.state.channel.add_thread_member(self.id, "@me")

    async def add_thread_member(
            self: abc.StateSnowflake,
            user: int | abc.Snowflake) -> None:
        """
        Add a user to a thread.

        Parameters
        ----------
        user : int | novus.abc.Snowflake
            The user who you want to add.
        """

        await self.state.channel.add_thread_member(self.id, try_id(user))

    async def leave_thread(self: abc.StateSnowflake) -> None:
        """
        Remove the current user from the thread.
        """

        await self.state.channel.remove_thread_member(self.id, "@me")

    async def remove_thread_member(
            self: abc.StateSnowflake,
            user: int | abc.Snowflake) -> None:
        """
        Remove a member from the thread.

        Parameters
        ----------
        user : int | novus.abc.Snowflake
            The user that you want to remove.
        """

        await self.state.channel.remove_thread_member(self.id, try_id(user))


class ForumTag:
    ...  # TODO
