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

from typing_extensions import Self

from ...enums import ComponentType, TextInputStyle
from ...utils import generate_repr
from .component import InteractableComponent

if TYPE_CHECKING:
    from ... import payloads

__all__ = (
    'TextInput',
)


class TextInput(InteractableComponent):
    """
    A text input component for inside of modals.
    """

    __slots__ = (
        'label',
        'style',
        'custom_id',
        'min_length',
        'max_length',
        'required',
        'value',
        'placeholder',
    )

    type = ComponentType.text_input
    label: str
    style: TextInputStyle
    custom_id: str
    min_length: int
    max_length: int
    required: bool
    value: str | None
    placeholder: str | None

    def __init__(
            self,
            label: str,
            *,
            style: TextInputStyle = TextInputStyle.short,
            custom_id: str,
            min_length: int = 0,
            max_length: int = 4_000,
            required: bool = True,
            value: str | None = None,
            placeholder: str | None = None):
        self.label = label
        self.style = style
        self.custom_id = custom_id
        self.min_length = min_length
        self.max_length = max_length
        self.required = required
        self.value = value or None
        self.placeholder = placeholder or None

    __repr__ = generate_repr(('label', 'style',))

    def _to_data(self) -> payloads.TextInput:
        v: payloads.TextInput = {
            "type": self.type.value,
            "label": self.label,
            "style": self.style.value,
            "custom_id": self.custom_id,
            "min_length": self.min_length,
            "max_length": self.max_length,
        }
        if self.value is not None:
            v["value"] = self.value
        if self.placeholder is not None:
            v["placeholder"] = self.placeholder
        return v

    @classmethod
    def _from_data(cls, data: payloads.TextInput) -> Self:
        return cls(
            label=data["label"],
            style=TextInputStyle(data["style"]),
            custom_id=data["custom_id"],
            min_length=data.get("min_length", 0),
            max_length=data.get("max_length", 4_000),
            required=data.get("required", True),
            value=data.get("value"),
            placeholder=data.get("placeholder"),
        )
