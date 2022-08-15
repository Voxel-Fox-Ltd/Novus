from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Union, Optional, List

from .enums import (
    ApplicationCommandOptionType,
    ApplicationCommandType,
    ChannelType,
    Locale,
)
from .channel import _channel_factory
from .permissions import Permissions
from .abc import Snowflake

if TYPE_CHECKING:
    from .types.interactions import (
        ApplicationCommand as ApplicationCommandPayload,
        ApplicationCommandInteractionDataOption as ApplicationCommandInteractionDataOptionPayload,
    )


ApplicationCommandOptionChoiceValue = Union[str, int]


__all__ = (
    "ApplicationCommandOptionChoice",
    "ApplicationCommandOption",
    "ApplicationCommand",
    "ApplicationCommandInteractionDataOption",
)


class ApplicationCommandInteractionDataOption:
    """
    A response from the API containing data from the user for a given interaction.
    This should not be created manually.

    .. versionadded:: 0.0.5

    Attributes
    -------------
    name: str
        The name of the parameter.
    type: ApplicationCommandOptionType
        The application command option type.
    value: Optional[str]
        The value passed into the command form the user.
    options: Optional[List[ApplicationCommandInteractionDataOption]]
        Present if this is a group or subcommand.
    focused: Optional[bool]
        True if this option is the currently focused option for autocomplete.
    """

    __slots__ = (
        "name",
        "type",
        "value",
        "options",
        "focused",
    )

    def __init__(self, data: ApplicationCommandInteractionDataOptionPayload):
        self.from_data(data)

    def __repr__(self) -> str:
        a = ('name', 'value', 'type')
        v = [f"{i}={getattr(self, i)!r}" for i in a]
        return f"{self.__class__.__name__}<{', '.join(v)}>"

    def from_data(self, data: ApplicationCommandInteractionDataOptionPayload):
        self.name: str = data["name"]
        self.type: ApplicationCommandOptionType = ApplicationCommandOptionType(data["type"])
        self.value: Optional[str] = data.get("value")
        self.options: Optional[List[ApplicationCommandInteractionDataOption]] = [
            ApplicationCommandInteractionDataOption(i) for i in data.get("options", [])
        ] or None
        self.focused: Optional[bool] = data.get("focused")


class ApplicationCommandOptionChoice:
    """
    The possible choices that an application command can take.

    .. versionchanged:: 0.0.6

        The positional args are now kwargs.

    Parameters
    -----------
    name: :class:`str`
        The name of this option.
    value: :class:`str`
        The value given to this option.
    """

    def __init__(
            self,
            *,
            name: str,
            name_localizations: Dict[Union[Locale, str], str] = None,
            value: ApplicationCommandOptionChoiceValue = None):
        self.name: str = name
        self.name_localizations = name_localizations or dict()
        self.value: Any = value if value is not None else name

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}<name={self.name!r}, value={self.value!r}>"

    @classmethod
    def from_data(cls, data: dict):
        return cls(
            name=data['name'],
            name_localizations=data.get("name_localizations", dict()),
            value=data['value'],
        )

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "name_localizations": {str(i): o for i, o in self.name_localizations.items()},
            "value": self.value,
        }


class ApplicationCommandOption:
    """
    An option displayed in a given application command.

    .. versionchanged:: 0.0.6

        The positional args are now kwargs.

    Parameters
    -----------
    name: :class:`str`
        The name of this option.
    type: :class:`ApplicationCommandOptionType`
        The type of this command option.
    description: :class:`str`
        The description given to this argument.
    required: Optional[:class:`bool`]
        Whether or not this option is required for the command to run.
    choices: List[:class:`ApplicationCommandOptionChoice`]
        A list of choices that this command can take.
    options: List[:class:`ApplicationCommandOption`]
        A list of options that go into the application command.
    channel_types: :class:`list`
        A list of channel types that the option accepts.

        .. versionadded:: 0.0.6
    autocomplete: :class:`bool`
        Whether or not the user typing this option should send autocomplete
        interaction payloads.

        .. versionadded:: 0.0.4
    name_localizations: Dict[:class:`str`, :class:`str`]
        A dictionary of language code to translation for the name of the command option.

        .. versionadded:: 0.0.6
    description_localizations: Dict[:class:`str`, :class:`str`]
        A dictionary of language code to translation for the name of the command option's description.

        .. versionadded:: 0.0.6
    min_value: Optional[:class:`int`]
        The minimum acceptable value of the field. Only usable for numeric types.

        .. versionadded:: 0.0.6
    max_value: Optional[:class:`int`]
        The maximum acceptable value of the field. Only usable for numeric types.

        .. versionadded:: 0.0.6

    Attributes
    -----------
    name: :class:`str`
        The name of this option.
    type: :class:`ApplicationCommandOptionType`
        The type of this command option.
    description: :class:`str`
        The description given to this argument.
    required: Optional[:class:`bool`]
        Whether or not this option is required for the command to run.
    choices: List[:class:`ApplicationCommandOptionChoice`]
        A list of choices that this command can take.
    options: List[:class:`ApplicationCommandOption`]
        A list of options that go into the application command.
    channel_types: :class:`list`
        A list of channel types that the option accepts.

        .. versionadded:: 0.0.4
    autocomplete: :class:`bool`
        Whether or not the user typing this option should send autocomplete
        interaction payloads.

        .. versionadded:: 0.0.4
    name_localizations: Dict[:class:`str`, :class:`str`]
        A dictionary of language code to translation for the name of the command option.

        .. versionadded:: 0.0.6
    description_localizations: Dict[:class:`str`, :class:`str`]
        A dictionary of language code to translation for the name of the command option's description.

        .. versionadded:: 0.0.6
    min_value: Optional[:class:`int`]
        The minimum acceptable value of the field. Only usable for numeric types.

        .. versionadded:: 0.0.6
    max_value: Optional[:class:`int`]
        The maximum acceptable value of the field. Only usable for numeric types.

        .. versionadded:: 0.0.6
    """

    def __init__(
            self,
            *,
            name: str,
            type: ApplicationCommandOptionType,
            description: str,
            required: bool = True,
            autocomplete: bool = False,
            name_localizations: Dict[Union[Locale, str], str] = None,
            description_localizations: Dict[Union[Locale, str], str] = None,
            choices: List[ApplicationCommandOptionChoice] = None,
            options: List[ApplicationCommandOption] = None,
            channel_types: List[ChannelType] = None,
            min_value: Optional[int] = None,
            max_value: Optional[int] = None,
            ):
        self.name: str = name
        self.type: ApplicationCommandOptionType = type
        self.description: str = description
        self.required: bool = required
        self.choices: List[ApplicationCommandOptionChoice] = choices or list()
        self.options: List[ApplicationCommandOption] = options or list()
        self.channel_types: list = channel_types or list()
        self.autocomplete: bool = autocomplete
        self.name_localizations = name_localizations or dict()
        self.description_localizations = description_localizations or dict()
        self.min_value = min_value
        self.max_value = max_value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}<name={self.name!r}, type={self.type.name!r}, choices={self.choices!r}, options={self.options!r}>"

    def add_choice(self, choice: ApplicationCommandOptionChoice) -> None:
        """
        Add a choice to this instance.
        """

        self.choices.append(choice)

    def add_option(self, option: ApplicationCommandOption) -> None:
        """
        Add an option to this instance.
        """

        self.options.append(option)

    @classmethod
    def from_data(cls, data: dict):
        base_option = cls(
            name=data['name'],
            type=ApplicationCommandOptionType(data['type']),
            description=data['description'],
            name_localizations=data.get("name_localizations", dict()),
            description_localizations=data.get("description_localizations", dict()),
            required=data.get('required', False),
            autocomplete=data.get('autocomplete', False),
            min_value=data.get('min_value', None),
            max_value=data.get('max_value', None),
        )
        for choice in data.get('choices', list()):
            base_option.add_choice(ApplicationCommandOptionChoice.from_data(choice))
        for option in data.get('options', list()):
            base_option.add_option(cls.from_data(option))
        for channel_type in data.get('channel_types', list()):
            channel, _ = _channel_factory(channel_type)
            base_option.channel_types.append(channel)
        return base_option

    def to_json(self) -> dict:
        payload = {
            "name": self.name,
            "type": self.type.value,
            "description": self.description,
            "required": self.required,
            "autocomplete": self.autocomplete,
            "choices": [i.to_json() for i in self.choices],
            "options": [i.to_json() for i in self.options],
            "min_value": self.min_value,
            "max_value": self.max_value,
            "name_localizations": {str(i): o for i, o in self.name_localizations.items()},
            "description_localizations": {str(i): o for i, o in self.description_localizations.items()},
        }
        if self.type in [ApplicationCommandOptionType.subcommand, ApplicationCommandOptionType.subcommand_group]:
            payload.pop("required", None)
            payload.pop("choices", None)
            payload.pop("channel_types", None)
            payload.pop("autocomplete", None)
        else:
            payload["channel_types"] = [i.value for i in self.channel_types]
        return payload


class ApplicationCommand(Snowflake):
    """
    An instance of an application command.

    .. versionchanged:: 0.0.6

        The positional args are now kwargs.

    Attributes
    -----------
    name: :class:`str`
        The name of this command.
    description: Optional[:class:`str`]
        The description for this command.
    type: :class:`ApplicationCommandType`
        The type of the application command.
    options: List[:class:`ApplicationCommandOption`]
        A list of the options added to this command.
    name_localizations: Dict[:class:`str`, :class:`str`]
        A dictionary of language codes to translations for the name of the command.

        .. versionadded:: 0.0.6
    description_localizations: Dict[:class:`str`, :class:`str`]
        A dictionary of language codes to translations for the description of the command.

        .. versionadded:: 0.0.6
    id: :class:`int`
        The ID of this application command.
    application_id: :class:`int`
        The application ID that this command is attached to.
    dm_permissions: :class:`bool`
        Whether or not the command is runnable in DMs.

        .. versionadded:: 0.0.6
    default_member_permissions: Optional[:class:`discord.Permissions`]
        The default permissions needed to be able to run this command.

        .. versionadded:: 0.0.6

    Parameters
    -----------
    name: :class:`str`
        The name of this command.
    description: Optional[:class:`str`]
        The description for this command.
    type: :class:`ApplicationCommandType`
        The type of the application command. Defaults to a chat input (slash) command.
    options: List[:class:`ApplicationCommandOption`]
        A list of the options added to this command.
    name_localizations: Dict[:class:`str`, :class:`str`]
        A dictionary of language codes to translations for the name of the command.

        .. versionadded:: 0.0.6
    description_localizations: Dict[:class:`str`, :class:`str`]
        A dictionary of language codes to translations for the description of the command.

        .. versionadded:: 0.0.6
    dm_permissions: :class:`bool`
        Whether or not the command is runnable in DMs.

        .. versionadded:: 0.0.6
    default_member_permissions: :class:`discord.Permissions`
        The default permissions needed to be able to run this command.

        .. versionadded:: 0.0.6
    """

    def __init__(
            self,
            *,
            name: str,
            description: Optional[str] = None,
            type: ApplicationCommandType = ApplicationCommandType.chat_input,
            options: Optional[List[ApplicationCommandOption]] = None,
            name_localizations: Optional[Dict[Union[Locale, str], str]] = None,
            description_localizations: Optional[Dict[Union[Locale, str], str]] = None,
            dm_permissions: bool = True,
            default_member_permissions: Optional[Permissions] = None):
        self.name: str = name
        self.description: str = description or name
        self.type: ApplicationCommandType = type
        self.options: List[ApplicationCommandOption] = options or list()
        self.id: Optional[int] = None
        self.application_id: Optional[int] = None
        self.name_localizations = name_localizations or dict()
        self.description_localizations = description_localizations or dict()
        self.dm_permissions = dm_permissions
        self.default_member_permissions = default_member_permissions

    def __repr__(self):
        return f"{self.__class__.__name__}<name={self.name!r}, type={self.type.name!r}, options={self.options!r}, permissions={self.default_member_permissions!r}>"

    def add_option(self, option: ApplicationCommandOption):
        """
        Add an option to this command instance.
        """

        self.options.append(option)

    @classmethod
    def from_data(cls, data: ApplicationCommandPayload):
        command = cls(
            name=data['name'],
            description=data['description'],
            type=ApplicationCommandType(data.get('type', 1)),
            name_localizations=data.get("name_localizations", dict()),
            description_localizations=data.get("description_localizations", dict()),
            dm_permissions=data.get("dm_permissions", True),
            default_member_permissions=None if data.get("default_member_permissions") is None else Permissions(int(data["default_member_permissions"])),
        )
        command.id = int(data.get('id', 0)) or None
        command.application_id = int(data.get('application_id', 0)) or None
        for option in data.get('options', list()):
            command.add_option(ApplicationCommandOption.from_data(option))
        return command

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.to_json() == other.to_json()

    def to_json(self) -> ApplicationCommandPayload:
        v: ApplicationCommandPayload = {
            "name": self.name,
            "description": self.description,
            "type": self.type.value,
            "options": [i.to_json() for i in self.options],
            "name_localizations": {str(i): o for i, o in self.name_localizations.items()},
            "description_localizations": {str(i): o for i, o in self.description_localizations.items()},
            "default_member_permissions": str(self.default_member_permissions.value) if self.default_member_permissions else None,
            "dm_permissions": self.dm_permissions,
        }
        if self.type != ApplicationCommandType.chat_input:
            v.pop("options", None)
            v.pop("description", None)
            v.pop("description_localizations", None)
        return v
