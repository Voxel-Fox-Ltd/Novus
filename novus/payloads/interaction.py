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

from typing import TYPE_CHECKING, Any, Literal, TypedDict, List

from typing_extensions import NotRequired

if TYPE_CHECKING:
    from . import (
        ActionRow,
        ApplicationCommandOptionType,
        Attachment,
        Channel,
        Entitlement,
        Guild,
        GuildMember,
        Message,
        Role,
        SelectOption,
        User,
    )
    from ._util import Snowflake

__all__ = (
    'CommandType',
    'InteractionResolved',
    'InteractionDataOption',
    'ApplicationComandData',
    'MessageComponentData',
    'ModalSubmitData',
    'Interaction',
)


CommandType = Literal[
    1,  # CHAT_INPUT
    2,  # USER
    3,  # MESSAGE
]


class InteractionResolved(TypedDict):
    users: NotRequired[dict[Snowflake, User]]
    members: NotRequired[dict[Snowflake, GuildMember]]
    roles: NotRequired[dict[Snowflake, Role]]
    channels: NotRequired[dict[Snowflake, Channel]]
    messages: NotRequired[dict[Snowflake, Message]]
    attachments: NotRequired[dict[Snowflake, Attachment]]


class InteractionDataOption(TypedDict):
    name: str
    type: ApplicationCommandOptionType
    value: NotRequired[str | int | bool]
    options: NotRequired[list[InteractionDataOption]]
    focused: NotRequired[bool]


class ApplicationComandData(TypedDict):
    id: Snowflake
    name: str
    type: CommandType
    resolved: NotRequired[InteractionResolved]
    options: NotRequired[list[InteractionDataOption]]
    guild_id: NotRequired[Snowflake]
    target_id: NotRequired[Snowflake]


class MessageComponentData(TypedDict):
    custom_id: str
    component_type: int
    values: NotRequired[list[SelectOption]]


class ModalSubmitData(TypedDict):
    custom_id: str
    components: list[ActionRow]


class Interaction(TypedDict):
    id: Snowflake
    application_id: Snowflake
    type: int
    data: ApplicationComandData | MessageComponentData | ModalSubmitData
    guild: NotRequired[Guild]
    guild_id: NotRequired[Snowflake]
    channel_id: Snowflake
    member: NotRequired[GuildMember]
    user: NotRequired[User]
    token: str
    version: Literal[1]
    message: NotRequired[Message]
    app_permissions: NotRequired[str]
    locale: str
    guild_locale: NotRequired[str]
    entitlements: List[Entitlement]
    authorizing_integration_owners: dict[str, Any]
    context: NotRequired[int]
