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
    'ComponentType',
    'ButtonStyle',
    'TextInputStyle',
)


class ComponentType(Enum):
    """All of the Discord component types."""

    ACTION_ROW = 1
    BUTTON = 2
    STRING_SELECT = 3
    TEXT_INPUT = 4
    USER_SELECT = 5
    ROLE_SELECT = 6
    MENTIONABLE_SELECT = 7
    CHANNEL_SELECT = 8

    SECTION = 9
    TEXT_DISPLAY = 10
    THUMBNAIL = 11
    MEDIA_GALLERY = 12
    FILE = 13
    SEPARATOR = 14
    CONTAINER = 17

    LABEL = 18
    FILE_UPLOAD = 19
    RADIO_GROUP = 21
    CHECKBOX_GROUP = 22


class ButtonStyle(Enum):
    """The different styles that can be applied to a button."""

    PRIMARY = 1
    BLURPLE = 1
    CTA = 1
    SECONDARY = 2
    GREY = 2
    GRAY = 2
    SUCCESS = 3
    GREEN = 3
    DANGER = 4
    RED = 4
    LINK = 5
    URL = 5


class TextInputStyle(Enum):
    """Different styles of text input component."""

    SHORT = 1
    PARAGRAPH = 2
    LONG = 2
