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

from typing import TYPE_CHECKING, Any, overload

from ..models import Webhook, WebhookMessage
from ._route import Route

if TYPE_CHECKING:
    from .. import payloads
    from ._http import HTTPConnection

__all__ = (
    'WebhookHTTPConnection',
)


class WebhookHTTPConnection:

    def __init__(self, parent: HTTPConnection):
        self.parent = parent

    async def create_webhook(
            self,
            channel_id: int,
            *,
            reason: str | None = None,
            **kwargs: dict[str, Any]) -> Webhook:
        """
        Create a webhook instance.
        """

        post_data = self.parent._get_kwargs(
            {
                "type": (
                    "name",
                ),
                "image": (
                    "avatar",
                ),
            },
            kwargs,
        )
        route = Route(
            "POST",
            "/channels/{channel_id}/webhooks",
            channel_id=channel_id,
        )
        data: payloads.Webhook = await self.parent.request(
            route,
            reason=reason,
            data=post_data,
        )
        return Webhook(state=self.parent, data=data)

    async def get_channel_webhooks(
            self,
            channel_id: int) -> list[Webhook]:
        """
        Get all webhooks associated with a channel.
        """

        route = Route(
            "GET",
            "/channels/{channel_id}/webhooks",
            channel_id=channel_id,
        )
        data: list[payloads.Webhook] = await self.parent.request(route)
        return [
            Webhook(state=self.parent, data=d)
            for d in data
        ]

    async def get_guild_webhooks(
            self,
            guild_id: int) -> list[Webhook]:
        """
        Get all webhooks associated with a guild.
        """

        route = Route(
            "GET",
            "/guild/{guild_id}/webhooks",
            guild_id=guild_id,
        )
        data: list[payloads.Webhook] = await self.parent.request(route)
        return [
            Webhook(state=self.parent, data=d)
            for d in data
        ]

    async def get_webhook(
            self,
            webhook_id: int,
            *,
            token: str | None = None) -> Webhook:
        """
        Get a webhook via its ID.
        """

        route = Route(
            "GET",
            "/webhooks/{webhook_id}",
            webhook_id=webhook_id,
        )
        data: payloads.Webhook = await self.parent.request(route)
        v = Webhook(state=self.parent, data=data)
        if token:
            v.token = token
        return v

    async def modify_webhook(
            self,
            webhook_id: int,
            *,
            reason: str | None = None,
            token: str | None = None,
            **kwargs: dict[str, Any]) -> Webhook:
        """
        Modify a webhook.
        """

        if token:
            route = Route(
                "PATCH",
                "/webhooks/{webhook_id}/{token}",
                webhook_id=webhook_id,
                token=token,
            )
        else:
            route = Route(
                "PATCH",
                "/webhooks/{webhook_id}",
                webhook_id=webhook_id,
            )

        post_data = self.parent._get_kwargs(
            {
                "type": (
                    "name",
                ),
                "image": (
                    "avatar",
                ),
                "snowflake": (
                    ("channel_id", "channel",),
                ),
            },
            kwargs,
        )

        data: payloads.Webhook = await self.parent.request(
            route,
            reason=reason,
            data=post_data,
        )
        v = Webhook(state=self.parent, data=data)
        if token:
            v.token = token
        return v

    async def delete_webhook(
            self,
            webhook_id: int,
            *,
            reason: str | None = None,
            token: str | None = None) -> None:
        """
        Delete a webhook.
        """

        if token:
            route = Route(
                "DELETE",
                "/webhooks/{webhook_id}/{token}",
                webhook_id=webhook_id,
                token=token,
            )
        else:
            route = Route(
                "DELETE",
                "/webhooks/{webhook_id}",
                webhook_id=webhook_id,
            )
        await self.parent.request(route, reason=reason)

    @overload
    async def execute_webhook(
            self,
            webhook_id: int,
            token: str,
            *,
            wait=True,
            thread_id: int | None,
            **kwargs: dict[str, Any]) -> WebhookMessage:
        ...

    @overload
    async def execute_webhook(
            self,
            webhook_id: int,
            token: str,
            *,
            wait=False,
            thread_id: int | None,
            **kwargs: dict[str, Any]) -> None:
        ...

    async def execute_webhook(
            self,
            webhook_id: int,
            token: str,
            *,
            wait: bool = False,
            thread_id: int | None = None,
            **kwargs: dict[str, Any]) -> WebhookMessage | None:
        """
        Create a webhook message.
        """

        route = Route(
            "POST",
            "/webhooks/{webhook_id}/{token}",
            webhook_id=webhook_id,
            token=token,
        )

        post_data = self.parent._get_kwargs(
            {
                "type": (
                    "content",
                    "username",
                    "avatar_url",
                    "tts",
                    "thread_name",
                ),
                "object": (
                    "embeds",
                    "allowed_mentions",
                    "components",
                ),
                "flags": (
                    "flags",
                )
            },
            kwargs,
        )
        files = post_data.pop("files", [])

        params: dict[str, str] = {}
        if wait is not None:
            params["wait"] = "true" if wait else "false"
        if thread_id is not None:
            params["thread_id"] = str(thread_id)

        data: payloads.Message | None = await self.parent.request(
            route,
            params=params,
            data=post_data,
            files=files,
        )
        if data:
            webhook = Webhook.partial(id=webhook_id, token=token, state=self.parent)
            return WebhookMessage(state=self.parent, data=data, webhook=webhook)
        return None

    async def get_webhook_message(
            self,
            webhook_id: int,
            token: str,
            message_id: int,
            *,
            thread_id: int | None = None) -> WebhookMessage:
        """
        Get a webhook message.
        """

        route = Route(
            "GET",
            "/webhooks/{webhook_id}/{token}/messages/{message_id}",
            webhook_id=webhook_id,
            token=token,
            message_id=message_id,
        )
        params: dict[str, str] = {}
        if thread_id:
            params["thread_id"] = str(thread_id)
        data: payloads.Message = await self.parent.request(
            route,
            params=params,
        )
        webhook = Webhook.partial(id=webhook_id, token=token, state=self.parent)
        return WebhookMessage(state=self.parent, data=data, webhook=webhook)

    async def edit_webhook_message(
            self,
            webhook_id: int,
            token: str,
            message_id: int,
            *,
            thread_id: int | None = None,
            **kwargs: dict[str, Any]) -> WebhookMessage:
        """
        Edit a webhook message.
        """

        route = Route(
            "PATCH",
            "/webhooks/{webhook_id}/{token}/messages/{message_id}",
            webhook_id=webhook_id,
            token=token,
            message_id=message_id,
        )

        post_data = self.parent._get_kwargs(
            {
                "type": (
                    "content",
                    "username",
                    "avatar_url",
                    "tts",
                    "thread_name",
                ),
                "object": (
                    "embeds",
                    "allowed_mentions",
                    "components",
                ),
                "flags": (
                    "flags",
                )
            },
            kwargs,
        )
        files = post_data.pop("files", [])

        params: dict[str, str] = {}
        if thread_id is not None:
            params["thread_id"] = str(thread_id)

        data: payloads.Message = await self.parent.request(
            route,
            params=params,
            data=post_data,
            files=files,
        )
        webhook = Webhook.partial(id=webhook_id, token=token, state=self.parent)
        return WebhookMessage(state=self.parent, data=data, webhook=webhook)

    async def delete_webhook_message(
            self,
            webhook_id: int,
            token: str,
            message_id: int,
            *,
            thread_id: int | None = None) -> None:
        """
        Delete a webhook message.
        """

        route = Route(
            "DELETE",
            "/webhooks/{webhook_id}/{token}/messages/{message_id}",
            webhook_id=webhook_id,
            token=token,
            message_id=message_id,
        )
        params: dict[str, str] = {}
        if thread_id:
            params["thread_id"] = str(thread_id)
        await self.parent.request(
            route,
            params=params,
        )
