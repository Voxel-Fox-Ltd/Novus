"""
The MIT License (MIT)

Copyright (c) 2015-2021 Rapptz

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from __future__ import annotations

from typing import Optional, TYPE_CHECKING, Dict, TypedDict, Union, List, Literal
from .snowflake import Snowflake
from .components import Component, SelectOption
from .embed import Embed
from .channel import ChannelType, Channel
from .member import Member
from .role import Role
from .user import User

if TYPE_CHECKING:
    from .message import AllowedMentions, Message


ApplicationCommandType = Literal[1, 2, 3]


class ApplicationCommand(TypedDict):
    id: Optional[Snowflake]
    application_id: Optional[Snowflake]
    name: str
    description: str
    type: ApplicationCommandType
    options: Optional[List[ApplicationCommandOption]]
    name_localizations: Optional[Dict[str, str]]
    description_localizations: Optional[Dict[str, str]]
    default_member_permissions: Optional[int]
    dm_permissions: bool


ApplicationCommandOptionType = Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]


class ApplicationCommandOption(TypedDict):
    type: ApplicationCommandOptionType
    name: str
    description: str
    required: bool
    choices: Optional[List[ApplicationCommandOptionChoice]]
    options: Optional[List[ApplicationCommandOption]]


class ApplicationCommandOptionChoice(TypedDict):
    name: str
    name_localizations: Optional[Dict[str, str]]
    value: Union[str, int]


ApplicationCommandPermissionType = Literal[1, 2]


class ApplicationCommandPermissions(TypedDict):
    id: Snowflake
    type: ApplicationCommandPermissionType
    permission: bool


class BaseGuildApplicationCommandPermissions(TypedDict):
    permissions: List[ApplicationCommandPermissions]


class PartialGuildApplicationCommandPermissions(BaseGuildApplicationCommandPermissions):
    id: Snowflake


class GuildApplicationCommandPermissions(PartialGuildApplicationCommandPermissions):
    application_id: Snowflake
    guild_id: Snowflake


InteractionType = Literal[1, 2, 3]


class _ApplicationCommandInteractionDataOption(TypedDict):
    name: str


class _ApplicationCommandInteractionDataOptionSubcommand(_ApplicationCommandInteractionDataOption):
    type: Literal[1, 2]
    options: List[ApplicationCommandInteractionDataOption]


class _ApplicationCommandInteractionDataOptionString(_ApplicationCommandInteractionDataOption):
    type: Literal[3]
    value: str


class _ApplicationCommandInteractionDataOptionInteger(_ApplicationCommandInteractionDataOption):
    type: Literal[4]
    value: int


class _ApplicationCommandInteractionDataOptionBoolean(_ApplicationCommandInteractionDataOption):
    type: Literal[5]
    value: bool


class _ApplicationCommandInteractionDataOptionSnowflake(_ApplicationCommandInteractionDataOption):
    type: Literal[6, 7, 8, 9]
    value: Snowflake


class _ApplicationCommandInteractionDataOptionNumber(_ApplicationCommandInteractionDataOption):
    type: Literal[10]
    value: float


ApplicationCommandInteractionDataOption = Union[
    _ApplicationCommandInteractionDataOptionString,
    _ApplicationCommandInteractionDataOptionInteger,
    _ApplicationCommandInteractionDataOptionSubcommand,
    _ApplicationCommandInteractionDataOptionBoolean,
    _ApplicationCommandInteractionDataOptionSnowflake,
    _ApplicationCommandInteractionDataOptionNumber,
]


class ApplicationCommandResolvedPartialChannel(TypedDict):
    id: Snowflake
    type: ChannelType
    permissions: str
    name: str


class ApplicationCommandInteractionDataResolved(TypedDict, total=False):
    users: Dict[Snowflake, User]
    members: Dict[Snowflake, Member]
    roles: Dict[Snowflake, Role]
    channels: Dict[Snowflake, ApplicationCommandResolvedPartialChannel]


class ApplicationCommandInteractionDataOption(TypedDict):
    name: str
    type: int
    value: Optional[str]
    options: List[ApplicationCommandInteractionDataOption]
    focused: Optional[bool]
    components: Optional[List[ApplicationCommandInteractionDataOption]]


class _InteractionDataOptional(TypedDict, total=False):
    resolved: Dict[str, dict]
    options: List[ApplicationCommandInteractionDataOption]
    custom_id: str
    component_type: int
    values: List[str]
    target_id: Snowflake
    components: List[ApplicationCommandInteractionDataOption]
    app_permissions: str


class InteractionData(_InteractionDataOptional):
    id: Snowflake
    name: str
    type: ApplicationCommandType


class InteractionResolved(TypedDict):
    users: List[Union[User, Member]]
    members: List[Member]
    roles: List[Role]
    channels: List[Channel]
    messages: List[Message]


class _InteractionOptional(TypedDict, total=False):
    data: InteractionData
    guild_id: Snowflake
    channel_id: Snowflake
    member: Member
    user: User
    message: Message
    guild_locale: str


class Interaction(_InteractionOptional):
    id: Snowflake
    application_id: Snowflake
    type: InteractionType
    token: str
    version: int
    resolved: InteractionResolved
    locale: str
    app_permissions: str


class InteractionApplicationCommandCallbackData(TypedDict, total=False):
    tts: bool
    content: str
    embeds: List[Embed]
    allowed_mentions: AllowedMentions
    flags: int
    components: List[Component]


InteractionResponseType = Literal[1, 4, 5, 6, 7]


class _InteractionResponseOptional(TypedDict, total=False):
    data: InteractionApplicationCommandCallbackData


class InteractionResponse(_InteractionResponseOptional):
    type: InteractionResponseType


class MessageInteraction(TypedDict):
    id: Snowflake
    type: InteractionType
    name: str
    user: User


class _EditApplicationCommandOptional(TypedDict, total=False):
    description: str
    options: Optional[List[ApplicationCommandOption]]
    type: ApplicationCommandType


class EditApplicationCommand(_EditApplicationCommandOptional):
    name: str
    default_permission: bool
