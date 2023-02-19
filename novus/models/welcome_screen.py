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

from typing import TYPE_CHECKING

from ..utils import try_snowflake

if TYPE_CHECKING:
    from ..payloads import GuildWelcomeScreen as WelcomeScreenPayload
    from ..payloads import GuildWelcomeScreenChannel as WelcomeScreenChannelPayload

__all__ = (
    'WelcomeScreenChannel',
    'WelcomeScreen',
)


class WelcomeScreenChannel:
    """
    A channel shown in a guild's welcome screen.
    """

    __slots__ = (
        'channel_id',
        'description',
        'emoji_id',
        'emoji_name',
    )

    def __init__(self, *, data: WelcomeScreenChannelPayload):
        self.channel_id = try_snowflake(data['channel_id'])
        self.description = data['description']
        self.emoji_id = try_snowflake(data.get('emoji_id'))
        self.emoji_name = data.get('emoji_name')


class WelcomeScreen:
    """
    A welcome screen for a guild.
    """

    __slots__ = (
        'description',
        'welcome_channels',
    )

    def __init__(self, *, data: WelcomeScreenPayload):
        self.description = data.get('description')
        self.welcome_channels = [
            WelcomeScreenChannel(data=i)
            for i in data['welcome_channels']
        ]
