from typing import Any, Union, Optional, List

from .message import Message
from .role import Role
from .enums import (
    ApplicationCommandOptionType,
    ApplicationCommandType,
)
from .channel import _channel_factory


ApplicationCommandOptionChoiceValue = Union[str, int]

__all__ = (
    "ApplicationCommandOptionChoice",
    "ApplicationCommandOption",
    "ApplicationCommand",
)


class ApplicationCommandOptionChoice(object):
    """
    The possible choices that an application command can take.

    Parameters
    -----------
    name: :class:`str`
        The name of this option.
    value: :class:`str`
        The value given to this option.
    """

    def __init__(self, name: str, value: ApplicationCommandOptionChoiceValue = None):
        self.name: str = name
        self.value: Any = value if value is not None else name

    @classmethod
    def from_data(cls, data: dict):
        return cls(data['name'], data['value'])

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "value": self.value,
        }


class ApplicationCommandOption(object):
    """
    An option displayed in a given application command.

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
    """

    def __init__(
            self, name: str, type: ApplicationCommandOptionType, description: str,
            default: Optional[str] = None, required: bool = True, autocomplete: bool = False):
        """
        Parameters
        -----------
        name: :class:`str`
            The name of this option.
        type: :class:`ApplicationCommandOptionType`
            The type of this command option.
        description: :class:`str`
            The description given to this argument.
        default: :class:`str`
            The default value given to the command option.
        required: :class:`bool`
            Whether or not this option is required for the command to run.
        autocomplete: :class:`bool`
            Whether or not the user typing this option should send autocomplete
            interaction payloads.

            .. versionadded:: 0.0.4
        """

        self.name: str = name
        self.type: ApplicationCommandOptionType = type
        self.description: str = description
        self.default: Optional[str] = default
        self.required: bool = required
        self.choices: List[ApplicationCommandOptionChoice] = list()
        self.options: List['ApplicationCommandOption'] = list()
        self.channel_types: list = list()
        self.autocomplete: bool = autocomplete

    def add_choice(self, choice: ApplicationCommandOptionChoice) -> None:
        """
        Add a choice to this instance.
        """

        self.choices.append(choice)

    def add_option(self, option: 'ApplicationCommandOption') -> None:
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
        }
        if self.type in [ApplicationCommandOptionType.subcommand, ApplicationCommandOptionType.subcommand_group]:
            payload.pop("required")
            payload.pop("default")
            payload.pop("choices")
            payload.pop("channel_types")
            payload.pop("autocomplete")
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


class ApplicationCommand(object):
    """
    An instance of an application command.

    Attributes
    -----------
    name: :class:`str`
        The name of this command.
    description: :class:`str`
        The description for this command.
    options: List[:class:`ApplicationCommandOption`]
        A list of the options added to this command.
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
    options: List[:class:`ApplicationCommandOption`]
        A list of the options added to this command.
    """

    def __init__(
            self, name: str, description: str = None,
            type: ApplicationCommandType = ApplicationCommandType.chat_input,
            options: List[ApplicationCommandOption] = None):
        self.name: str = name
        self.description: Optional[str] = description
        self.type: ApplicationCommandType = type
        self.options: List[ApplicationCommandOption] = options or list()
        self.id: Optional[int] = None
        self.application_id: Optional[int] = None

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
            data['name'],
            data.get('description'),
            ApplicationCommandType(data.get('type', 1)),
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
        }
        if self.description is None:
            v.pop("description", None)
        if self.type != ApplicationCommandType.chat_input:
            v.pop("options", None)
        return v
