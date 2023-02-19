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

from typing import TYPE_CHECKING, Any, TypeAlias

from ....utils import try_object

if TYPE_CHECKING:
    import io

    from ....enums import AutoModerationEventType, AutoModerationTriggerType
    from ... import (
        AutoModerationAction,
        AutoModerationRule,
        AutoModerationTriggerMetadata,
    )
    from ...abc import Snowflake, StateSnowflake

    FileT: TypeAlias = str | bytes | io.IOBase


class GuildAutomodAPI:

    async def fetch_auto_moderation_rules(
            self: StateSnowflake) -> list[AutoModerationRule]:
        """
        Get the auto moderation rules for this guild.

        Returns
        -------
        list[novus.AutoModerationRule]
            A list of the auto moderation rules for the guild.
        """

        return await (
            self.state.auto_moderation
            .list_auto_moderation_rules_for_guild(self.id)
        )

    async def create_auto_moderation_rule(
            self: StateSnowflake,
            *,
            reason: str | None = None,
            name: str,
            event_type: AutoModerationEventType,
            trigger_type: AutoModerationTriggerType,
            actions: list[AutoModerationAction],
            trigger_metadata: AutoModerationTriggerMetadata | None = None,
            enabled: bool = False,
            exempt_roles: list[int | Snowflake] | None = None,
            exempt_channels: list[int | Snowflake] | None = None) -> AutoModerationRule:
        """
        Create a new auto moderation rule.

        Parameters
        ----------
        name : str
            The new name for the role.
        event_type : novus.AutoModerationEventType
            The event type.
        trigger_type : novus.AutoModerationTriggerType
            The trigger type.
        actions : list[novus.AutoModerationAction]
            The actions to be taken on trigger.
        trigger_metadata : novus.AutoModerationTriggerMetadata | None
            The trigger metadata.
        enabled : bool
            Whether the rule is enabled or not.
        exempt_roles : list[int | novus.abc.Snowflake] | None
            A list of roles that are exempt from the rule.
        exempt_channels : list[int | novus.abc.Snowflake] | None
            A list of channels that are exempt from the rule.
        reason : str | None
            The reason shown in the audit log.

        Returns
        -------
        novus.AutoModerationRule
            The created rule.
        """

        updates: dict[str, Any] = {}
        updates["name"] = name
        updates["event_type"] = event_type
        updates["trigger_type"] = trigger_type
        updates["trigger_metadata"] = trigger_metadata
        if actions:
            updates["actions"] = actions
        updates["enabled"] = enabled
        if exempt_roles:
            updates["exempt_roles"] = [try_object(i) for i in exempt_roles]
        if exempt_channels:
            updates["exempt_channels"] = [try_object(i) for i in exempt_channels]

        return await self.state.auto_moderation.create_auto_moderation_rule(
            self.id,
            reason=reason,
            **updates,
        )
