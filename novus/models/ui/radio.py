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

from ...enums import ComponentType
from ...utils import MISSING
from .component import Component

if TYPE_CHECKING:
    from ... import payloads

__all__ = (
    "RadioGroupOption",
    "RadioGroup",
)


class RadioGroupOption:
    """
    An option for a radio group.

    Parameters
    ----------
    label : str
        The label for the option.
    value : str
        The value for the option.
    description : str
        The description for the option.
    default : bool
        Whether or not the option is selected by default.

    Attributes
    ----------
    label : str
        The label for the option.
    value : str
        The value for the option.
    description : str
        The description for the option.
    default : bool
        Whether or not the option is selected by default.
    """

    label: str
    value: str
    description: str
    default: bool

    def __init__(
            self,
            label: str,
            value: str,
            description: str = MISSING,
            default: bool = MISSING):
        self.label = label
        self.value = value
        self.description = description
        self.default = default

    def _to_data(self) -> payloads.RadioGroupOption:
        v: payloads.RadioGroupOption = {
            "label": self.label,
            "value": self.value,
        }
        if self.description is not MISSING:
            v["description"] = self.description
        if self.default is not MISSING:
            v["default"] = self.default
        return v

    @classmethod
    def _from_data(cls, data: payloads.RadioGroupOption) -> Self:
        return cls(
            label=data["label"],
            value=data["value"],
            description=data.get("description", MISSING),
            default=data.get("default", MISSING),
        )


class RadioGroup(Component):
    """
    A group holding radio buttons.

    Parameters
    ----------
    custom_id : str
        A custom ID for the radio group.
    options : list[RadioGroupOption]
        A list of options for the radio group.
    required : bool
        Whether or not the radio group is required to be filled out.

    Attributes
    ----------
    custom_id : str
        A custom ID for the radio group.
    options : list[RadioGroupOption]
        A list of options for the radio group.
    required : bool
        Whether or not the radio group is required to be filled out.
    """

    type = ComponentType.RADIO_GROUP

    custom_id: str
    options: list[RadioGroupOption]
    required: bool

    def __init__(
            self,
            custom_id: str,
            options: list[RadioGroupOption],
            required: bool = False):
        self.custom_id = custom_id
        self.options = options
        self.required = required

    def add_option(self, option: RadioGroupOption) -> Self:
        """
        Adds an option to the radio group.

        Parameters
        ----------
        option : RadioGroupOption
            The option to add.

        Returns
        -------
        RadioGroup
            The radio group that the option was added to.
        """

        self.options.append(option)
        return self

    def _to_data(self) -> payloads.RadioGroup:
        v: payloads.RadioGroup = {
            "type": self.type,
            "custom_id": self.custom_id,
            "options": [i._to_data() for i in self.options],
        }
        if self.required:
            v["required"] = self.required
        return v

    @classmethod
    def _from_data(cls, data: payloads.RadioGroup) -> Self:
        return cls(
            custom_id=data["custom_id"],
            options=[RadioGroupOption._from_data(i) for i in data["options"]],
            required=data.get("required", False),
        )
