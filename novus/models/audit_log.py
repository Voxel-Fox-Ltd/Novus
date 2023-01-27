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

from typing import TYPE_CHECKING, Generator, Any

from .api_mixins.audit_log import AuditLogAPIMixin
from .user import User
from .channel import Channel
from ..utils import try_snowflake, cached_slot_property, generate_repr
from ..enums import AuditLogEventType

if TYPE_CHECKING:
    from .abc import Snowflake
    from ..api import HTTPConnection
    from ..payloads import (
        AuditLog as AuditLogPayload,
        AuditLogEntry as AuditLogEntryPayload,
    )

__all__ = (
    'AuditLogContainer',
    'AuditLogEntry',
    'AuditLog',
)


class AuditLogContainer:
    """
    A proxy object for audit log changes, and extra information given back from
    Discord. This can hold a wide variety of information (attributes of changed
    entities; additional parameters for a user action; etc), so can be iterated
    over like a `dict` for easy access.
    """

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __len__(self) -> int:
        return len(self.__dict__)

    def __iter__(self) -> Generator[tuple[str, Any], None, None]:
        yield from self.__dict__.items()

    def __repr__(self) -> str:
        values = ' '.join('%s=%r' % item for item in self.__dict__.items())
        if values:
            return f'<{self.__class__.__name__} {values}>'
        return f'<{self.__class__.__name__}>'

    if TYPE_CHECKING:

        def __getattr__(self, item: str) -> Any:
            ...

        def __setattr__(self, key: str, value: Any) -> Any:
            ...


class AuditLogEntry:
    """
    An individual entry in the audit log.

    Attributes
    ----------
    id : int
        The ID of the entry.
    reason : str | None
        The reason added to the entry, if one was given.
    target_id : int | None
        The ID of the affected entity.
    target : novus.models.abc.Snowflake | None
        The affected entity.
    user_id : int | None
        The ID of the user or app that made the changes.
    user : novus.models.User | None
        The user or app that made the changes.
    action_type : novus.enums.AuditLogEvent
        The action that was applied.
    options : novus.models.AuditLogContainer
        Additional information for the entry.
    before : novus.models.AuditLogContainer | None
        The state of the object before the action happened. Could be ``None``
        in the case of new objects being created.
    after : novus.models.AuditLogContainer | None
        The state of the object after the action happened. Could be ``None``
        in the case of an object being removed.
    """

    __slots__ = (
        'log',
        'id',
        'reason',
        'target_id',
        'user_id',
        'action_type',
        'options',
        'before',
        'after',

        '_cs_user',
        '_cs_target',
    )

    def __init__(self, *, data: AuditLogEntryPayload, log: AuditLog):
        self.log = log
        self.id = try_snowflake(data['id'])
        self.reason = data.get('reason', None)
        self.target_id = try_snowflake(data.get('target_id'))
        self.user_id = try_snowflake(data.get('user_id'))
        self.action_type = AuditLogEventType(data['action_type'])

        self.options: AuditLogContainer | None = None
        if 'options' in data:
            self.options = AuditLogContainer()
            for k, v in data['options'].items():
                if k.endswith("_id") or k == "id":
                    v = int(v)  # type: ignore
                setattr(self.options, k, v)

        self.before: AuditLogContainer | None = AuditLogContainer()
        self.after: AuditLogContainer | None = AuditLogContainer()

        # Log all changes uwu
        changes = data.get('changes', list())
        for change in changes:

            # Special case for role add/remove
            if change['key'].startswith("$"):
                if change['key'] == "$add":
                    self.before = None
                    change_obj = self.after
                elif change['key'] == "$remove":
                    self.after = None
                    change_obj = self.before
                else:
                    raise ValueError("Invalid change key")
                nv = change.get('new_value')
                assert change_obj is not None
                assert nv is not None
                for k, v in nv[0].items():
                    if k == "id":
                        v = int(v)
                    setattr(change_obj, k, v)
                continue

            # Everything else case for everything else
            key = change['key']
            setattr(self.before, key, change.get('old_value'))
            setattr(self.after, key, change.get('new_value'))

        # If we're all null
        if self.before is not None:
            for _, v in self.before:
                if v is not None:
                    break
            else:
                self.before = None
        if self.after is not None:
            for _, v in self.after:
                if v is not None:
                    break
            else:
                self.after = None

    __repr__ = generate_repr(('id', 'action_type', 'reason',))

    @cached_slot_property('_cs_user')
    def user(self) -> User | None:
        if self.user_id is None:
            return None
        return self.log._get_user(self.user_id)

    @cached_slot_property('_cs_target')
    def target(self) -> Snowflake | None:
        if self.target_id is None:
            return None
        action_base = "_".join(self.action_type.name.split("_")[:-1])
        match action_base:
            case "guild":
                return None
            case "channel":
                return None
            case "member" | "bot":
                return self.log._get_user(self.target_id)
            case "role":
                return None
            case "invite":
                return None
            case "webhook":
                return self.log._get_webhook(self.target_id)
            case "emoji":
                return None
            case "message":
                return None
            case "integration":
                return self.log._get_integration(self.target_id)
            case "stage_instance":
                return None
            case "sticker":
                return None
            case "guild_scheduled_event":
                return self.log._get_guild_scheduled_event(self.target_id)
            case "thread":
                return self.log._get_thread(self.target_id)
            case "application_command_permission":
                return self.log._get_application_command(self.target_id)
            case "auto_moderation_rule":
                return self.log._get_auto_moderation_rule(self.target_id)
            case _:
                return None


class AuditLog(AuditLogAPIMixin):
    """
    A model containing the audit logs for a guild.

    Attributes
    ----------
    entries : list[novus.models.AuditLogEntry]
        The entries contained in the audit log.
    """

    __slots__ = (
        'guild',
        'entries',
        '_state',
        '_targets',
        '_application_commands',
        '_auto_moderation_rules',
        '_guild_scheduled_events',
        '_integrations',
        '_threads',
        '_users',
        '_webhooks',
    )

    def __init__(self, *, data: AuditLogPayload, state: HTTPConnection, guild: Snowflake):
        self.guild = guild
        self._state = state
        self._targets: dict[str, dict[int, Any]] = {
            'application_commands': {int(i['id']): i for i in data['application_commands']},
            'auto_moderation_rules': {int(i['id']): i for i in data['auto_moderation_rules']},
            'guild_scheduled_events': {int(i['id']): i for i in data['guild_scheduled_events']},
            'integrations': {int(i['id']): i for i in data['integrations']},
            'threads': {int(i['id']): i for i in data['threads']},
            'users': {int(i['id']): i for i in data['users']},
            'webhooks': {int(i['id']): i for i in data['webhooks']},
        }
        self.entries = [
            AuditLogEntry(data=d, log=self)
            for d in data['audit_log_entries']
        ]

        self._application_commands = {}
        self._auto_moderation_rules = {}
        self._guild_scheduled_events = {}
        self._integrations = {}
        self._threads = {}
        self._users = {}
        self._webhooks = {}

    __repr__ = generate_repr(('guild',))

    def __iter__(self):
        return iter(self.entries)

    def _get_application_command(self, id: int):
        if id in self._application_commands:
            return self._application_commands[id]
        # TODO

    def _get_auto_moderation_rule(self, id: int):
        if id in self._auto_moderation_rules:
            return self._auto_moderation_rules[id]
        # TODO

    def _get_guild_scheduled_event(self, id: int):
        if id in self._guild_scheduled_events:
            return self._guild_scheduled_events[id]
        # TODO

    def _get_integration(self, id: int):
        if id in self._integrations:
            return self._integrations[id]
        # TODO

    def _get_thread(self, id: int):
        if id in self._threads:
            return self._threads[id]
        if id in self._targets['threads']:
            self._threads[id] = None
            return None
        self._threads[id] = u = Channel._from_data(
            data=self._targets['threads'][id],
            state=self._state,
        )
        return u

    def _get_user(self, id: int):
        if id in self._users:
            return self._users[id]
        if id in self._targets['users']:
            self._users[id] = None
            return None
        self._users[id] = u = User(
            data=self._targets['users'][id],
            state=self._state,
        )
        return u

    def _get_webhook(self, id: int):
        if id in self._webhooks:
            return self._webhooks[id]
        # TODO
