from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Union, Optional, List

from .enums import (
    ApplicationCommandOptionType,
    ApplicationCommandType,
)
from .channel import _channel_factory
from .permissions import Permissions

if TYPE_CHECKING:
    from .types.interactions import (
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
            value: ApplicationCommandOptionChoiceValue = None):
        self.name: str = name
        self.value: Any = value if value is not None else name

    @classmethod
    def from_data(cls, data: dict):
        return cls(
            name=data['name'],
            value=data['value'],
        )

    def to_json(self) -> dict:
        return {
            "name": self.name,
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
    default: :class:`Any`
        The default value given to the command option.
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
    """

    def __init__(
            self,
            *,
            name: str,
            type: ApplicationCommandOptionType,
            description: str,
            default: Optional[str] = None,
            required: bool = True,
            autocomplete: bool = False,
            name_localizations: Dict[str, str] = None,
            description_localizations: Dict[str, str] = None,
            choices: List[ApplicationCommandOptionChoice] = None,
            options: List[ApplicationCommandOption] = None,
            ):
        self.name: str = name
        self.type: ApplicationCommandOptionType = type
        self.description: str = description
        self.default: Optional[str] = default
        self.required: bool = required
        self.choices: List[ApplicationCommandOptionChoice] = choices or list()
        self.options: List[ApplicationCommandOption] = options or list()
        self.channel_types: list = list()
        self.autocomplete: bool = autocomplete
        self.name_localizations = name_localizations or dict()
        self.description_localizations = description_localizations or dict()

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
            default=data.get('default', None),
            required=data.get('required', False),
            autocomplete=data.get('autocomplete', False),
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
            "default": self.default,
            "required": self.required,
            "autocomplete": self.autocomplete,
            "choices": [i.to_json() for i in self.choices],
            "options": [i.to_json() for i in self.options],
        }
        if self.type in [ApplicationCommandOptionType.subcommand, ApplicationCommandOptionType.subcommand_group]:
            payload.pop("required", None)
            payload.pop("default", None)
            payload.pop("choices", None)
            payload.pop("channel_types", None)
            payload.pop("autocomplete", None)
        else:
            counter = 0
            channel_types = []
            while len(channel_types) != len(self.channel_types) and counter < 50:
                t, _ = _channel_factory(counter)
                if t in self.channel_types:
                    channel_types.append(counter)
                counter += 1
            payload["channel_types"] = channel_types
        return payload


class ApplicationCommand:
    """
    An instance of an application command.

    .. versionchanged:: 0.0.6

        The positional args are now kwargs.

    Attributes
    -----------
    name: :class:`str`
        The name of this command.
    description: :class:`str`
        The description for this command.
    type: :class:`ApplicationCommandType`
        The type of the application command.
    options: List[:class:`ApplicationCommandOption`]
        A list of the options added to this command.
    default_permission: :class:`Permissions`
        The permissions that are required to run the application command.

        .. versionadded:: 0.0.6
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

    Parameters
    -----------
    name: :class:`str`
        The name of this command.
    description: :class:`str`
        The description for this command.
    type: :class:`ApplicationCommandType`
        The type of the application command. Defaults to a chat input (slash) command.
    options: List[:class:`ApplicationCommandOption`]
        A list of the options added to this command.
    default_permission: :class:`Permissions`
        The permissions that are required to run the application command.

        .. versionadded:: 0.0.6
    name_localizations: Dict[:class:`str`, :class:`str`]
        A dictionary of language codes to translations for the name of the command.

        .. versionadded:: 0.0.6
    description_localizations: Dict[:class:`str`, :class:`str`]
        A dictionary of language codes to translations for the description of the command.

        .. versionadded:: 0.0.6
    """

    def __init__(
            self,
            *,
            name: str,
            description: str = None,
            type: ApplicationCommandType = ApplicationCommandType.chat_input,
            options: List[ApplicationCommandOption] = None,
            default_permission: Permissions = None,
            name_localizations: Dict[str, str] = None,
            description_localizations: Dict[str, str] = None):
        self.name: str = name
        self.description: Optional[str] = description
        self.type: ApplicationCommandType = type
        self.options: List[ApplicationCommandOption] = options or list()
        self.id: Optional[int] = None
        self.application_id: Optional[int] = None
        self.default_permission = default_permission or None
        self.name_localizations = name_localizations or dict()
        self.description_localizations = description_localizations or dict()

    def __repr__(self):
        return f"ApplcationCommand<name={self.name}, type={self.type.name}>"

    def add_option(self, option: ApplicationCommandOption):
        """
        Add an option to this command instance.
        """

        self.options.append(option)

    @classmethod
    def from_data(cls, data: dict):
        command = cls(
            name=data['name'],
            description=data.get('description'),
            type=ApplicationCommandType(data.get('type', 1)),
            default_permission=Permissions(int(data.get('permissions', 0))),
            name_localizations=data.get("name_localizations", dict()),
            description_localizations=data.get("description_localizations", dict()),
        )
        command.id = int(data.get('id', 0)) or None
        command.application_id = int(data.get('application_id', 0)) or None
        for option in data.get('options', list()):
            command.add_option(ApplicationCommandOption.from_data(option))
        return command

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.to_json() == other.to_json()

    def to_json(self):
        v = {
            "name": self.name,
            "description": self.description,
            "type": self.type.value,
            "options": [i.to_json() for i in self.options],
            "name_localizations": self.name_localizations,
            "description_localizations": self.description_localizations,
        }
        if self.default_permission:
            v["default_permission"] = str(self.default_permission.value)
        if self.description is None:
            v.pop("description", None)
            v.pop("description_localizations")
        if self.type != ApplicationCommandType.chat_input:
            v.pop("options", None)
        return v
