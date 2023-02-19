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

from typing import TYPE_CHECKING, Any, TypeAlias, overload

from ....enums import ChannelType
from ....utils import MISSING, try_object

if TYPE_CHECKING:
    import io

    from ... import (
        Channel,
        ForumTag,
        GuildTextChannel,
        PermissionOverwrite,
        Reaction,
        Thread,
    )
    from ...abc import Snowflake, StateSnowflake

    FileT: TypeAlias = str | bytes | io.IOBase


class GuildChannelAPI:

    async def fetch_channels(self: StateSnowflake) -> list[Channel]:
        """
        Fetch all of the channels from a guild.

        Returns
        -------
        list[novus.model.Channel]
            A list of channels from the guild.
        """

        channels = await self.state.guild.get_guild_channels(self.id)
        for c in channels:
            c.guild = self
        return channels

    @overload
    async def create_channel(
            self: StateSnowflake,
            *,
            name: str,
            type: ChannelType = ChannelType.guild_text,
            bitrate: int = ...,
            user_limit: int = ...,
            rate_limit_per_user: int = ...,
            position: int = ...,
            permission_overwrites: list[PermissionOverwrite] = ...,
            parent: int | Snowflake = ...,
            nsfw: bool = ...,
            default_auto_archive_duration: int = ...,
            default_reaction_emoji: Reaction = ...,
            available_tags: list[ForumTag] = ...) -> GuildTextChannel:
        ...

    @overload
    async def create_channel(
            self: StateSnowflake,
            *,
            name: str,
            type: ChannelType = ChannelType.private_thread,
            bitrate: int = ...,
            user_limit: int = ...,
            rate_limit_per_user: int = ...,
            position: int = ...,
            permission_overwrites: list[PermissionOverwrite] = ...,
            parent: int | Snowflake = ...,
            nsfw: bool = ...,
            default_auto_archive_duration: int = ...,
            default_reaction_emoji: Reaction = ...,
            available_tags: list[ForumTag] = ...) -> Thread:
        ...

    @overload
    async def create_channel(
            self: StateSnowflake,
            *,
            name: str,
            type: ChannelType = ChannelType.public_thread,
            bitrate: int = ...,
            user_limit: int = ...,
            rate_limit_per_user: int = ...,
            position: int = ...,
            permission_overwrites: list[PermissionOverwrite] = ...,
            parent: int | Snowflake = ...,
            nsfw: bool = ...,
            default_auto_archive_duration: int = ...,
            default_reaction_emoji: Reaction = ...,
            available_tags: list[ForumTag] = ...) -> Thread:
        ...

    async def create_channel(
            self: StateSnowflake,
            *,
            name: str,
            type: ChannelType = MISSING,
            bitrate: int = MISSING,
            user_limit: int = MISSING,
            rate_limit_per_user: int = MISSING,
            position: int = MISSING,
            permission_overwrites: list[PermissionOverwrite] = MISSING,
            parent: int | Snowflake = MISSING,
            nsfw: bool = MISSING,
            default_auto_archive_duration: int = MISSING,
            default_reaction_emoji: Reaction = MISSING,
            available_tags: list[ForumTag] = MISSING) -> Channel:
        """
        Create a channel within the guild.

        Parameters
        ----------
        name : str
            The name of the channel.
        type : novus.ChannelType
            The type of the channel.
        bitrate : int
            The bitrate for the channel. Only for use with voice channels.
        user_limit : int
            The user limit for the channel. Only for use with voice channels.
        rate_limit_per_user : int
            The slowmode seconds on the channel.
        position : int
            The channel position.
        permission_overwrites : list[novus.PermissionOverwrite]
            A list of permission overwrites for the channel.
        parent : int | novus.abc.Snowflake
            A parent object for the channel.
        nsfw : bool
            Whether or not the channel will be set to NSFW.
        default_auto_archive_duration : int
            The default duration that clients use (in minutes) to automatically
            archive the thread after recent activity. Only for use with forum
            channels.
        default_reaction_emoji : Reaction
            The default add reaction button to be shown on threads. Only for
            use with forum channels.
        available_tags : list[ForumTag]
            The tags available for threads. Only for use with forum channels.

        Returns
        -------
        novus.model.Channel
            The created channel.
        """

        update: dict[str, Any] = {}

        if name is not MISSING:
            update["name"] = name
        if type is not MISSING:
            update["type"] = type
        if bitrate is not MISSING:
            update["bitrate"] = bitrate
        if user_limit is not MISSING:
            update["user_limit"] = user_limit
        if rate_limit_per_user is not MISSING:
            update["rate_limit_per_user"] = rate_limit_per_user
        if position is not MISSING:
            update["position"] = position
        if permission_overwrites is not MISSING:
            update["permission_overwrites"] = permission_overwrites
        if parent is not MISSING:
            update["parent"] = try_object(parent)
        if nsfw is not MISSING:
            update["nsfw"] = nsfw
        if default_auto_archive_duration is not MISSING:
            update["default_auto_archive_duration"] = default_auto_archive_duration
        if default_reaction_emoji is not MISSING:
            update["default_reaction_emoji"] = default_reaction_emoji
        if available_tags is not MISSING:
            update["available_tags"] = available_tags

        channel = await self.state.guild.create_guild_channel(self.id, **update)
        channel.guild = self
        return channel

    async def move_channels(self: StateSnowflake) -> None:
        raise NotImplementedError()

    async def fetch_active_threads(self: StateSnowflake) -> list[Thread]:
        """
        Get the active threads from inside the guild.

        Returns
        -------
        list[novus.model.Thread]
            A list of threads.
        """

        threads = await self.state.guild.get_active_guild_threads(self.id)
        for t in threads:
            t.guild = self
        return threads
