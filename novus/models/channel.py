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
from ..utils import generate_repr, try_snowflake
from .mixins import Hashable, Messageable
from .object import Object

if TYPE_CHECKING:
    from ..api import HTTPConnection
    from ..payloads import Channel as ChannelPayload
    from .abc import StateSnowflake

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
            return Channel


def channel_builder(
        *,
        state: HTTPConnection,
        data: ChannelPayload,
        guild: StateSnowflake | None = None) -> Channel:
    factory = channel_factory(data['type'])
    if guild is None or GuildChannel not in factory.mro():
        return factory(state=state, data=data)
    return factory(state=state, data=data, guild=guild)  # type: ignore


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
    raw : dict
        The raw data usede to construct the channel object.
    """

    __slots__ = (
        '_state',
        'id',
        'type',
        'guild',
        'raw',
    )

    def __init__(self, *, state: HTTPConnection, data: ChannelPayload):
        self._state = state
        self.id = try_snowflake(data['id'])
        self.type = ChannelType(data.get('type', 0))
        self.raw = data
        self.guild: StateSnowflake | None = None

    __repr__ = generate_repr(('id',))

    async def _get_channel(self) -> int:
        return self.id

    @classmethod
    def partial(cls, state: HTTPConnection, id: int | str) -> Channel:
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
        novus.Channel
            The channel object.
        """

        return cls(
            state=state,
            data={"id": id}  # pyright: ignore
        )


class DMChannel(Channel):
    """
    A channel associated with a user's DMs.

    Attributes
    ----------
    id : int
        The ID of the channel.
    """


class GroupDMChannel(Channel):
    """
    A channel associated with a group DM.

    Attributes
    ----------
    id : int
        The
         ID of the channel.
    """


class GuildChannel(Channel):

    __slots__ = (
        '_state',
        'id',
        'type',
        'guild',
        'guild_id',
        'position',
        'permissions_overwrites',
        'name',
        'topic',
        'nsfw',
        'last_message_id',
        'parent_id',
        'rate_limit_per_user',
    )

    guild: StateSnowflake

    def __init__(
            self,
            *,
            state: HTTPConnection,
            data: ChannelPayload,
            guild: int | StateSnowflake | None = None):
        super().__init__(state=state, data=data)
        del self.raw  # Not needed for known types)
        guild_id = try_snowflake(data.get('guild_id')) or guild
        if guild_id is None:
            raise ValueError("Missing guild ID from guild channel %s" % data)
        self.position = data.get('position', 0)
        self.permissions_overwrites = [
            PermissionOverwrite(
                id=int(d['id']),
                type=PermissionOverwriteType(d['type']),
                allow=Permissions(int(d['allow'])),
                deny=Permissions(int(d['deny'])),
            )
            for d in data.get('permission_overwrites', list())
        ]
        if 'name' not in data:
            raise TypeError(
                "Missing channel name from channel payload %s"
                % data
            )
        self.name = data['name']
        self.topic = data.get('topic', None)
        self.nsfw = data.get('nsfw', False)
        self.last_message_id = try_snowflake(data.get('last_message_id'))
        self.parent_id = try_snowflake(data.get('parent_id'))
        self.rate_limit_per_user: int | None = data.get('rate_limit_per_user')
        if isinstance(guild_id, int):
            self.guild = Object(guild_id, state=self._state)
        else:
            self.guild = guild_id

    __repr__ = generate_repr(('id', 'guild_id', 'name',))

    def __str__(self) -> str:
        return f"#{self.name}"

    @property
    def mention(self) -> str:
        return f"<#{self.id}>"


class GuildTextChannel(GuildChannel):
    """
    A text channel inside of a guild.

    Attributes
    ----------
    id : int
        The ID of the channel.
    type : novus.ChannelType
        The type of the channel.
    guild_id : int | None
        The ID of the guild associated with the channel. May be ``None`` for
        some channel objects received over gateway guild dispatches.
    position: int
        The sorting position of the channel (relative to its parent container).
    permissions_overwrites: list[novus.PermissionOverwrite]
        The overwrites assoicated with this channel.
    name : str
        The name of the channel.
    topic : str | None
        The topic set in the channel.
    nsfw : bool
        Whether or not the channel is marked as NSFW.
    last_message_id : int | None
        The ID of the last message sent in the channel. May or may not point to
        an existing or valid message or thread.
    parent_id : int | None
        The ID of the parent container channel.
    rate_limit_per_user: int | None
        The amount of seconds a user has to wait before sending another
        message.
    """


class GuildVoiceChannel(GuildTextChannel):
    """
    A text channel inside of a guild.

    Attributes
    ----------
    id : int
        The ID of the channel.
    type : novus.ChannelType
        The type of the channel.
    guild_id : int | None
        The ID of the guild associated with the channel. May be ``None`` for
        some channel objects received over gateway guild dispatches.
    position: int
        The sorting position of the channel (relative to its parent container).
    permissions_overwrites: list[novus.PermissionOverwrite]
        The overwrites assoicated with this channel.
    name : str
        The name of the channel.
    topic : str | None
        The topic set in the channel.
    nsfw : bool
        Whether or not the channel is marked as NSFW.
    last_message_id : int | None
        The ID of the last message sent in the channel. May or may not point to
        an existing or valid message or thread.
    parent_id : int | None
        The ID of the parent container channel.
    rate_limit_per_user: int | None
        The amount of seconds a user has to wait before sending another
        message.
    """


class GuildStageChannel(GuildChannel):
    """
    A stage channel within a guild.
    """


class GuildCategory(GuildChannel):
    """
    A guild category channel.

    Attributes
    ----------
    id : int
        The ID of the channel.
    type : novus.ChannelType
        The type of the channel.
    guild_id : int | None
        The ID of the guild associated with the channel. May be ``None`` for
        some channel objects received over gateway guild dispatches.
    position: int
        The sorting position of the channel (relative to its parent container).
    permissions_overwrites: list[novus.PermissionOverwrite]
        The overwrites assoicated with this channel.
    name : str
        The name of the channel.
    nsfw : bool
        Whether or not the channel is marked as NSFW.
    rate_limit_per_user: int | None
        The amount of seconds a user has to wait before sending another
        message.
    """


class GuildAnnouncementChannel(GuildTextChannel):
    """
    An announcement channel within a guild.
    """


class GuildForumChannel(GuildTextChannel):
    """
    A forum channel within a guild.
    """


class Thread(GuildTextChannel):
    """
    A model representing a thread.
    """


class ForumTag:
    ...  # TODO
