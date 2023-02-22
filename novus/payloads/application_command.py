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

from typing import TYPE_CHECKING, Literal, TypedDict

from typing_extensions import NotRequired

if TYPE_CHECKING:
    from . import ChannelType, Locale, Snowflake

__all__ = (
    'ApplicationCommandType',
    'ApplicationCommandOptionType',
    'ApplicationCommandChoice',
    'ApplicationCommandOption',
    'PartialApplicationCommand',
    'ApplicationCommand',
)


ApplicationCommandType = Literal[
    1,  # CHAT_INPUT
    2,  # USER
    3,  # MESSAGE
]


ApplicationCommandOptionType = Literal[
    1,  # SUB_COMMAND
    2,  # SUB_COMMAND_GROUP
    3,  # STRING
    4,  # INTEGER
    5,  # BOOLEAN
    6,  # USER
    7,  # CHANNEL
    8,  # ROLE
    9,  # MENTIONABLE
    10,  # NUMBER (double)
    11,  # ATTACHMENT
]


class ApplicationCommandChoice(TypedDict):
    name: str
    name_localizations: NotRequired[dict[Locale, str] | None]
    value: str | int | float


class ApplicationCommandOption(TypedDict):
    type: ApplicationCommandOptionType
    name: str
    name_localizations: NotRequired[dict[Locale, str] | None]
    description: str
    description_localizations: NotRequired[dict[Locale, str] | None]
    required: NotRequired[bool]
    choices: NotRequired[list[ApplicationCommandChoice]]
    options: NotRequired[list[ApplicationCommandOption]]
    channel_types: NotRequired[list[ChannelType]]
    min_value: NotRequired[int | float]
    max_value: NotRequired[int | float]
    min_length: NotRequired[int]
    max_length: NotRequired[int]
    autocomplete: NotRequired[bool]


class PartialApplicationCommand(TypedDict):
    type: NotRequired[ApplicationCommandType]
    name: str
    name_localizations: NotRequired[dict[Locale, str] | None]
    description: str
    description_localizations: NotRequired[dict[Locale, str] | None]
    options: NotRequired[list[ApplicationCommandOption]]
    default_member_permissions: str | None
    dm_permission: NotRequired[bool]
    nsfw: NotRequired[bool]


class ApplicationCommand(PartialApplicationCommand):
    id: Snowflake
    application_id: Snowflake
    guild_id: NotRequired[Snowflake]
    version: Snowflake
