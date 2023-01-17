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

from . import abc
from .guild import Guild, OauthGuild, GuildPreview
from .emoji import Emoji
from .role import Role
from .asset import Asset
from .welcome_screen import WelcomeScreen, WelcomeScreenChannel
from .sticker import Sticker

__all__ = (
    # abc
    'abc',

    # guild
    'Guild',
    'GuildPreview',
    'OauthGuild',

    # emoji
    'Emoji',

    # role
    'Role',

    # asset
    'Asset',

    # welcome_screen
    'WelcomeScreen',
    'WelcomeScreenChannel',

    # sticker
    'Sticker',
)
