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

from typing import TYPE_CHECKING, Any

from ...utils import MISSING, try_object

if TYPE_CHECKING:
    from ...api import HTTPConnection
    from .. import File, Webhook
    from ..abc import Snowflake, StateSnowflake


class WebhookAPIMixin:

    @classmethod
    async def fetch(
            cls,
            state: HTTPConnection,
            id: int,
            token: str | None = None) -> Webhook:
        """
        Get a webhook instance.

        Parameters
        ----------
        state : novus.HTTPConnection
            The API connection.
        id : int
            The ID of the webhook.
        token : str
            The webhook token.

        Returns
        -------
        novus.Webhook
            The webhook instance.
        """

        return await state.webhook.get_webhook(id, token=token)

    async def edit(
            self: StateSnowflake,
            *,
            reason: str | None = None,
            name: str = MISSING,
            avatar: File | None = MISSING,
            channel: int | Snowflake = MISSING) -> Webhook:
        """
        Edit the webhook.

        Parameters
        ----------
        name : str
            The new name of the webhook.
        avatar : novus.File | None
            The avatar of the webhook.
        channel : int | novus.abc.Snowflake
            The channel to move the webhook to.
        reason : str | None
            The reason shown in the audit log.

        Returns
        -------
        novus.Webhook
            The updated webhook instance.
        """

        update: dict[str, Any] = {}
        if name is not MISSING:
            update["name"] = name
        if avatar is not MISSING:
            update["avatar"] = None
            if avatar is not None:
                update["avatar"] = avatar.data
        if channel is not MISSING:
            update["channel"] = try_object(channel)

        return await self._state.webhook.modify_webhook(
            self.id,
            reason=reason,
            **update,
        )

    async def edit_with_token(
            self: StateSnowflake,
            *,
            reason: str | None = None,
            name: str = MISSING,
            avatar: File | None = MISSING) -> Webhook:
        """
        Edit the webhook. Requires the state to have a ``token`` attribute.

        Parameters
        ----------
        name : str
            The new name of the webhook.
        avatar : novus.File | None
            The avatar of the webhook.
        reason : str | None
            The reason shown in the audit log.

        Returns
        -------
        novus.Webhook
            The updated webhook instance.
        """

        update: dict[str, Any] = {}
        if name is not MISSING:
            update["name"] = name
        if avatar is not MISSING:
            update["avatar"] = None
            if avatar is not None:
                update["avatar"] = avatar.data

        return await self._state.webhook.modify_webhook(
            self.id,
            token=self.token,  # pyright: ignore
            reason=reason,
            **update,
        )
