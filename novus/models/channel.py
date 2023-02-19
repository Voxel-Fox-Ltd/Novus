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

import logging
from typing import TYPE_CHECKING, Type

from ..enums import ChannelType, PermissionOverwriteType
from ..flags import Permissions
from ..utils import generate_repr, parse_timestamp, try_snowflake
from .api_mixins.channel import (
    AnnouncementChannelAPIMixin,
    ChannelAPIMixin,
    ForumChannelAPIMixin,
    TextChannelAPIMixin,
)
from .mixins import HasChannel, Hashable
from .user import User

if TYPE_CHECKING:
    from datetime import datetime as dt

    from ..api import HTTPConnection
    from ..payloads import Channel as ChannelPayload
    from . import Guild, GuildMember, ThreadMember
    from . import api_mixins as amix

__all__ = (
    'PermissionOverwrite',
    'Channel',
    'GuildChannel',
    'GuildTextChannel',
    'DMChannel',
    'GroupDMChannel',
    'Thread',
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
        #     return Channel
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
        data: ChannelPayload,
        guild_id: int | None = None) -> Channel:
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
            id: int,
            type: PermissionOverwriteType,
            *,
            allow: Permissions,
            deny: Permissions):
        self.id = id
        self.type = type
        self.allow = allow
        self.deny = deny

    __repr__ = generate_repr(('id', 'type', 'allow', 'deny',))


class Channel(Hashable, HasChannel, ChannelAPIMixin):
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
    raw: ChannelPayload
    guild: Guild | amix.GuildAPIMixin | None

    def __init__(self, *, state: HTTPConnection, data: ChannelPayload):
        self.state = state
        self.id = try_snowflake(data['id'])
        self.type = ChannelType(data.get('type', 0))
        self.raw = data
        if "guild" in self.__slots__:
            self.guild = None

    __repr__ = generate_repr(('id',))

    async def _get_channel(self) -> int:
        return self.id

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


class TextChannel(Channel, TextChannelAPIMixin):
    """
    An abstract channel class.

    Represents any channel that has messages.
    """


class VoiceChannel(Channel):
    """
    An abstract channel class.

    Represents any channel that has voice capability.
    """


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


class GuildChannel(Channel):
    """
    An abstract channel class.

    Any channel inside of a guild.
    """

    id: int
    guild: Guild | amix.GuildAPIMixin
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
            data: ChannelPayload,
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
            self.parent = self.state.cache.get_channel(parent_id, or_object=True)
        self.rate_limit_per_user = data.get('rate_limit_per_user')

    __repr__ = generate_repr(('id', 'guild', 'name',))

    def __str__(self) -> str:
        return f"#{self.name}"

    @property
    def mention(self) -> str:
        return f"<#{self.id}>"


class GuildTextChannel(GuildChannel, TextChannel):
    """
    A text channel inside of a guild.

    Attributes
    ----------
    id : int
        The ID of the channel.
    type : novus.ChannelType
        The type of the channel.
    guild : novus.Guild | novus.Object | None
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


class GuildVoiceChannel(GuildTextChannel, VoiceChannel):
    """
    A voice channel inside of a guild.

    Attributes
    ----------
    id : int
        The ID of the channel.
    type : novus.ChannelType
        The type of the channel.
    guild : novus.Guild | novus.Object | None
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
            data: ChannelPayload,
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


class GuildAnnouncementChannel(GuildTextChannel, AnnouncementChannelAPIMixin):
    """
    An announcement channel within a guild.
    """


class GuildForumChannel(GuildChannel, ForumChannelAPIMixin):
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

    owner: GuildMember | User | amix.UserAPIMixin
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
            data: ChannelPayload,
            guild_id: int | None = None):
        super().__init__(state=state, data=data, guild_id=guild_id)
        self._members: dict[int, ThreadMember] = {}
        assert "owner_id" in data
        try:
            self.owner = self.guild.get_member(data["owner_id"])  # pyright: ignore
            if self.owner is None:
                raise ValueError
        except (AttributeError, ValueError):
            self.owner = self.state.cache.get_user(data["owner_id"], or_object=True)
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


class ForumTag:
    ...  # TODO
