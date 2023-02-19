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

import re
from typing import TYPE_CHECKING

from ..utils import cached_slot_property, generate_repr, try_snowflake
from .api_mixins.webhook import InteractionWebhookAPIMixin, WebhookAPIMixin
from .asset import Asset

if TYPE_CHECKING:
    from ..api import HTTPConnection
    from ..payloads import Webhook as WebhookPayload

__all__ = (
    'Webhook',
    'InteractionWebhook',
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

    WEBHOOK_REGEX = re.compile(
        r"discord\.com\/api\/webhooks\/"  # base and path
        + r"(?P<id>\d{16,23})"  # webhook ID
        + r"(?:\/(?P<token>[a-zA-Z0-9\-_]{0,80}))?"  # webhook token
    )

    __slots__ = (
        'state',
        'id',
        'guild_id',
        'channel_id',
        'name',
        'avatar_hash',
        'token',
        '_cs_avatar',
    )

    def __init__(self, *, state: HTTPConnection, data: WebhookPayload):
        self.state = state
        self.id: int = try_snowflake(data['id'])
        self.guild_id: int | None = try_snowflake(data.get('guild_id'))
        self.channel_id: int | None = try_snowflake(data.get('channel_id'))
        self.name: str | None = data.get('name')
        self.avatar_hash: str | None = data.get('avatar')
        self.token: str | None = data.get('token')

    __repr__ = generate_repr(("id",))

    @cached_slot_property('_cs_avatar')
    def avatar(self) -> Asset:
        return Asset.from_user_avatar(self)

    @classmethod
    def partial(
            cls,
            id: str | int,
            token: str | None = None,
            *,
            state: HTTPConnection | None = None) -> Webhook:
        """
        Create a partial webhook state, allowing you to run webhook API methods.

        Parameters
        ----------
        id : str | int
            The ID of the webhook.
        token : str | None
            The auth token for the webhook.
        state : HTTPConnection | None
            The API connection, if one is made. Passing this enables API
            methods to be run on returned objects (eg a `Message.guild` from a
            message returned by executing a webhook).
            If no state is provided, one will be created for you to enable the
            sending of messages.

        Returns
        -------
        novus.Webhook
            The created webhook instance.
        """

        from ..api import HTTPConnection  # Circular imports my beloved
        data = {
            "id": id,
            "token": token,
        }
        return cls(
            state=state or HTTPConnection(),
            data=data,  # pyright: ignore
        )

    @classmethod
    def from_url(cls, url: str, state: HTTPConnection | None = None) -> Webhook:
        """
        Get a webhook object from a valid Discord URL. This won't get attributes
        like the name or channel ID, but will allow you to run API methods with
        the object.

        Parameters
        ----------
        url : str
            The URL of the webhook.
        state : HTTPConnection | None
            The API connection, if one is made. Passing this enables API
            methods to be run on returned objects (eg a `Message.guild` from a
            message returned by executing a webhook).
            If no state is provided, one will be created for you to enable the
            sending of messages.

        Returns
        -------
        novus.Webhook
            The created webhook instance.

        Raises
        ------
        ValueError
            The provided URL is not valid.
        """

        match = cls.WEBHOOK_REGEX.search(url)
        if match is None:
            raise ValueError("Invalid webhook URL")
        return cls.partial(
            id=match.group("id"),
            token=match.group("token"),
            state=state,
        )


class InteractionWebhook(Webhook, InteractionWebhookAPIMixin):
    pass
