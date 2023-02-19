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

__all__ = (
    'ComponentType',
    'ButtonStyle',
    'TextInputStyle',
)


class ComponentType(Enum):
    """
    All of the Discord component types.
    """

    action_row = 1
    button = 2
    string_select = 3
    text_input = 4
    user_select = 5
    role_select = 6
    mentionable_select = 7
    channel_select = 8


class ButtonStyle(Enum):
    """
    The different styles that can be applied to a button.
    """

    primary = 1
    blurple = 1
    cta = 1
    secondary = 2
    grey = 2
    gray = 2
    success = 3
    green = 3
    danger = 4
    red = 4
    link = 5
    url = 5


class TextInputStyle(Enum):
    """
    Different styles of text input component.
    """

    short = 1
    paragraph = 2
    long = 2
