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

from typing import TYPE_CHECKING, Type
import logging

from .mixins import Hashable, Messageable
from .object import Object
from ..enums import ChannelType, PermissionOverwriteType
from ..flags import Permissions
from ..utils import try_snowflake, generate_repr

if TYPE_CHECKING:
    from .abc import StateSnowflake
    from ..api import HTTPConnection
    from ..payloads import Channel as ChannelPayload

__all__ = (
    'PermissionOverwrite',
    'Channel',
    'GuildChannel',
    'GuildTextChannel',
    'DMChannel',
    'GroupDMChannel',
    'Thread',
    'ForumTag',
)


log = logging.getLogger("novus.models.channel")


def channel_factory(
        channel_type: int) -> Type[Channel]:
    match channel_type:
        case ChannelType.guild_text.value:
            return GuildTextChannel
        case ChannelType.dm.value:
            return DMChannel
        # case ChannelType.guild_voice.value:
        #     return MessageableChannel
        case ChannelType.group_dm.value:
            return GroupDMChannel
        # case ChannelType.guild_category.value:
        #     return Channel
        # case ChannelType.guild_announcement.value:
        #     return GuildTextChannel
        # case ChannelType.announcement_thread.value:
        #     return GuildTextChannel
        case ChannelType.public_thread.value:
            return Thread
        case ChannelType.private_thread.value:
            return Thread
        # case ChannelType.guild_stage_voice.value:
        #     return Channel
        # case ChannelType.guild_directory.value:
        #     return Channel
        # case ChannelType.guild_forum.value:
        #     return Channel
        case _:
            log.warning(
                "Unknown channel type %s"
                % channel_type
            )
            return MessageableChannel


class PermissionOverwrite:
    """
    A class representing a permission overwrite for a guild channel.

    Parameters
    ----------
    id : int
        The ID of the target.
    type : novus.enums.PermissionOverwriteType
        The type of the target.
    allow : novus.flags.Permissions
        The permissions that the target is explicitly allowed.
    deny : novus.flags.Permissions
        The permissions that the target is explicitly denied.

    Attributes
    ----------
    id : int
        The ID of the target.
    type : novus.enums.PermissionOverwriteType
        The type of the target.
    allow : novus.flags.Permissions
        The permissions that the target is explicitly allowed.
    deny : novus.flags.Permissions
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


class Channel(Hashable):
    """
    The base channel object that all other channels inherit from. This is also
    the object that will be returned if there is an unknown channel type.
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
        self.type = ChannelType(data['type'])
        self.raw = data
        self.guild: StateSnowflake | None = None

    __repr__ = generate_repr(('id', 'type',))

    @staticmethod
    def _from_data(*, state: HTTPConnection, data: ChannelPayload) -> Channel:
        factory = channel_factory(data['type'])
        return factory(state=state, data=data)


class MessageableChannel(Channel, Messageable):

    async def _get_channel(self) -> int:
        return self.id


class DMChannel(MessageableChannel):
    """
    A channel associated with a user's DMs.

    Attributes
    ----------
    id : int
        The ID of the channel.
    """


class GroupDMChannel(MessageableChannel):
    """
    A channel associated with a group DM.

    Attributes
    ----------
    id : int
        The ID of the channel.
    """


class GuildChannel(Channel):

    __slots__ = (
        *Channel.__slots__[:-1],  # get all apart from ``raw``
        'guild_id',
        'position',
        'permissions_overwrites',
        'name',
        'topic',
        'nsfw',
        'last_message_id',
        'parent_id',
    )

    guild: StateSnowflake

    def __init__(self, *, state: HTTPConnection, data: ChannelPayload):
        super().__init__(state=state, data=data)
        del self.raw  # Not needed for known types)
        self.guild_id = try_snowflake(data.get('guild_id'))
        if self.guild_id is None:
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
        self.guild = Object(self.guild_id, state=self._state)

    __repr__ = generate_repr(('id', 'guild_id', 'name',))


class GuildTextChannel(GuildChannel, MessageableChannel):
    """
    A text channel inside of a guild.

    Attributes
    ----------
    id : int
        The ID of the channel.
    type : novus.enums.ChannelType
        The type of the channel.
    guild_id : int | None
        The ID of the guild associated with the channel. May be ``None`` for
        some channel objects received over gateway guild dispatches.
    position: int
        The sorting position of the channel (relative to its parent container).
    permissions_overwrites: list[novus.models.PermissionOverwrite]
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


class Thread(GuildTextChannel):
    """
    A model representing a thread.
    """


class ForumTag:
    ...  # TODO
