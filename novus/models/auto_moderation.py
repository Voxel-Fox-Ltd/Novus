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

from ..enums import (
    AutoModerationActionType,
    AutoModerationEventType,
    AutoModerationKeywordPresetType,
    AutoModerationTriggerType,
)
from ..utils import generate_repr, try_enum, try_snowflake
from .api_mixins.auto_moderation import AutoModerationAPIMixin
from .object import Object

if TYPE_CHECKING:
    from ..api import HTTPConnection
    from ..payloads import AutoModerationAction as AutoModerationActionPayload
    from ..payloads import \
        AutoModerationActionMetadata as AutoModerationActionMetadataPayload
    from ..payloads import AutoModerationRule as AutoModerationRulePayload
    from ..payloads import \
        AutoModerationTriggerMetadata as AutoModerationTriggerMetadataPayload
    from .abc import Snowflake

__all__ = (
    'AutoModerationTriggerMetadata',
    'AutoModerationAction',
    'AutoModerationRule',
)


class AutoModerationTriggerMetadata:
    """
    The metadata associated with an auto moderation trigger.

    Parameters
    ----------
    keyword_filters : list[str] | None
        A list of substrings which will be searched for in content.
        A keyword can be a phrase which contains multiple words. Wildcard
        symbols (``*``) can be used to customize how much of each keyword will
        be matched.
    regex_patterns : list[str] | None
        A list of regular expression patterns that will be matched against
        the content.
        Only rust flavored regex is supported.
    presets : list[novus.enums.AutoModerationKeywordPresetType] | None
        A list of preset word lists that you want to match against.
    allow_list : list[str] | None
        A list of substrings which should not trigger the rule.
    mention_total_limit : int | None
        The total number of unique role and user mentions allowed per message.
    """

    def __init__(
            self,
            *,
            keyword_filters: list[str] | None = None,
            regex_patterns: list[str] | None = None,
            presets: list[AutoModerationKeywordPresetType] | None = None,
            allow_list: list[str] | None = None,
            mention_total_limit: int | None = None):
        self.keyword_filters = keyword_filters or list()
        self.regex_patterns = regex_patterns or list()
        self.presets = presets or list()
        self.allow_list = allow_list or list()
        self.mention_total_limit = (
            mention_total_limit
            if mention_total_limit is not None
            else None
        )

    __repr__ = generate_repr((
        'keyword_filters',
        'regex_patterns',
        'presets',
        'allow_list',
        'mention_total_limit',
    ))

    @classmethod
    def _from_data(
            cls,
            *,
            data: AutoModerationTriggerMetadataPayload) -> AutoModerationTriggerMetadata:
        return cls(
            keyword_filters=data.get('keyword_filter'),
            regex_patterns=data.get('regex_patterns'),
            presets=[
                try_enum(AutoModerationKeywordPresetType, i)
                for i in data.get('presets', [])
            ] or None,
            allow_list=data.get('allow_list'),
            mention_total_limit=data.get('mention_total_limit'),
        )

    def _to_data(self) -> AutoModerationTriggerMetadataPayload:
        ret: AutoModerationTriggerMetadataPayload = {}
        if self.keyword_filters is not None:
            ret['keyword_filter'] = self.keyword_filters
        if self.regex_patterns is not None:
            ret['regex_patterns'] = self.regex_patterns
        if self.presets is not None:
            ret['presets'] = [i.value for i in self.presets]
        if self.allow_list is not None:
            ret['allow_list'] = self.allow_list
        if self.mention_total_limit is not None:
            ret['mention_total_limit'] = self.mention_total_limit
        return ret


class AutoModerationAction:
    """
    A moderation action to be taken on a rule being triggered.

    Parameters
    ----------
    type : novus.enums.AutoModerationActionType
        The type of action to be taken.
    channel : int | novus.models.abc.Snowflake | None
        The channel associated with the action. Can only be set if
        the action type is `AutoModerationActionType.send_alert_message`.
    duration : int | None
        The duration (in seconds) associated with the action. Can only be set
        if the action type is `AutoModerationActionType.timeout`.

    Attributes
    ----------
    type : novus.enums.AutoModerationActionType
        The type of action to be taken.
    channel_id : int | None
        The channel ID associated with the action. Will only be set if
        the action type is `AutoModerationActionType.send_alert_message`.
    duration : int | None
        The duration (in seconds) associated with the action. Will only be set
        if the action type is `AutoModerationActionType.timeout`.
    """

    __slots__ = (
        'type',
        'channel_id',
        'duration',
    )

    def __init__(
            self,
            type: AutoModerationActionType,
            *,
            channel: int | Snowflake | None = None,
            duration: int | None = None):
        self.type = type
        self.channel_id = None
        if channel is not None:
            if self.type != AutoModerationActionType.send_alert_message:
                raise ValueError("Cannot set channel for action type %s" % self.type)
            self.channel_id = channel if isinstance(channel, int) else channel.id
        self.duration = None
        if duration is not None:
            if self.type != AutoModerationActionType.timeout:
                raise ValueError("Cannot set duration for action type %s" % self.type)
            self.duration = duration

    __repr__ = generate_repr(('type', 'channel_id', 'duration',))

    @classmethod
    def _from_data(cls, *, data: AutoModerationActionPayload) -> AutoModerationAction:
        return cls(
            type=try_enum(AutoModerationActionType, data['type']),
            channel=try_snowflake(data.get('metadata', {}).get('channel_id')),
            duration=data.get('metadata', {}).get('duration_seconds'),
        )

    def _to_data(self) -> AutoModerationActionPayload:
        data: AutoModerationActionPayload = {}  # type: ignore
        data['type'] = self.type.value
        metadata: AutoModerationActionMetadataPayload = {}  # type: ignore
        if self.channel_id is not None:
            metadata['channel_id'] = str(self.channel_id)
        if self.duration is not None:
            metadata['duration_seconds'] = self.duration
        if metadata:
            data['metadata'] = metadata
        return data


class AutoModerationRule(AutoModerationAPIMixin):
    """
    A model representing an auto moderation rule.

    Attributes
    ----------
    id : int
        The ID of the rule.
    guild_id : int
        The ID of the guild that the rule is tied to.
    name : str
        The name given to the rule.
    creator_id : int
        The ID of the user that created the rule.
    event_type : novus.enums.AutoModerationEventType
        The event type.
    trigger_type : novus.enums.AutoModerationTriggerType
        The trigger type for the rule.
    trigger_metadata : novus.models.AutoModerationTriggerMetadata
        The metadata associated with the rule.
    actions : list[novus.models.AutoModerationAction]
        A list of actions taken when the rule is triggered.
    enabled : bool
        Whether the rule is enabled.
    exempt_role_ids : list[int]
        A list of IDs corresponding to roles that are exempt from this rule.
    exempt_channel_ids : list[int]
        A list of IDs corresponding to channels that are exempt from this rule.
    guild : novus.models.abc.Snowflake
        A guild object (or a snowflake object).
    """

    __slots__ = (
        '_state',
        'id',
        'guild_id',
        'name',
        'creator_id',
        'event_type',
        'trigger_type',
        'trigger_metadata',
        'actions',
        'enabled',
        'exempt_role_ids',
        'exempt_channel_ids',
        'guild',
    )

    def __init__(
            self,
            *,
            state: HTTPConnection,
            data: AutoModerationRulePayload):
        self._state = state
        self.id = try_snowflake(data['id'])
        self.guild_id = try_snowflake(data['guild_id'])
        self.name = data['name']
        self.creator_id = try_snowflake(data['creator_id'])
        self.event_type = try_enum(AutoModerationEventType, data['event_type'])
        self.trigger_type = try_enum(AutoModerationTriggerType, data['trigger_type'])
        self.trigger_metadata = AutoModerationTriggerMetadata._from_data(data=data['trigger_metadata'])
        self.actions: list[AutoModerationAction] = [
            AutoModerationAction._from_data(data=d)
            for d in data['actions']
        ]
        self.enabled = data['enabled']
        self.exempt_role_ids = [
            try_snowflake(d)
            for d in data['exempt_roles']
        ]
        self.exempt_channel_ids = [
            try_snowflake(d)
            for d in data['exempt_channels']
        ]
        self.guild = Object(self.guild_id, state=self._state)

    __repr__ = generate_repr((
        'id',
        'guild_id',
        'name',
        'event_type',
        'trigger_type',
        'trigger_metadata',
        'actions',
        'enabled',
    ))
