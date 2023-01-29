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

from .utils import Enum

__all__ = ("Locale",)


class Locale(Enum):
    indonesian = "id"
    danish = "da"
    german = "de"
    uk_english = "en-GB"
    us_english = "en-US"
    spanish = "es-ES"
    french = "fr"
    croatian = "hr"
    italian = "it"
    lithuanian = "lt"
    hungarian = "hu"
    dutch = "nl"
    norwegian = "no"
    polish = "pl"
    brazilian_portuguese = "pt-BR"
    romanian = "ro"
    finnish = "fi"
    swedish = "sv-SE"
    vietnamese = "vi"
    turkish = "tr"
    czech = "cs"
    greek = "el"
    bulgarian = "bg"
    russian = "ru"
    ukrainian = "uk"
    hindi = "hi"
    thai = "th"
    china_chinese = "zh-CN"
    japanese = "ja"
    taiwan_chinese = "zh-TW"
    korean = "ko"

    # Non-Discord aliases
    english = "en-US"
    chinese = "zh-CN"
    portuguese = "pt-BR"
