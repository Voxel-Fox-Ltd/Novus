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

from typing import TYPE_CHECKING, Literal, Optional, TypedDict

if TYPE_CHECKING:
    from ._snowflake import Snowflake, Timestamp
    from .user import User, PartialUser
    from .channel import Channel, ChannelType
    from .embed import Embed
    from .application import Application
    from .interaction import MessageInteraction
    from .components import MessageComponent
    from .emoji import Emoji

__all__ = (
    'Attachment',
    'AllowedMentions',
    'ChannelMention',
    'Reaction',
    'MessageActivity',
    'MessageReference',
    'PartialSticker',
    'Message',
)


class _AttachmentOptional(TypedDict, total=False):
    description: str
    content_type: str
    height: str
    width: str
    ephemeral: str


class Attachment(_AttachmentOptional):
    id: Snowflake
    filename: str
    size: int
    url: str
    proxy_url: str


class AllowedMentions(TypedDict):
    parse: list[Literal["roles", "users", "everyone"]]
    roles: list[Snowflake]
    users: list[Snowflake]
    replied_user: bool


class ChannelMention(TypedDict):
    id: Snowflake
    guild_id: Snowflake
    type: ChannelType
    name: str


class Reaction(TypedDict):
    count: int
    me: bool
    emoji: Emoji


class _MessageActivityOptional(TypedDict, total=False):
    party_id: str  # Probably a snowflake, but typed as a string in the docs


class MessageActivity(_MessageActivityOptional):
    type: int


class MessageReference(TypedDict, total=False):
    message_id: Snowflake
    channel_id: Snowflake
    guild_id: Snowflake
    fail_if_not_exists: bool


class PartialSticker(TypedDict):  # Called "StickerItem" in the API
    id: Snowflake
    name: str
    format_type: str


class _MessageOptional(TypedDict, total=False):
    mention_channels: list[ChannelMention]
    reactions: list[Reaction]
    nonce: int | str
    webhook_id: Snowflake
    activity: MessageActivity
    application: Application
    application_id: Snowflake
    message_reference: MessageReference
    flags: int
    referenced_message: Optional[Message]
    interaction: MessageInteraction
    thread: Channel
    components: list[MessageComponent]
    sticker_items: list[PartialSticker]
    position: int


class Message(_MessageOptional):
    id: Snowflake
    channel_id: Snowflake
    author: User | PartialUser
    content: str
    timestamp: str
    edited_timestamp: Optional[Timestamp]
    tts: bool
    mention_everyone: bool
    mentions: list[User]
    mention_roles: list[Snowflake]
    attachments: list[Attachment]
    embeds: list[Embed]
    pinned: bool
    type: int
