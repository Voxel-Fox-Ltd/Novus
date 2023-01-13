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

from enum import Enum

from .helpers import enum_docstrings

__all__ = (
    'ApplicationFlags',
    'Locale',
)


@enum_docstrings.enum_docstrings
class ApplicationFlags(Enum):
    """
    The public flags for an application.

    Attributes
    ----------
    APPLICATION_COMMAND_BADGE
        Indicates if an app has registered global application commands.
    EMBEDDED
        Indicates if an app is embedded within the Discord client (currently
        unavailable publicly).
    GATEWAY_GUILD_MEMBERS
        Intent required for bots in 100 or more servers to receive
        member-related events like ``guild_member_add``.
    GATEWAY_GUILD_MEMBERS_LIMITED
        Intent required for bots in under 100 servers to receive member-related
        events like ``guild_member_add``.
    GATEWAY_MESSAGE_CONTENT
        Intent required for bots in 100 or more servers to receive message
        content.
    GATEWAY_MESSAGE_CONTENT_LIMITED
        Intent required for bots in under 100 servers to receive message
        content.
    GATEWAY_PRESENCE
        Intent required for bots in 100 or more servers to receive
        ``presence_update`` events.
    GATEWAY_PRESENCE_LIMITED
        Intent required for bots in under 100 servers to receive
        ``presence_update`` events.
    VERIFICATION_PENDING_GUILD_LIMIT
        Indicates unusual growth of an app that prevents verification.
    """

    GATEWAY_PRESENCE = 1 << 12
    GATEWAY_PRESENCE_LIMITED = 1 << 13
    GATEWAY_GUILD_MEMBERS = 1 << 14
    GATEWAY_GUILD_MEMBERS_LIMITED = 1 << 15
    VERIFICATION_PENDING_GUILD_LIMIT = 1 << 16
    EMBEDDED = 1 << 17
    GATEWAY_MESSAGE_CONTENT = 1 << 18
    GATEWAY_MESSAGE_CONTENT_LIMITED = 1 << 19
    APPLICATION_COMMAND_BADGE = 1 << 23


class Locale(Enum):
    INDONESIAN = "id"
    DANISH = "da"
    GERMAN = "de"
    UK_ENGLISH = "en-GB"
    US_ENGLISH = "en-US"
    SPANISH = "es-ES"
    FRENCH = "fr"
    CROATIAN = "hr"
    ITALIAN = "it"
    LITHUANIAN = "lt"
    HUNGARIAN = "hu"
    DUTCH = "nl"
    NORWEGIAN = "no"
    POLISH = "pl"
    BRAZILIAN_PORTUGUESE = "pt-BR"
    ROMANIAN = "ro"
    FINNISH = "fi"
    SWEDISH = "sv-SE"
    VIETNAMESE = "vi"
    TURKISH = "tr"
    CZECH = "cs"
    GREEK = "el"
    BULGARIAN = "bg"
    RUSSIAN = "ru"
    UKRAINIAN = "uk"
    HINDI = "hi"
    THAI = "th"
    CHINA_CHINESE = "zh-CN"
    JAPANESE = "ja"
    TAIWAN_CHINESE = "zh-TW"
    KOREAN = "ko"

    # Non-Discord aliases
    ENGLISH = "en-US"
    CHINESE = "zh-CN"
    PORTUGUESE = "pt-BR"
