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

from __future__ import annotations

from typing import TYPE_CHECKING

from ..utils import cached_slot_property, try_snowflake
from .api_mixins.webhook import WebhookAPIMixin
from .asset import Asset

if TYPE_CHECKING:
    from ..api import HTTPConnection
    from ..payloads import Webhook as WebhookPayload

__all__ = (
    'Webhook',
)


class Webhook(WebhookAPIMixin):
    """
    A model for a webhook instance.

    Attributes
    ----------
    id: int
        The ID of the webhook.
    guild_id: int | None
        The guild ID this webhook is for, if any.
    channel_id: int | None
        The channel ID this webhook is for, if any.
    name: str | None
        The default of the webhook.
    avatar_hash: str | None
        The hash associated with the user avatar.
    avatar: novus.Asset | None
        The avatar asset associated with the hash.
    token: str | None
        The token of the webhook.
    """

    __slots__ = (
        '_state',
        'id',
        'guild_id',
        'channel_id',
        'name',
        'avatar_hash',
        'token',
        '_cs_avatar',
    )

    def __init__(self, *, state: HTTPConnection, data: WebhookPayload):
        self._state = state
        self.id: int = try_snowflake(data['id'])
        self.guild_id: int | None = try_snowflake(data.get('guild_id'))
        self.channel_id: int | None = try_snowflake(data['channel_id'])
        self.name: str | None = data['name']
        self.avatar_hash: str | None = data['avatar']
        self.token: str | None = data.get('token')

    @cached_slot_property('_cs_avatar')
    def avatar(self) -> Asset:
        return Asset.from_user_avatar(self)
