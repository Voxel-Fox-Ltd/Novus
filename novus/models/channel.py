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
from typing import TYPE_CHECKING, Any, Literal, Type

from typing_extensions import Self

from ..enums import ChannelType, ForumLayout, ForumSortOrder, PermissionOverwriteType
from ..flags import ChannelFlags, Permissions
from ..utils import (
    MISSING,
    DiscordDatetime,
    add_not_missing,
    generate_repr,
    parse_timestamp,
    try_id,
    try_snowflake,
)
from .abc import Hashable, Messageable
from .emoji import PartialEmoji
from .user import User

if TYPE_CHECKING:
    from .. import payloads
    from ..api import APIIterator, HTTPConnection
    from ..flags import MessageFlags
    from ..utils.types import AnySnowflake
    from . import abc
    from .embed import Embed
    from .file import File
    from .guild import BaseGuild
    from .guild_member import GuildMember, ThreadMember
    from .invite import Invite
    from .message import AllowedMentions, Message
    from .role import Role
    from .ui.action_row import ActionRow

__all__ = (
    'PermissionOverwrite',
    'Channel',
    'ForumTag',

    # 'GuildTextChannel',
    # 'DMChannel',
    # 'GroupDMChannel',
    # 'Thread',
    # 'GuildVoiceChannel',
    # 'GuildStageChannel',
    # 'GuildCategory',
    # 'GuildAnnouncementChannel',
    # 'GuildForumChannel',
)


log = logging.getLogger("novus.channel")


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
            type: PermissionOverwriteType | type[Role] | type[User] | None = None,
            *,
            allow: Permissions | None = None,
            deny: Permissions | None = None):
        self.id = try_id(id)
        self.type: PermissionOverwriteType
        from .guild import BaseGuild
        from .guild_member import GuildMember
        from .role import Role
        if type:
            if type is Role:
                self.type = PermissionOverwriteType.role
            elif type is User:
                self.type = PermissionOverwriteType.member
            else:
                self.type = type
        elif isinstance(id, (BaseGuild, Role)):
            self.type = PermissionOverwriteType.role
        elif isinstance(id, (User, GuildMember)):
            self.type = PermissionOverwriteType.member
        else:
            raise TypeError("Type cannot be set implicitly from a non guild/role/user type.")
        self.allow: Permissions = allow or Permissions()
        self.deny: Permissions = deny or Permissions()

    __repr__ = generate_repr(('id', 'type', 'allow', 'deny',))

    def _to_data(self) -> payloads.ChannelOverwrite:
        return {
            "id": str(self.id),
            "type": self.type.value,
            "allow": str(self.allow.value),
            "deny": str(self.deny.value),
        }


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


class Channel(Hashable, Messageable):
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
    """

    __slots__ = (
        'state',
        'id',
        'type',
        'guild_id',
        'position',
        'overwrites',
        'name',
        'topic',
        'nsfw',
        'last_message_id',
        'bitrate',
        'user_limit',
        'rate_limit_per_user',
        'parent_id',
        'last_pin_timestamp',
        'rtc_region',
        'video_quality_mode',
        'message_count',
        'member_count',
        'archived',
        'auto_archive_duration',
        'archive_timestsamp',
        'locked',
        'invitable',
        'create_timestamp',
        'default_auto_archive_duration',
        'flags',
        'total_messages_sent',
        'available_tags',
        'applied_tags',
        'default_reaction_emoji',
        'default_thread_rate_limit_per_user',
        'default_sort_order',
        'default_forum_layout',
        '_cs_parent',
        '_cs_guild',
        '_members',
        '_channels',
    )

    id: int
    type: ChannelType
    guild_id: int | None
    # guild: BaseGuild | None
    position: int | None
    overwrites: list[PermissionOverwrite] | None
    name: str | None
    topic: str | None
    nsfw: bool
    last_message_id: int | None
    bitrate: int | None
    user_limit: int | None
    rate_limit_per_user: int | None
    # recipients: list[User] | None
    # icon_hash: str | None
    # icon: Asset | None
    # owner_id: int | None
    # owner: User | None  # Only group DMs
    # application_id: int | None
    # managed: bool
    parent_id: int | None
    # parent: Channel | None
    last_pin_timestamp: DiscordDatetime | None
    rtc_region: str | None
    video_quality_mode: None
    message_count: int | None
    member_count: int | None
    # <thread_metadata>
    archived: bool | None
    auto_archive_duration: int | None
    archive_timestsamp: DiscordDatetime | None
    locked: bool | None
    invitable: bool | None
    create_timestamp: DiscordDatetime | None
    # </thread_metadata>
    # member: ThreadMember | None  # Ignoring
    default_auto_archive_duration: int | None
    # permissions: Permissions  # Only included in interactions
    flags: ChannelFlags | None
    total_messages_sent: int | None
    available_tags: list[ForumTag] | None
    applied_tags: list[ForumTag] | None
    default_reaction_emoji: PartialEmoji | None
    default_thread_rate_limit_per_user: int | None
    default_sort_order: ForumSortOrder | None
    default_forum_layout: ForumLayout | None

    def __init__(
            self,
            *,
            state: HTTPConnection,
            data: payloads.Channel,
            guild_id: int | str | None = None):
        self.state = state
        self.id = try_snowflake(data['id'])
        self.type = ChannelType(data.get('type', 0))
        self.guild_id = (
            try_snowflake(data.get("guild_id"))
            or try_snowflake(guild_id)
        )
        self._members: dict[int, GuildMember] = {}
        self._channels: dict[int, Channel] = {}
        self._update(data)

    __repr__ = generate_repr(('id',))

    def __str__(self) -> str:
        return f"#{self.name}"

    def _update(self, data: payloads.Channel) -> Self:
        self.position = data.get("position")
        self.overwrites = [
            PermissionOverwrite(
                id=int(d['id']),
                type=(
                    PermissionOverwriteType(d['type']) if isinstance(d["type"], int)
                    else PermissionOverwriteType[d["type"]]
                ),
                allow=Permissions(int(d['allow'])),
                deny=Permissions(int(d['deny'])),
            )
            for d in data.get('permission_overwrites', list())
        ]
        self.name = data.get("name")
        self.topic = data.get("topic")
        self.nsfw = data.get("nsfw", False)
        lmid = data.get("last_message_id")
        self.last_message_id = int(lmid) if lmid is not None else None
        self.bitrate = data.get("bitrate")
        self.user_limit = data.get("user_limit")
        self.rate_limit_per_user = data.get("rate_limit_per_user")
        # self.recipients = data.get("recipients")
        # self.icon_hash = data.get("icon_hash")
        # self.owner_id = data.get("owner_id")
        # self.application_id = data.get("application_id")
        # self.managed = data.get("managed")
        pid = data.get("parent_id")
        ipid = int(pid) if pid is not None else None
        try:
            if ipid != self.parent_id:
                del self._cs_parent
                raise ValueError
        except (AttributeError, ValueError):
            self.parent_id = ipid
        self.last_pin_timestamp = parse_timestamp(data.get("last_pin_timestamp"))
        self.rtc_region = data.get("rtc_region")
        # self.video_quality_mode =  data.get("video_quality_mode")  # TODO make enum class
        self.message_count = data.get("message_count")
        self.member_count = data.get("member_count")
        self.archived = None
        self.auto_archive_duration = None
        self.archive_timestsamp = None
        self.locked = None
        self.invitable = None
        self.create_timestamp = None
        if "thread_metadata" in data:
            tmd = data["thread_metadata"]
            self.archived = tmd["archived"]
            self.auto_archive_duration = tmd["auto_archive_duration"]
            self.archive_timestsamp = parse_timestamp(tmd.get("archive_timestsamp"))
            self.locked = tmd["locked"]
            self.invitable = tmd.get("invitable")
            self.create_timestamp = parse_timestamp(tmd.get("create_timestamp"))
        self.default_auto_archive_duration = data.get("default_auto_archive_duration")
        self.flags = ChannelFlags(data.get("flags", 0))
        self.total_messages_sent = data.get("total_messages_sent")
        self.available_tags = [
            ForumTag(data=i) for i in
            data.get("available_tags", [])
        ]
        self.applied_tags = [
            ForumTag(data=i) for i in
            data.get("applied_tags", [])
        ]
        emoji = data.get("default_reaction_emoji")
        self.default_reaction_emoji = PartialEmoji(data=emoji) if emoji else None
        self.default_thread_rate_limit_per_user = data.get("default_thread_rate_limit_per_user")
        dso = data.get("default_sort_order")
        self.default_sort_order = ForumSortOrder(dso) if dso is not None else None
        dfl = data.get("default_forum_layout")
        self.default_forum_layout = ForumLayout(dfl) if dfl is not None else None
        return self

    @property
    def mention(self) -> str:
        return f"<#{self.id}>"

    @classmethod
    def partial(
            cls,
            state: HTTPConnection,
            id: int | str,
            type: ChannelType = ChannelType.guild_text) -> Self:
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

        return cls(
            state=state,
            data={"id": id, "type": type.value}  # pyright: ignore
        )

    # @cached_slot_property("_cs_guild")
    @property
    def guild(self) -> BaseGuild | None:
        if self.guild_id is None:
            return None
        return self.state.cache.get_guild(self.guild_id)

    # @cached_slot_property("_cs_parent")
    @property
    def parent(self) -> Channel | None:
        if self.parent_id is None:
            return None
        return self.state.cache.get_channel(self.parent_id)

    # Non-API thread/category only

    def _add_member(self, member: ThreadMember) -> None:
        self._members[member.id] = member

    def _remove_member(self, id: int | str) -> None:
        self._members.pop(try_snowflake(id), None)

    @property
    def channels(self) -> list[Channel]:
        return list(self._channels.values())

    def _add_channel(self, channel: Channel) -> None:
        self._channels[channel.id] = channel

    def _remove_channel(self, id: int | str) -> None:
        self._channels.pop(try_snowflake(id), None)

    @property
    def channel(self) -> list[Channel]:
        return list(self._channels.values())

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

    # API methods - text channel

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

    def messages(
            self,
            *,
            limit: int | None = 100,
            before: int | abc.Snowflake | Message = MISSING,
            after: int | abc.Snowflake | Message = MISSING) -> APIIterator[Message]:
        """
        Get an iterator of messages from a channel.

        Examples
        --------

        .. code-block::

            async for message in channel.messages(limit=1_000):
                print(message.content)

        .. code-block::

            messages = await channel.messages(limit=200).flatten()

        Parameters
        ----------
        limit : int
            The number of messages that you want to get.
        before : int | novus.abc.Snowflake
            Get messages before this ID.
            Only one of ``around``, ``before``, and ``after`` can be set.
        after : int | novus.abc.Snowflake
            Get messages after this ID.
            Only one of ``around``, ``before``, and ``after`` can be set.

        Returns
        -------
        APIIterator[novus.Message]
            The messages that were retrieved, as a generator.
        """

        from ..api import APIIterator  # circular import
        return APIIterator(
            method=self.fetch_messages,
            before=before,
            after=after,
            limit=limit,
            method_limit=100,
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

        .. code-block::

            async with channel.typing():
                ...
        """

        return Typing(self.state, self)

    async def fetch_pinned_messages(self: abc.StateSnowflake) -> list[Message]:
        """
        Get a list of pinned messages in the channel.
        """

        return await self.state.channel.get_pinned_messages(self.id)

    async def bulk_delete_messages(
            self: abc.StateSnowflake,
            messages: list[int] | list[abc.Snowflake],
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
            message_ids=try_id(messages),
        )

    async def create_thread(
            self: abc.StateSnowflake,
            name: str,
            type: ChannelType,
            *,
            reason: str | None = None,
            invitable: bool = MISSING,
            rate_limit_per_user: int) -> Channel:
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

    async def create_thread_in_forum(
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
            flags: MessageFlags = MISSING) -> Channel:
        """
        Create a thread in a forum or media channel.

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

        return await self.state.channel.start_thread_in_forum_channel(
            self.id,
            reason=reason,
            **params,
        )

    # API methods - announcement channel

    async def follow(
            self: abc.StateSnowflake,
            destination: AnySnowflake) -> None:
        """
        Follow an announcement channel to send messages to the specific target
        channel.

        Parameters
        ----------
        destination : int | novus.abc.Snowflake
            The channel you want to send the announcements to.
        """

        await self.state.channel.follow_announcement_channel(
            try_id(self),
            try_id(destination),
        )

    # API methods - threads

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

    def __init__(self, *, data: dict):
        ...  # TODO
