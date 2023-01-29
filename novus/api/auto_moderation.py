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

from ..models import AutoModerationRule
from ._route import Route

if TYPE_CHECKING:
    from .. import payloads
    from ._http import HTTPConnection

__all__ = (
    'AutoModerationHTTPConnection',
)


class AutoModerationHTTPConnection:

    def __init__(self, parent: HTTPConnection):
        self.parent = parent

    async def list_auto_moderation_rules_for_guild(
            self,
            guild_id: int) -> list[AutoModerationRule]:
        """
        Get a list of automoderator rules for the guild.
        """

        route = Route(
            "GET",
            "/guilds/{guild_id}/auto-moderation/rules",
            guild_id=guild_id,
        )
        data: list[payloads.AutoModerationRule] = await self.parent.request(route)
        return [
            AutoModerationRule(state=self.parent, data=d)
            for d in data
        ]

    async def get_auto_moderation_rule(
            self,
            guild_id: int,
            rule_id: int) -> AutoModerationRule:
        """
        Get a specific automoderator rule for the guild.
        """

        route = Route(
            "GET",
            "/guilds/{guild_id}/auto-moderation/rules/{rule_id}",
            guild_id=guild_id,
            rule_id=rule_id,
        )
        data: payloads.AutoModerationRule = await self.parent.request(route)
        return AutoModerationRule(state=self.parent, data=data)

    async def create_auto_moderation_rule(
            self,
            guild_id: int,
            *,
            reason: str | None = None,
            **kwargs: dict[str, Any]) -> AutoModerationRule:
        """
        Create an automoderation rule.
        """

        post_data = self.parent._get_kwargs(
            {
                "type": (
                    "name",
                    "enabled",
                    "trigger_metadata",
                ),
                "snowflake": (
                    "exempt_roles",
                    "exempt_channels",
                ),
                "enum": (
                    "event_type",
                    "trigger_type",
                ),
                "object": (
                    "actions",
                    "trigger_metadata",
                ),
            },
            kwargs,
        )
        route = Route(
            "POST",
            "/guilds/{guild_id}/auto-moderation/rules",
            guild_id=guild_id,
        )
        data: payloads.AutoModerationRule = await self.parent.request(
            route,
            reason=reason,
            data=post_data,
        )
        return AutoModerationRule(
            state=self.parent,
            data=data,
        )

    async def modify_auto_moderation_rule(
            self,
            guild_id: int,
            rule_id: int,
            *,
            reason: str | None = None,
            **kwargs: dict[str, Any]) -> AutoModerationRule:
        """
        Edit an automoderation rule.
        """

        post_data = self.parent._get_kwargs(
            {
                "type": (
                    "name",
                    "enabled",
                    "trigger_metadata",
                ),
                "snowflake": (
                    "exempt_roles",
                    "exempt_channels",
                ),
                "enum": (
                    "event_type",
                    "trigger_type",
                ),
                "object": (
                    "actions",
                    "trigger_metadata",
                ),
            },
            kwargs,
        )
        route = Route(
            "PATCH",
            "/guilds/{guild_id}/auto-moderation/rules/{rule_id}",
            guild_id=guild_id,
            rule_id=rule_id,
        )
        data: payloads.AutoModerationRule = await self.parent.request(
            route,
            reason=reason,
            data=post_data,
        )
        return AutoModerationRule(
            state=self.parent,
            data=data,
        )

    async def delete_auto_moderation_rule(
            self,
            guild_id: int,
            rule_id: int,
            *,
            reason: str | None = None) -> None:
        """
        Delete an automoderation rule.
        """

        route = Route(
            "DELETE",
            "/guilds/{guild_id}/auto-moderation/rules/{rule_id}",
            guild_id=guild_id,
            rule_id=rule_id,
        )
        await self.parent.request(
            route,
            reason=reason,
        )
