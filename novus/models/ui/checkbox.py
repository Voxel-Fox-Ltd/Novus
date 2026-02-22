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
    "CheckboxGroupOption",
    "CheckboxGroup",
)


class CheckboxGroupOption:
    """
    An option for a checkbox group.

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

    def _to_data(self) -> payloads.CheckboxGroupOption:
        v: payloads.CheckboxGroupOption = {
            "label": self.label,
            "value": self.value,
        }
        if self.description is not MISSING:
            v["description"] = self.description
        if self.default is not MISSING:
            v["default"] = self.default
        return v

    @classmethod
    def _from_data(cls, data: payloads.CheckboxGroupOption) -> Self:
        return cls(
            label=data["label"],
            value=data["value"],
            description=data.get("description", MISSING),
            default=data.get("default", MISSING),
        )


class CheckboxGroup(Component):
    """
    A group holding checkbox buttons.

    Parameters
    ----------
    custom_id : str
        A custom ID for the checkbox group.
    options : list[CheckboxGroupOption]
        A list of options for the checkbox group.
    required : bool
        Whether or not the checkbox group is required to be filled out.

    Attributes
    ----------
    custom_id : str
        A custom ID for the checkbox group.
    options : list[CheckboxGroupOption]
        A list of options for the checkbox group.
    required : bool
        Whether or not the checkbox group is required to be filled out.
    """

    type = ComponentType.CHECKBOX_GROUP

    custom_id: str
    options: list[CheckboxGroupOption]
    required: bool

    def __init__(
            self,
            custom_id: str,
            options: list[CheckboxGroupOption],
            min_values: int = MISSING,
            max_values: int = MISSING,
            required: bool = False):
        self.custom_id = custom_id
        self.options = options
        self.min_values = min_values
        self.max_values = max_values
        self.required = required

    def _to_data(self) -> payloads.CheckboxGroup:
        v: payloads.CheckboxGroup = {
            "type": self.type,
            "custom_id": self.custom_id,
            "options": [i._to_data() for i in self.options],
        }
        if self.min_values is not MISSING:
            v["min_values"] = self.min_values
        if self.max_values is not MISSING:
            v["max_values"] = self.max_values
        if self.required:
            v["required"] = self.required
        return v

    @classmethod
    def _from_data(cls, data: payloads.CheckboxGroup) -> Self:
        return cls(
            custom_id=data["custom_id"],
            options=[CheckboxGroupOption._from_data(i) for i in data["options"]],
            min_values=data.get("min_values", MISSING),
            max_values=data.get("max_values", MISSING),
            required=data.get("required", False),
        )
