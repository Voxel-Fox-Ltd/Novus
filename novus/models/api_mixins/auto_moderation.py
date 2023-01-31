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

from ...utils import MISSING, try_id, try_object

if TYPE_CHECKING:
    from ...api import HTTPConnection
    from ...enums import AutoModerationEventType, AutoModerationTriggerType
    from ..abc import Snowflake, StateSnowflakeWithGuild
    from ..auto_moderation import (
        AutoModerationAction,
        AutoModerationRule,
        AutoModerationTriggerMetadata,
    )


class AutoModerationAPIMixin:

    @classmethod
    async def fetch(
            cls,
            state: HTTPConnection,
            guild: int | Snowflake,
            rule: int | Snowflake) -> AutoModerationRule:
        """
        Get an instance of an auto moderation rule from the API.

        Parameters
        ----------
        state : HTTPConnection
            The API connection.
        guild : int | novus.abc.Snowflake
            An association to a guild that you want to get the rule from.
        rule : int | novus.abc.Snowflake
            An association to get the rule from.

        Returns
        -------
        novus.AutoModerationRule
            The auto moderation rule.
        """

        return await state.auto_moderation.get_auto_moderation_rule(
            try_id(guild),
            try_id(rule),
        )

    @classmethod
    async def fetch_all_for_guild(
            cls,
            state: HTTPConnection,
            guild: int | Snowflake) -> list[AutoModerationRule]:
        """
        Get all of the auto moderation rules from the API for a given guild.

        Parameters
        ----------
        state : novus.HTTPConnection
            The API connection to manage the entity with.
        guild : int | novus.abc.Snowflake
            An association to a guild that you want to get the rules from.

        Returns
        -------
        list[novus.AutoModerationRule]
            The list of auto moderation rules in the guild.
        """

        return await state.auto_moderation.list_auto_moderation_rules_for_guild(
            try_id(guild),
        )

    async def edit(
            self: StateSnowflakeWithGuild,
            *,
            reason: str | None = None,
            name: str = MISSING,
            event_type: AutoModerationEventType = MISSING,
            trigger_type: AutoModerationTriggerType = MISSING,
            trigger_metadata: AutoModerationTriggerMetadata = MISSING,
            actions: list[AutoModerationAction] = MISSING,
            enabled: bool = MISSING,
            exempt_roles: list[int | Snowflake] = MISSING,
            exempt_channels: list[int | Snowflake] = MISSING) -> AutoModerationRule:
        """
        Edit an instance of the auto moderation rule.

        Parameters
        ----------
        name : str
            The new name for the role.
        event_type : novus.AutoModerationEventType
            The event type.
        trigger_type : novus.AutoModerationTriggerType
            The trigger type.
        trigger_metadata : novus.AutoModerationTriggerMetadata
            The trigger metadata.
        actions : list[novus.AutoModerationAction]
            The actions to be taken on trigger.
        enabled : bool
            Whether the rule is enabled or not.
        exempt_roles : list[int | novus.abc.Snowflake]
            A list of roles that are exempt from the rule.
        exempt_channels : list[int | novus.abc.Snowflake]
            A list of channels that are exempt from the rule.
        reason : str | None
            The reason shown in the audit log.

        Returns
        -------
        novus.AutoModerationRule
            The updated rule.
        """

        updates: dict[str, Any] = {}

        if name is not MISSING:
            updates["name"] = name
        if event_type is not MISSING:
            updates["event_type"] = event_type
        if trigger_type is not MISSING:
            updates["trigger_type"] = trigger_type
        if trigger_metadata is not MISSING:
            updates["trigger_metadata"] = trigger_metadata
        if actions is not MISSING:
            updates["actions"] = actions
        if enabled is not MISSING:
            updates["enabled"] = enabled
        if exempt_roles is not MISSING:
            updates["exempt_roles"] = [try_object(i) for i in exempt_roles]
        if exempt_channels is not MISSING:
            updates["exempt_channels"] = [try_object(i) for i in exempt_channels]

        return await self._state.auto_moderation.modify_auto_moderation_rule(
            self.guild.id,
            self.id,
            reason=reason,
            **updates,
        )

    async def delete(
            self: StateSnowflakeWithGuild,
            *,
            reason: str | None = None) -> None:
        """
        Delete this auto moderation rule.

        Parameters
        ----------
        reason : str | None
            The reason shown in the audit log.

        Returns
        -------
        novus.AutoModerationRule
            The updated rule.
        """

        await self._state.auto_moderation.delete_auto_moderation_rule(
            self.guild.id,
            self.id,
            reason=reason,
        )
        return

    @classmethod
    async def create(
            cls,
            state: HTTPConnection,
            guild: int | Snowflake,
            *,
            reason: str | None = None,
            name: str,
            event_type: AutoModerationEventType,
            trigger_type: AutoModerationTriggerType,
            trigger_metadata: AutoModerationTriggerMetadata | None = None,
            actions: list[AutoModerationAction] | None = None,
            enabled: bool = False,
            exempt_roles: list[int | Snowflake] | None = None,
            exempt_channels: list[int | Snowflake] | None = None) -> AutoModerationRule:
        """
        Create a new auto moderation rule.

        Parameters
        ----------
        state : novus.HTTPConnection
            The API connection to create the entity with.
        guild: int | novus.abc.Snowflake
            The ID of the guild to create the object in.
        name : str
            The new name for the role.
        event_type : novus.AutoModerationEventType
            The event type.
        trigger_type : novus.AutoModerationTriggerType
            The trigger type.
        trigger_metadata : novus.AutoModerationTriggerMetadata | None
            The trigger metadata.
        actions : list[novus.AutoModerationAction] | None
            The actions to be taken on trigger.
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
            The updated rule.
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

        return await state.auto_moderation.create_auto_moderation_rule(
            try_id(guild),
            reason=reason,
            **updates,
        )
