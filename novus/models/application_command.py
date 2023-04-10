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

from typing import TYPE_CHECKING

from typing_extensions import Self

from ..enums.application_command import ApplicationCommandType, ApplicationOptionType
from ..enums.channel import ChannelType
from ..flags.permissions import Permissions
from ..utils import (
    MISSING,
    Localization,
    flatten_localization,
    generate_repr,
    try_snowflake,
)

if TYPE_CHECKING:
    from .. import enums, flags, payloads
    from ..api import HTTPConnection

    LocType = dict[str, str] | dict[enums.Locale, str] | Localization | None

__all__ = (
    'ApplicationCommandOption',
    'ApplicationCommandChoice',
    'PartialApplicationCommand',
    'ApplicationCommand',
)


class ApplicationCommandOption:
    """
    An option for use inside of an application command.

    Parameters
    ----------
    name: str
        The name of the option.
    description: str
        The description of the option.
    type: novus.ApplicationOptionType
        The type of the option.
    name_localizations : dict[str | novus.Locale, str] | novus.Localization
        Localizations for the option's name.
    description_localizations : dict[str | novus.Locale, str] | novus.Localization
        Localizations for the option's description.
    required: bool
        Whether or not the option is required.
    choices: list[novus.ApplicationCommandChoice]
        Choices for the option.
    options: list[novus.ApplicationCommandOption]
        Options for the option.
    channel_types: list[novus.ChannelType]
        The channel types that are supported by the option, if the option type
        is a channel.
    min_value: int
        The minimum allowed value for the option if the option type is an
        integer or number.
    max_value: int
        The maximum allowed value for the option if the option type is an
        integer or number.
    min_length: int
        The minimum length of the input string if the option type is string.
    max_length: int
        The maximum length of the input string if the option type is string.
    autocomplete: bool
        Whether or not autocomplete interactions are enabled for this option.

    Attributes
    ----------
    name: str
        The name of the option.
    description: str
        The description of the option.
    type: novus.ApplicationOptionType
        The type of the option.
    name_localizations : novus.Localization
        Localizations for the option's name.
    description_localizations : novus.Localization
        Localizations for the option's description.
    required: bool
        Whether or not the option is required.
    choices: list[novus.ApplicationCommandChoice]
        Choices for the option.
    options: list[novus.ApplicationCommandOption]
        Options for the option.
    channel_types: list[novus.ChannelType]
        The channel types that are supported by the option, if the option type
        is a channel.
    min_value: int
        The minimum allowed value for the option if the option type is an
        integer or number.
    max_value: int
        The maximum allowed value for the option if the option type is an
        integer or number.
    min_length: int
        The minimum length of the input string if the option type is string.
    max_length: int
        The maximum length of the input string if the option type is string.
    autocomplete: bool
        Whether or not autocomplete interactions are enabled for this option.
    """

    if TYPE_CHECKING:
        type: ApplicationOptionType
        name: str
        name_localizations: Localization
        description: str
        description_localizations: Localization
        required: bool
        choices: list[ApplicationCommandChoice]
        options: list[ApplicationCommandOption]
        channel_types: list[ChannelType]
        min_value: int | float | None
        max_value: int | float | None
        min_length: int | None
        max_length: int | None
        autocomplete: bool

    def __init__(
            self,
            name: str,
            description: str,
            type: ApplicationOptionType,
            *,
            name_localizations: LocType = MISSING,
            description_localizations: LocType = MISSING,
            required: bool = True,
            choices: list[ApplicationCommandChoice] = MISSING,
            options: list[ApplicationCommandOption] = MISSING,
            channel_types: list[ChannelType] = MISSING,
            min_value: int | float | None = MISSING,
            max_value: int | float | None = MISSING,
            min_length: int | None = MISSING,
            max_length: int | None = MISSING,
            autocomplete: bool = False):
        self.name = name
        self.description = description
        self.type = type
        self.name_localizations = flatten_localization(name_localizations)
        self.description_localizations = flatten_localization(description_localizations)
        self.required = required
        self.choices = choices or []
        self.options = options or []
        self.channel_types = channel_types or []
        self.min_value = min_value or None
        self.max_value = max_value or None
        self.min_length = min_length or None
        self.max_length = max_length or None
        self.autocomplete = autocomplete

    __repr__ = generate_repr(('name', 'description', 'type', 'choices', 'options'))

    def add_option(self, option: ApplicationCommandOption) -> Self:
        self.options.append(option)
        return self

    def _to_data(self) -> payloads.ApplicationCommandOption:
        d: payloads.ApplicationCommandOption = {
            "type": self.type.value,
            "name": self.name,
            "description": self.description,
        }
        if self.name_localizations:
            d["name_localizations"] = self.name_localizations._to_data()
        if self.description_localizations:
            d["description_localizations"] = self.description_localizations._to_data()
        if self.options:
            d["options"] = [i._to_data() for i in self.options]

        # Only add options valid for the type
        if self.type == ApplicationOptionType.sub_command:
            pass
        elif self.type == ApplicationOptionType.sub_command_group:
            pass
        else:
            if self.required:
                d["required"] = self.required
            if self.choices:
                d["choices"] = [i._to_data() for i in self.choices]
            if self.channel_types:
                d["channel_types"] = [i.value for i in self.channel_types]
            if self.min_value is not None:
                d["min_value"] = self.min_value
            if self.max_value is not None:
                d["max_value"] = self.max_value
            if self.min_length is not None:
                d["min_length"] = self.min_length
            if self.max_length is not None:
                d["max_length"] = self.max_length
            if self.autocomplete:
                d["autocomplete"] = self.autocomplete
        return d

    @classmethod
    def _from_data(cls, data: payloads.ApplicationCommandOption) -> Self:
        return cls(
            name=data["name"],
            description=data["description"],
            type=ApplicationOptionType(data["type"]),
            name_localizations=data.get("name_localizations"),
            description_localizations=data.get("description_localizations"),
            required=data.get("required", True),
            choices=[
                ApplicationCommandChoice(**d)
                for d in data.get("choices") or []
            ],
            options=[
                ApplicationCommandOption._from_data(d)
                for d in data.get("options") or []
            ],
            channel_types=[
                ChannelType(d)
                for d in data.get("channel_types") or []
            ],
            min_value=data.get("min_value"),
            max_value=data.get("max_value"),
            min_length=data.get("min_length"),
            max_length=data.get("max_length"),
            autocomplete=data.get("autocomplete", False),
        )


class ApplicationCommandChoice:
    """
    A choice object for application commands.

    Parameters
    ----------
    name : str
        The name of the choice.
    value : str | int | float
        The value associated with the choice.

        .. note::

            Large numbers (those in BIGINT range, including IDs) will be
            truncated by Discord - it's recommended that you use a string in
            their place.
    name_localizations : dict[str | novus.Locale, str] | novus.Localization
        Localizations for the choice name.

    Attributes
    ----------
    name : str
        The name of the choice.
    name_localizations : novus.Localization
        Localizations for the command name.
    value : str | int | float
        The value associated with the choice.
    """

    name: str
    name_localizations: Localization
    value: str | int | float

    def __init__(
            self,
            name: str,
            value: str | int | float,
            *,
            name_localizations: LocType = None):
        self.name = name
        self.value = value
        self.name_localizations = flatten_localization(name_localizations)

    def _to_data(self) -> payloads.ApplicationCommandChoice:
        d: payloads.ApplicationCommandChoice = {
            "name": self.name,
            "value": self.value,
        }
        if self.name_localizations:
            d["name_localizations"] = self.name_localizations._to_data()
        return d


class PartialApplicationCommand:
    """
    A partial application command object. This is an object that can be
    created and used by general users.

    Parameters
    ----------
    name : str
        The name of the command.
    description : str
        The description of the command.
    type : novus.ApplicationCommandType
        The command type.
    name_localizations : dict[str | novus.Locale, str] | novus.Localization
        Localizations for the command name.
    description_localizations : dict[str | novus.Locale, str] | novus.Localization
        Localizations for the description.
    options : list[novus.ApplicationCommandOption]
        Thje options for the command.
    default_member_permissions : novus.Permissions
        The permissions required (by default) to run the command.
    dm_permission : bool
        Whether or not the command can be run in DMs.
    nsfw : bool
        Whether or not the command is marked as NSFW.

    Attributes
    ----------
    name : str
        The name of the command.
    description : str
        The description of the command.
    type : novus.ApplicationCommandType
        The command type.
    name_localizations : dict[str | novus.Locale, str] | novus.Localization
        Localizations for the command.
    description_localizations : dict[str | novus.Locale, str] | novus.Localization
        Localizations for the description.
    options : list[novus.ApplicationCommandOption]
        Thje options for the command.
    default_member_permissions : novus.Permissions
        The permissions required (by default) to run the command.
    dm_permission : bool
        Whether or not the command can be run in DMs.
    nsfw : bool
        Whether or not the command is marked as NSFW.
    """

    if TYPE_CHECKING:
        type: ApplicationCommandType
        name: str
        name_localizations: Localization
        description: str | None
        description_localizations: Localization
        options: list[ApplicationCommandOption]
        default_member_permissions: flags.Permissions
        dm_permission: bool
        nsfw: bool

    def __init__(
            self,
            name: str,
            description: str | None,
            type: ApplicationCommandType,
            *,
            name_localizations: LocType = MISSING,
            description_localizations: LocType = MISSING,
            options: list[ApplicationCommandOption] = MISSING,
            default_member_permissions: Permissions | None = MISSING,
            dm_permission: bool = True,
            nsfw: bool = False):
        self.type = type
        self.name = name
        self.name_localizations = flatten_localization(name_localizations)
        self.description = description
        self.description_localizations = flatten_localization(description_localizations)
        self.options = options or []
        if default_member_permissions is MISSING:
            self.default_member_permissions = None
        else:
            self.default_member_permissions = default_member_permissions
        self.dm_permission = dm_permission
        self.nsfw = nsfw

    __repr__ = generate_repr(('name', 'description', 'options', 'type',))

    def __eq__(self, other: PartialApplicationCommand) -> bool:
        return self._to_data() == other._to_data()

    def __ne__(self, other: PartialApplicationCommand) -> bool:
        return not self.__eq__(other)

    def add_option(self, option: ApplicationCommandOption) -> Self:
        self.options.append(option)
        return self

    def _to_data(self) -> payloads.PartialApplicationCommand:
        d: payloads.PartialApplicationCommand = {
            "name": self.name,
            "description": self.description,
            "type": self.type.value,
            "name_localizations": self.name_localizations._to_data(),
            "description_localizations": self.description_localizations._to_data(),
            "dm_permission": self.dm_permission,
            "default_member_permissions": None,
        }
        if self.default_member_permissions is not None:
            d["default_member_permissions"] = str(self.default_member_permissions.value)
        if self.options:
            d["options"] = [i._to_data() for i in self.options]
        return d

    @classmethod
    def _from_data(cls, data: payloads.ApplicationCommand) -> Self:
        permissions = Permissions(int(data.get("default_member_permissions") or 0))
        return cls(
            type=ApplicationCommandType(data.get("type", 1)),
            name=data["name"],
            name_localizations=data.get("name_localizations"),
            description=data["description"],
            description_localizations=data.get("description_localizations"),
            options=[
                ApplicationCommandOption._from_data(d)
                for d in data.get("options", [])
            ],
            default_member_permissions=permissions,
            dm_permission=data.get("dm_permission", True),
            nsfw=data.get("nsfw", False),
        )


class ApplicationCommand(PartialApplicationCommand):
    """
    An application command object.

    Attributes
    ----------
    id : int
        The ID of the command.
    type : novus.ApplicationCommandType
        The type of the command.
    application_id : int
        The ID of the application that the command is registered to.
    guild_id : int | None
        The ID of the guild that the command is registered to.
    name : str
        The name of the command.
    name_localizations : novus.Localization
        The command's name localizations.
    description : str
        The description of the command.
    description_localizations : novus.Localization
        The command's description localizations.
    options : list[novus.ApplicationCommandOption]
        The options of the command.
    default_member_permissions : novus.Permissions
        The permissions required to run the command by default.
    dm_permission : bool
        Whether or not the command can be run in DMs.
    nsfw : bool
        Whether or not the command is marked as NSFW.
    version : int
        The version of the command. An auto-updating snowflake.
    """

    if TYPE_CHECKING:
        id: int
        type: ApplicationCommandType
        application_id: int
        guild_id: int | None
        name: str
        name_localizations: Localization
        description: str
        description_localizations: Localization
        options: list[ApplicationCommandOption]
        default_member_permissions: flags.Permissions
        dm_permission: bool
        nsfw: bool
        version: int

    def __init__(
            self,
            *,
            state: HTTPConnection,
            data: payloads.ApplicationCommand):
        p = int(data.get("default_member_permissions", 0) or 0)
        permissions = Permissions(p)
        self.state = state
        super().__init__(
            name=data.get("name"),
            description=data.get("description"),
            type=ApplicationCommandType(data.get("type", 1)),
            name_localizations=data.get("name_localizations"),
            description_localizations=data.get("description_localizations"),
            default_member_permissions=permissions,
            dm_permission=data.get("dm_permission", True),
            options=[
                ApplicationCommandOption._from_data(d)
                for d in data.get("options", [])
            ],
        )
        self.id = try_snowflake(data["id"])
        self.application_id = try_snowflake(data["application_id"])
        self.guild_id = try_snowflake(data.get("guild_id"))
        self.version = try_snowflake(data["version"])

    __repr__ = generate_repr(('id', 'name', 'description', 'options', 'type',))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ApplicationCommand):
            return False
        if not self._to_data() == other._to_data():
            return False
        return all((
            self.id == other.id,
            self.application_id == other.application_id,
            self.guild_id == other.guild_id,
        ))
