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

from datetime import datetime as dt
from typing import TYPE_CHECKING, Any, Literal, NoReturn, Type
from urllib.parse import quote_plus

from ..flags import Permissions
from ..models import (
    Channel,
    GuildMember,
    Invite,
    Message,
    PartialEmoji,
    Role,
    ThreadMember,
    User,
)
from ..utils import MISSING
from ._route import Route

if TYPE_CHECKING:
    from .. import payloads
    from ._http import HTTPConnection

__all__ = (
    'ChannelHTTPConnection',
)


class ChannelHTTPConnection:

    def __init__(self, parent: HTTPConnection):
        self.parent = parent

    async def get_channel(self, channel_id: int) -> Channel:
        """
        Get a channel object by its ID.
        """

        route = Route(
            "GET",
            "/channels/{channel_id}",
            channel_id=channel_id,
        )
        data: payloads.Channel = await self.parent.request(route)
        return Channel(state=self.parent, data=data)

    async def modify_channel(
            self,
            channel_id: int,
            *,
            reason: str | None = None,
            **kwargs: dict[str, Any]) -> Channel:
        """
        Modify a channel's settings.
        """

        post_data = self.parent._get_kwargs(
            {
                "type": (
                    "name",
                    "position",
                    "topic",
                    "nsfw",
                    "rate_limit_per_user",
                    "bitrate",
                    "user_limit",
                    "default_auto_archive_duration",
                    "default_thread_rate_limit_per_user",
                    "archived",
                    "auto_archive_duration",
                    "locked",
                    "invitable",
                ),
                "flags": (
                    "flags",
                    "default_sort_order",
                    "default_forum_layout",
                ),
                "snowflake": (
                    ("parent_id", "parent",),
                ),
                "image": (
                    "icon",
                ),
                "enum": (
                    "type",
                    ("rtc_region", "region",),
                ),
                "object": (
                    ("permission_overwrites", "overwrites",),
                    "available_tags",
                    "default_reaction_emoji",
                    "applied_tags",
                ),
            },
            kwargs,
        )

        route = Route(
            "PATCH",
            "/channels/{channel_id}",
            channel_id=channel_id,
        )
        data: payloads.Channel = await self.parent.request(
            route,
            reason=reason,
            data=post_data,
        )
        return Channel(state=self.parent, data=data)

    async def delete_channel(
            self,
            channel_id: int,
            *,
            reason: str | None = None) -> None:
        """
        Delete a channel (or close a DM channel).
        """

        route = Route(
            "DELETE",
            "/channels/{channel_id}",
            channel_id=channel_id,
        )
        await self.parent.request(
            route,
            reason=reason,
        )

    async def get_channel_messages(
            self,
            channel_id: int,
            *,
            around: int = MISSING,
            before: int = MISSING,
            after: int = MISSING,
            limit: int = MISSING) -> list[Message]:
        """
        Get a channel object by its ID.
        """

        params: dict[str, int] = {}
        if around is not MISSING:
            params["around"] = around
        if before is not MISSING:
            params["before"] = before
        if after is not MISSING:
            params["after"] = after
        if limit is not MISSING:
            params["limit"] = limit

        route = Route(
            "GET",
            "/channels/{channel_id}/messages",
            channel_id=channel_id,
        )
        data: list[payloads.Message] = await self.parent.request(
            route,
            params=params,
        )
        return [
            Message(state=self.parent, data=d)
            for d in data
        ]

    async def get_channel_message(self, channel_id: int, message_id: int) -> Message:
        """
        Get a specific message inside of a channel.
        """

        route = Route(
            "GET",
            "/channels/{channel_id}/messages/{message_id}",
            channel_id=channel_id,
            message_id=message_id,
        )
        data: payloads.Message = await self.parent.request(route)
        return Message(state=self.parent, data=data)

    async def create_message(
            self,
            channel_id: int,
            **kwargs: dict[str, Any]) -> Message:
        """
        Create a new message inside of a channel.
        """

        route = Route(
            "POST",
            "/channels/{channel_id}/messages",
            channel_id=channel_id,
        )

        post_data = self.parent._get_kwargs(
            {
                "type": (
                    "content",
                    "tts",
                ),
                "object": (
                    "embeds",
                    "allowed_mentions",
                    "components",
                    "message_reference",
                ),
                "flags": (
                    "flags",
                ),
                "snowflake": (
                    ("sticker_ids", "stickers",),
                ),
            },
            kwargs,
        )
        files = post_data.pop("files", [])

        data: payloads.Message = await self.parent.request(
            route,
            data=post_data,
            files=files,
        )
        return Message(state=self.parent, data=data)

    async def crosspost_message(
            self,
            channel_id: int,
            message_id: int) -> Message:
        """
        Crosspost a message.
        """

        route = Route(
            "POST",
            "/channels/{channel_id}/messages/{message_id}/crosspost",
            channel_id=channel_id,
            message_id=message_id,
        )
        data: payloads.Message = await self.parent.request(route)
        return Message(state=self.parent, data=data)

    async def create_reaction(
            self,
            channel_id: int,
            message_id: int,
            emoji: str | PartialEmoji) -> None:
        """
        Create a reaction on a message.
        """

        emoji_str: str
        if isinstance(emoji, str):
            emoji_str = quote_plus(emoji)
        elif isinstance(emoji, PartialEmoji):  # pyright: ignore[reportUnnecessaryIsInstance]
            emoji_str = f"{emoji.name}:{emoji.id}"
        else:
            raise ValueError
        route = Route(
            "PUT",
            "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me",
            channel_id=channel_id,
            message_id=message_id,
            emoji=emoji_str,
        )
        await self.parent.request(route)

    async def delete_own_reaction(
            self,
            channel_id: int,
            message_id: int,
            emoji: str | PartialEmoji) -> None:
        """
        Remove your own reaction to a message.
        """

        emoji_str: str
        if isinstance(emoji, str):
            emoji_str = quote_plus(emoji)
        elif isinstance(emoji, PartialEmoji):  # pyright: ignore[reportUnnecessaryIsInstance]
            emoji_str = f"{emoji.name}:{emoji.id}"
        else:
            raise ValueError
        route = Route(
            "DELETE",
            "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me",
            channel_id=channel_id,
            message_id=message_id,
            emoji=emoji_str,
        )
        await self.parent.request(route)

    async def delete_user_reaction(
            self,
            channel_id: int,
            message_id: int,
            emoji: str | PartialEmoji,
            user_id: int) -> None:
        """
        Remove another user's reaction from a message.
        """

        emoji_str: str
        if isinstance(emoji, str):
            emoji_str = quote_plus(emoji)
        elif isinstance(emoji, PartialEmoji):  # pyright: ignore[reportUnnecessaryIsInstance]
            emoji_str = f"{emoji.name}:{emoji.id}"
        else:
            raise ValueError
        route = Route(
            "DELETE",
            "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/{user_id}",
            channel_id=channel_id,
            message_id=message_id,
            emoji=emoji_str,
            user_id=user_id,
        )
        await self.parent.request(route)

    async def get_reactions(
            self,
            channel_id: int,
            message_id: int,
            emoji: str | PartialEmoji) -> list[User]:
        """
        Get a list of users who reacted to a message with a particular emoji.
        """

        emoji_str: str
        if isinstance(emoji, str):
            emoji_str = quote_plus(emoji)
        elif isinstance(emoji, PartialEmoji):  # pyright: ignore[reportUnnecessaryIsInstance]
            emoji_str = f"{emoji.name}:{emoji.id}"
        else:
            raise ValueError
        route = Route(
            "GET",
            "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/",
            channel_id=channel_id,
            message_id=message_id,
            emoji=emoji_str,
        )
        data: list[payloads.User] = await self.parent.request(route)
        return [
            User(state=self.parent, data=d)
            for d in data
        ]

    async def delete_all_reactions(
            self,
            channel_id: int,
            message_id: int) -> None:
        """
        Remove all reactions from a message.
        """
        route = Route(
            "DELETE",
            "/channels/{channel_id}/messages/{message_id}/reactions",
            channel_id=channel_id,
            message_id=message_id,
        )
        await self.parent.request(route)

    async def delete_all_reactions_for_emoji(
            self,
            channel_id: int,
            message_id: int,
            emoji: str | PartialEmoji) -> None:
        """
        Remove all reactions for the given emoji on a message.
        """

        emoji_str: str
        if isinstance(emoji, str):
            emoji_str = quote_plus(emoji)
        elif isinstance(emoji, PartialEmoji):  # pyright: ignore[reportUnnecessaryIsInstance]
            emoji_str = f"{emoji.name}:{emoji.id}"
        else:
            raise ValueError
        route = Route(
            "DELETE",
            "/channels/{channel_id}/messages/{message_id}/reactions/{emoji}",
            channel_id=channel_id,
            message_id=message_id,
            emoji=emoji_str,
        )
        await self.parent.request(route)

    async def edit_message(
            self,
            channel_id: int,
            message_id: int,
            **kwargs: dict[str, Any]) -> Message:
        """
        Edit an existing message.
        """

        route = Route(
            "PATCH",
            "/channels/{channel_id}/messages/{message_id}",
            channel_id=channel_id,
            message_id=message_id,
        )

        post_data = self.parent._get_kwargs(
            {
                "type": (
                    "content",
                ),
                "object": (
                    "embeds",
                    "allowed_mentions",
                    "components",
                    "attachments",
                ),
                "flags": (
                    "flags",
                )
            },
            kwargs,
        )
        files = post_data.pop("files", [])

        data: payloads.Message = await self.parent.request(
            route,
            data=post_data,
            files=files,
        )
        return Message(state=self.parent, data=data)

    async def delete_message(
            self,
            channel_id: int,
            message_id: int,
            *,
            reason: str | None = None) -> None:
        """
        Delete an existing message.
        """

        route = Route(
            "DELETE",
            "/channels/{channel_id}/messages/{message_id}",
            channel_id=channel_id,
            message_id=message_id,
        )
        await self.parent.request(route, reason=reason)

    async def bulk_delete_messages(
            self,
            channel_id: int,
            *,
            reason: str | None = None,
            message_ids: list[int]) -> None:
        """
        Delete multiple messages.
        """

        route = Route(
            "POST",
            "/channels/{channel_id}/messages/bulk-delete",
            channel_id=channel_id,
        )
        await self.parent.request(
            route,
            reason=reason,
            data={
                "messages": message_ids
            },
        )

    async def edit_channel_permissions(
            self,
            channel_id: int,
            overwrite_id: int,
            *,
            reason: str | None = None,
            allow: Permissions = Permissions.none(),
            deny: Permissions = Permissions.none(),
            type: Type[User] | Type[GuildMember] | Type[Role]) -> None:
        """
        Update the permissions for a given item in the channel.
        """

        route = Route(
            "PUT",
            "/channels/{channel_id}/permissions/{overwrite_id}",
            channel_id=channel_id,
            overwrite_id=overwrite_id,
        )

        post_data = {
            "allow": str(allow.value),
            "deny": str(deny.value),
            "type": 0 if type is Role else 1,
        }

        await self.parent.request(
            route,
            reason=reason,
            data=post_data,
        )

    async def get_channel_invites(
            self,
            channel_id: int) -> list[Invite]:
        """
        Get the invites for a channel.
        """

        route = Route(
            "GET",
            "/channels/{channel_id}/invites",
            channel_id=channel_id,
        )
        data: list[payloads.InviteWithMetadata] = await self.parent.request(route)
        return [
            Invite(state=self.parent, data=d)
            for d in data
        ]

    async def create_channel_invite(
            self,
            channel_id: int,
            *,
            reason: str | None = None,
            **kwargs: dict[str, Any]) -> Invite:
        """
        Create an invite for the channel.
        """

        route = Route(
            "POST",
            "/channels/{channel_id}/invites",
            channel_id=channel_id,
        )

        post_data = self.parent._get_kwargs(
            {
                "type": (
                    "max_age",
                    "max_uses",
                    "temporary",
                    "unique",
                ),
            },
            kwargs,
        )

        data: payloads.InviteWithMetadata = await self.parent.request(
            route,
            reason=reason,
            data=post_data,
        )
        return Invite(state=self.parent, data=data)

    async def delete_channel_permission(
            self,
            channel_id: int,
            overwrite_id: int,
            *,
            reason: str | None = None) -> None:
        """
        Delete channel permission.
        """

        route = Route(
            "POST",
            "/channels/{channel_id}/permissions/{overwrite_id}",
            channel_id=channel_id,
            overwrite_id=overwrite_id,
        )
        await self.parent.request(
            route,
            reason=reason,
        )

    async def follow_announcement_channel(
            self,
            channel_id: int,
            webhook_channel_id: int) -> int:
        """
        Follow an announcement channel. Returns the created webhook ID.
        """

        route = Route(
            "POST",
            "/channels/{channel_id}/followers",
            channel_id=channel_id,
        )
        data = await self.parent.request(
            route,
            data={
                "webhook_channel_id": str(webhook_channel_id),
            }
        )
        return data["webhook_id"]

    async def trigger_typing_indicator(
            self,
            channel_id: int) -> None:
        """
        Trigger the typing indicator for the specified channel.
        """

        route = Route(
            "POST",
            "/channels/{channel_id}/typing",
            channel_id=channel_id,
        )
        await self.parent.request(route)

    async def get_pinned_messages(
            self,
            channel_id: int) -> list[Message]:
        """
        Return all of the pinned messages in the channel.
        """

        route = Route(
            "GET",
            "/channels/{channel_id}/pins",
            channel_id=channel_id,
        )
        data: list[payloads.Message] = await self.parent.request(route)
        return [
            Message(state=self.parent, data=d)
            for d in data
        ]

    async def pin_message(
            self,
            channel_id: int,
            message_id: int,
            *,
            reason: str | None = None) -> None:
        """
        Pin a message.
        """

        route = Route(
            "PUT",
            "/channels/{channel_id}/pins/{message_id}",
            channel_id=channel_id,
            message_id=message_id,
        )
        await self.parent.request(route, reason=reason)

    async def unpin_message(
            self,
            channel_id: int,
            message_id: int,
            *,
            reason: str | None = None) -> None:
        """
        Unpin a message.
        """

        route = Route(
            "DELETE",
            "/channels/{channel_id}/pins/{message_id}",
            channel_id=channel_id,
            message_id=message_id,
        )
        await self.parent.request(route, reason=reason)

    async def group_dm_add_recipient(
            self,
            channel_id: int,
            user_id: int) -> NoReturn:
        raise NotImplementedError()

    async def start_thread_from_message(
            self,
            channel_id: int,
            message_id: int,
            *,
            reason: str | None = None,
            **kwargs: dict[str, Any]) -> Channel:
        """
        Create a thread from a message.
        """

        route = Route(
            "POST",
            "/channels/{channel_id}/messages/{message_id}/threads",
            channel_id=channel_id,
            message_id=message_id,
        )

        post_data = self.parent._get_kwargs(
            {
                "type": (
                    "name",
                    "auto_archive_duration",
                    "rate_limit_per_user",
                ),
            },
            kwargs,
        )

        data: payloads.Channel = await self.parent.request(
            route,
            reason=reason,
            data=post_data,
        )
        return Channel(state=self.parent, data=data)

    async def start_thread_without_message(
            self,
            channel_id: int,
            *,
            reason: str | None = None,
            **kwargs: dict[str, Any]) -> Channel:
        """
        Create a thread not connected to an existing message.
        """

        route = Route(
            "POST",
            "/channels/{channel_id}/threads",
            channel_id=channel_id,
        )

        post_data = self.parent._get_kwargs(
            {
                "type": (
                    "name",
                    "auto_archive_duration",
                    "rate_limit_per_user",
                    "invitable",
                ),
                "enum": (
                    "type",
                )
            },
            kwargs,
        )

        data: payloads.Channel = await self.parent.request(
            route,
            reason=reason,
            data=post_data,
        )
        return Channel(state=self.parent, data=data)

    async def start_thread_in_forum_channel(
            self,
            channel_id: int,
            *,
            reason: str | None = None,
            **kwargs: dict[str, Any]) -> Channel:
        """
        Create a thread inside of a forum channel.
        """

        route = Route(
            "POST",
            "/channels/{channel_id}/threads",
            channel_id=channel_id,
        )

        message_data = self.parent._get_kwargs(
            {
                "type": (
                    "content",
                ),
                "object": (
                    "embeds",
                    "allowed_mentions",
                    "components",
                ),
                "flags": (
                    "flags",
                ),
                "snowflake": (
                    ("sticker_ids", "stickers",),
                ),
            },
            kwargs,
        )
        files = message_data.pop("files", [])

        post_data = self.parent._get_kwargs(
            {
                "type": (
                    "name",
                    "auto_archive_duration",
                    "rate_limit_per_user",
                ),
                "snowflake": (
                    "applied_tags",
                ),
            },
            kwargs,
        )
        post_data["message"] = message_data

        data: payloads.Channel = await self.parent.request(
            route,
            reason=reason,
            data=post_data,
            files=files,
        )
        return Channel(state=self.parent, data=data)

    async def add_thread_member(
            self,
            channel_id: int,
            user_id: int | Literal["@me"]) -> None:
        """
        Add a member to a thread.
        """

        route = Route(
            "PUT",
            "/channels/{channel_id}/thread-members/{user_id}",
            channel_id=channel_id,
            user_id=user_id,
        )
        await self.parent.request(route)

    async def remove_thread_member(
            self,
            channel_id: int,
            user_id: int | Literal["@me"]) -> None:
        """
        Remove another user from a thread.
        """

        route = Route(
            "DELETE",
            "/channels/{channel_id}/thread-members/{user_id}",
            channel_id=channel_id,
            user_id=user_id,
        )
        await self.parent.request(route)

    async def get_thread_member(
            self,
            channel_id: int,
            user_id: int,
            *,
            with_member: bool = False) -> ThreadMember:
        """
        Get a member in a thread.
        """

        route = Route(
            "GET",
            "/channels/{channel_id}/thread-members/{user_id}",
            channel_id=channel_id,
            user_id=user_id,
        )
        data: payloads.ThreadMember = await self.parent.request(
            route,
            params={"with_member": str(with_member)},
        )
        return ThreadMember(state=self.parent, data=data)

    async def list_thread_members(
            self,
            channel_id: int,
            *,
            with_member: bool = False,
            after: int = MISSING,
            limit: int = 100) -> list[ThreadMember]:
        """
        Get an array of thread members.
        """

        route = Route(
            "GET",
            "/channels/{channel_id}/thread-members",
            channel_id=channel_id,
        )

        params: dict[str, str | int] = {
            "with_member": str(with_member),
            "limit": limit,
        }
        if after is not MISSING:
            params["after"] = str(after)

        data: list[payloads.ThreadMember] = await self.parent.request(
            route,
            params=params,
        )
        return [
            ThreadMember(state=self.parent, data=d)
            for d in data
        ]

    async def list_public_archived_threads(
            self,
            channel_id: int,
            *,
            before: dt = MISSING,
            limit: int = MISSING) -> list[Channel]:
        """
        Get the archived threads inthe channel that are public.
        """

        route = Route(
            "GET",
            "/channels/{channel_id}/threads/archived/public",
            channel_id=channel_id,
        )

        params: dict[str, Any] = {}
        if before is not MISSING:
            params["before"] = before
        if limit is not MISSING:
            params["limit"] = limit

        data: dict[str, Any] = await self.parent.request(
            route,
            params=params,
        )
        return [
            Channel(state=self.parent, data=d)
            for d in data["threads"]
        ]  # pyright: ignore

    async def list_private_archived_threads(
            self,
            channel_id: int,
            *,
            before: dt = MISSING,
            limit: int = MISSING) -> list[Channel]:
        """
        Get the archived threads inthe channel that are private.
        """

        route = Route(
            "GET",
            "/channels/{channel_id}/threads/archived/private",
            channel_id=channel_id,
        )

        params: dict[str, Any] = {}
        if before is not MISSING:
            params["before"] = before
        if limit is not MISSING:
            params["limit"] = limit

        data: dict[str, Any] = await self.parent.request(
            route,
            params=params,
        )
        return [
            Channel(state=self.parent, data=d)
            for d in data["threads"]
        ]  # pyright: ignore

    async def list_joined_private_archived_threads(
            self,
            channel_id: int,
            *,
            before: dt = MISSING,
            limit: int = MISSING) -> list[Channel]:
        """
        Get the archived threads inthe channel that are private.
        """

        route = Route(
            "GET",
            "/channels/{channel_id}/users/@me/threads/archived/private",
            channel_id=channel_id,
        )

        params: dict[str, Any] = {}
        if before is not MISSING:
            params["before"] = before
        if limit is not MISSING:
            params["limit"] = limit

        data: dict[str, Any] = await self.parent.request(
            route,
            params=params,
        )
        return [
            Channel(state=self.parent, data=d)
            for d in data["threads"]
        ]
