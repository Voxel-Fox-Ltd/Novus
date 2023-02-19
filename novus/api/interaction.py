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

from typing import TYPE_CHECKING, Any, NoReturn

from ._route import Route
from .webhook import WebhookHTTPConnection

if TYPE_CHECKING:
    from ..enums import InteractionResponseType
    from ._http import HTTPConnection

__all__ = (
    'InteractionHTTPConnection',
)


class InteractionHTTPConnection:

    def __init__(self, parent: HTTPConnection):
        self.parent = parent

    async def get_global_application_commands(self) -> NoReturn:
        raise NotImplementedError()

    async def create_global_application_command(self) -> NoReturn:
        raise NotImplementedError()

    async def edit_global_application_command(self) -> NoReturn:
        raise NotImplementedError()

    async def delete_global_application_command(self) -> NoReturn:
        raise NotImplementedError()

    async def bulk_overwrite_global_application_commands(self) -> NoReturn:
        raise NotImplementedError()

    async def get_guild_application_commands(self) -> NoReturn:
        raise NotImplementedError()

    async def create_guild_application_command(self) -> NoReturn:
        raise NotImplementedError()

    async def get_guild_application_command(self) -> NoReturn:
        raise NotImplementedError()

    async def edit_guild_application_command(self) -> NoReturn:
        raise NotImplementedError()

    async def delete_guild_application_command(self) -> NoReturn:
        raise NotImplementedError()

    async def bulk_overwrite_guild_application_commands(self) -> NoReturn:
        raise NotImplementedError()

    async def get_application_command_permissions(self) -> NoReturn:
        raise NotImplementedError()

    async def edit_application_command_permissions(self) -> NoReturn:
        raise NotImplementedError()

    async def create_interaction_response(
            self,
            interaction_id: int | str,
            token: str,
            type: InteractionResponseType,
            interaction_data: dict[str, Any] | None = None) -> None:
        """
        Respond to an interaction.
        """

        route = Route(
            "POST",
            "/interactions/{interaction_id}/{token}/callback",
            interaction_id=interaction_id,
            token=token,
        )

        interaction_data = self.parent._get_kwargs(
            {
                "type": (
                    "content",
                    "tts",
                    "custom_id",
                    "title",
                ),
                "object": (
                    "embeds",
                    "allowed_mentions",
                    "components",
                    "choices"
                ),
                "flags": (
                    "flags",
                )
            },
            interaction_data or {},
        )
        files = interaction_data.pop("files", [])

        post_data = {"type": type.value}
        if interaction_data:
            post_data["data"] = interaction_data

        await self.parent.request(
            route,
            data=post_data,
            files=files,
        )

    async def get_original_interaction_response(self) -> NoReturn:
        raise NotImplementedError()

    async def edit_original_interaction_response(self) -> NoReturn:
        raise NotImplementedError()

    async def delete_original_interaction_response(self) -> NoReturn:
        raise NotImplementedError()

    create_followup_message = WebhookHTTPConnection.execute_webhook
    get_followup_message = WebhookHTTPConnection.get_webhook_message
    edit_followup_message = WebhookHTTPConnection.edit_webhook_message
    delete_followup_message = WebhookHTTPConnection.delete_webhook_message
