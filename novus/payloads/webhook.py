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

from typing import TYPE_CHECKING, Literal, Optional, TypedDict

if TYPE_CHECKING:
    from ._util import Snowflake
    from .user import User
    from .guild import Guild
    from .channel import Channel

__all__ = (
    'Webhook',
)


class _WebhookOptional(TypedDict, total=False):
    guild_id: Optional[Snowflake]
    user: User  # Created by
    token: str
    source_guild: Guild
    source_channel: Channel
    url: str


class Webhook(_WebhookOptional):
    id: Snowflake
    type: Literal[1, 2, 3]
    channel_id: Optional[Snowflake]
    name: Optional[str]
    avatar: Optional[str]
    application_id: Optional[Snowflake]
