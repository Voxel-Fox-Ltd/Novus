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

from typing import TYPE_CHECKING, Any, NoReturn

from ..models import ApplicationCommand
from ._route import Route
from .webhook import WebhookHTTPConnection

if TYPE_CHECKING:
    from .. import WebhookMessage, payloads
    from ..enums import InteractionResponseType
    from ._http import HTTPConnection

__all__ = (
    'InteractionHTTPConnection',
)


class InteractionHTTPConnection:

    def __init__(self, parent: HTTPConnection):
        self.parent = parent

    async def get_global_application_commands(
            self,
            application_id: int,
            *,
            with_localizations: bool = False) -> list[ApplicationCommand]:
        """Get the global application commands."""

        params = {
            "with_localizations": str(with_localizations).lower()
        }
        route = Route(
            "GET",
            "/applications/{application_id}/commands",
            application_id=application_id,
        )
        data: list[payloads.ApplicationCommand] = await self.parent.request(
            route,
            params=params,
        )
        return [
            ApplicationCommand(state=self.parent, data=d)
            for d in data
        ]

    async def create_global_application_command(
            self,
            application_id: int,
            **kwargs: Any) -> ApplicationCommand:
        """Create a global application command."""

        route = Route(
            "POST",
            "/applications/{application_id}/commands",
            application_id=application_id,
        )

        post_data = self.parent._get_kwargs(
            {
                "type": (
                    "name",
                    "description",
                    "dm_permission",
                    "nsfw",
                ),
                "object": (
                    "name_localizations",
                    "description_localizations",
                    "options",
                ),
                "flags": (
                    "default_member_permissions",
                ),
                "enum": (
                    "type",
                ),
            },
            kwargs,
        )

        data: payloads.ApplicationCommand = await self.parent.request(
            route,
            data=post_data,
        )
        return ApplicationCommand(state=self.parent, data=data)

    async def get_global_application_command(
            self,
            application_id: int,
            command_id: int) -> ApplicationCommand:
        """Get a single global application command."""

        route = Route(
            "GET",
            "/applications/{application_id}/commands/{command_id}",
            application_id=application_id,
            command_id=command_id,
        )
        data: payloads.ApplicationCommand = await self.parent.request(
            route,
        )
        return ApplicationCommand(state=self.parent, data=data)

    async def edit_global_application_command(
            self,
            application_id: int,
            command_id: int,
            **kwargs: Any) -> ApplicationCommand:
        """Edit a global application command."""

        route = Route(
            "PATCH",
            "/applications/{application_id}/commands/{command_id}",
            application_id=application_id,
            command_id=command_id,
        )

        post_data = self.parent._get_kwargs(
            {
                "type": (
                    "name",
                    "description",
                    "dm_permission",
                    "nsfw",
                ),
                "object": (
                    "name_localizations",
                    "description_localizations",
                    "options",
                ),
                "flags": (
                    "default_member_permissions",
                ),
                "enum": (
                    "type",
                ),
            },
            kwargs,
        )

        data: payloads.ApplicationCommand = await self.parent.request(
            route,
            data=post_data,
        )
        return ApplicationCommand(state=self.parent, data=data)

    async def delete_global_application_command(
            self,
            application_id: int,
            command_id: int) -> None:
        """Delete a global application command."""

        route = Route(
            "DELETE",
            "/applications/{application_id}/commands/{command_id}",
            application_id=application_id,
            command_id=command_id,
        )
        await self.parent.request(route)

    async def bulk_overwrite_global_application_commands(
            self,
            application_id: int,
            commands: list[payloads.PartialApplicationCommand]) -> list[ApplicationCommand]:
        """Overwrite all current global application commands."""

        route = Route(
            "PUT",
            "/applications/{application_id}/commands",
            application_id=application_id,
        )

        post_data = [
            self.parent._get_kwargs(
                {
                    "type": (
                        "name",
                        "description",
                        "dm_permission",
                        "nsfw",
                    ),
                    "object": (
                        "name_localizations",
                        "description_localizations",
                        "options",
                    ),
                    "flags": (
                        "default_member_permissions",
                    ),
                    "enum": (
                        "type",
                    ),
                },
                d,
            )
            for d in commands
        ]

        data: list[payloads.ApplicationCommand] = await self.parent.request(
            route,
            data=post_data,
        )
        return [
            ApplicationCommand(state=self.parent, data=d)
            for d in data
        ]

    async def get_guild_application_commands(
            self,
            application_id: int,
            guild_id: int,
            *,
            with_localizations: bool = False) -> list[ApplicationCommand]:
        """Get all of the application commands in a guild."""

        params = {
            "with_localizations": str(with_localizations).lower()
        }
        route = Route(
            "GET",
            "/applications/{application_id}/guilds/{guild_id}/commands",
            application_id=application_id,
            guild_id=guild_id,
        )
        data: list[payloads.ApplicationCommand] = await self.parent.request(
            route,
            params=params,
        )
        return [
            ApplicationCommand(state=self.parent, data=d)
            for d in data
        ]

    async def create_guild_application_command(
            self,
            application_id: int,
            guild_id: int,
            **kwargs: Any) -> ApplicationCommand:
        """Create a guild application command."""

        route = Route(
            "POST",
            "/applications/{application_id}/guilds/{guild_id}/commands",
            application_id=application_id,
            guild_id=guild_id,
        )

        post_data = self.parent._get_kwargs(
            {
                "type": (
                    "name",
                    "description",
                    "dm_permission",
                    "nsfw",
                ),
                "object": (
                    "name_localizations",
                    "description_localizations",
                    "options",
                ),
                "flags": (
                    "default_member_permissions",
                ),
                "enum": (
                    "type",
                ),
            },
            kwargs,
        )

        data: payloads.ApplicationCommand = await self.parent.request(
            route,
            data=post_data,
        )
        return ApplicationCommand(state=self.parent, data=data)

    async def get_guild_application_command(
            self,
            application_id: int,
            guild_id: int,
            command_id: int) -> ApplicationCommand:
        """Get a single guild application command."""

        route = Route(
            "GET",
            "/applications/{application_id}/guilds/{guild_id}/commands/{command_id}",
            application_id=application_id,
            guild_id=guild_id,
            command_id=command_id,
        )
        data: payloads.ApplicationCommand = await self.parent.request(
            route,
        )
        return ApplicationCommand(state=self.parent, data=data)

    async def edit_guild_application_command(
            self,
            application_id: int,
            guild_id: int,
            command_id: int,
            **kwargs: Any) -> ApplicationCommand:
        """Edit a guild application command."""

        route = Route(
            "PATCH",
            "/applications/{application_id}/guilds/{guild_id}/commands/{command_id}",
            application_id=application_id,
            guild_id=guild_id,
            command_id=command_id,
        )

        post_data = self.parent._get_kwargs(
            {
                "type": (
                    "name",
                    "description",
                    "dm_permission",
                    "nsfw",
                ),
                "object": (
                    "name_localizations",
                    "description_localizations",
                    "options",
                ),
                "flags": (
                    "default_member_permissions",
                ),
                "enum": (
                    "type",
                ),
            },
            kwargs,
        )

        data: payloads.ApplicationCommand = await self.parent.request(
            route,
            data=post_data,
        )
        return ApplicationCommand(state=self.parent, data=data)

    async def delete_guild_application_command(
            self,
            application_id: int,
            guild_id: int,
            command_id: int) -> None:
        """Delete a guild application command."""

        route = Route(
            "DELETE",
            "/applications/{application_id}/guilds/{guild_id}/commands/{command_id}",
            application_id=application_id,
            guild_id=guild_id,
            command_id=command_id,
        )
        await self.parent.request(route)

    async def bulk_overwrite_guild_application_commands(
            self,
            application_id: int,
            guild_id: int,
            commands: list[payloads.PartialApplicationCommand]) -> list[ApplicationCommand]:
        """Overwrite all current guild application commands."""

        route = Route(
            "PUT",
            "/applications/{application_id}/guilds/{guild_id}/commands",
            application_id=application_id,
            guild_id=guild_id,
        )

        post_data = [
            self.parent._get_kwargs(
                {
                    "type": (
                        "name",
                        "description",
                        "dm_permission",
                        "nsfw",
                    ),
                    "object": (
                        "name_localizations",
                        "description_localizations",
                        "options",
                    ),
                    "flags": (
                        "default_member_permissions",
                    ),
                    "enum": (
                        "type",
                    ),
                },
                d,
            )
            for d in commands
        ]

        data: list[payloads.ApplicationCommand] = await self.parent.request(
            route,
            data=post_data,
        )
        return [
            ApplicationCommand(state=self.parent, data=d)
            for d in data
        ]

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

    async def get_original_interaction_response(
            self,
            application_id: int,
            interaction_token: str) -> WebhookMessage:
        """Get the original message associated with an interaction."""

        return await self.parent.webhook.get_webhook_message(
            application_id,
            interaction_token,
            "@original",  # pyright: ignore
        )

    async def edit_original_interaction_response(
            self,
            application_id: int,
            interaction_token: str,
            **kwargs: Any) -> WebhookMessage:
        """Edit the original interaction response."""

        return await self.parent.webhook.edit_webhook_message(
            application_id,
            interaction_token,
            "@original",  # pyright: ignore
            **kwargs,
        )

    async def delete_original_interaction_response(
            self,
            application_id: int,
            interaction_token: str) -> None:
        """Delete original resposne to an interaction."""

        await self.parent.webhook.delete_webhook_message(
            application_id,
            interaction_token,
            "@original",  # pyright: ignore
        )

    create_followup_message = WebhookHTTPConnection.execute_webhook
    get_followup_message = WebhookHTTPConnection.get_webhook_message
    edit_followup_message = WebhookHTTPConnection.edit_webhook_message
    delete_followup_message = WebhookHTTPConnection.delete_webhook_message
