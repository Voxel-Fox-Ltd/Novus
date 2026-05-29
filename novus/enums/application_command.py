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

from .utils import Enum

__all__ = (
    "ApplicationCommandType",
    "ApplicationOptionType",
    "ApplicationIntegrationType",
    "ApplicationCommandContext",
)


class ApplicationCommandType(Enum):
    """
    Types of application command.
    """

    CHAT_INPUT = 1
    USER = 2
    MESSAGE = 3


class ApplicationOptionType(Enum):
    """
    Types of option supported in application commands.
    """

    SUB_COMMAND = 1
    SUB_COMMAND_GROUP = 2
    STRING = 3
    INTEGER = 4
    BOOLEAN = 5
    USER = 6
    CHANNEL = 7
    ROLE = 8
    MENIONABLE = 9
    NUMBER = 10
    ATTACHMENT = 11


class ApplicationIntegrationType(Enum):
    """
    The places in which a given command can be installed. May also be referred to as an
    installation context.
    """

    GUILD_INSTALL = 0
    USER_INSTALL = 1


class ApplicationCommandContext(Enum):
    """
    The context where an interaction is used or where it was triggered from.
    """

    GUILD = 0
    BOT_DM = 1
    PRIVATE_CHANNEL = 2
