"""
The MIT License (MIT)

Copyright (c) 2021-present Kae Bartlett

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from __future__ import annotations

import uuid
from typing import Optional, TYPE_CHECKING

from .models import InteractableComponent
from ..enums import TextStyle, ComponentType

if TYPE_CHECKING:
    from ..types.components import (
        InputText as InputTextPayload,
    )


class InputText(InteractableComponent):
    """Represents an input text component.

    .. versionadded:: 0.0.5

    Attributes
    ------------
    label: :class:`str`
        The label you want to display above the input text component in the modal.
    style: :class:`discord.TextStyle`
        The style of the input text component.
    custom_id: Optional[:class:`str`]
        The ID that you want to assign to this input text component.
    placeholder: Optional[:class:`str`]
        The text shown (greyed out) in the input text component.
    min_length: Optional[:class:`int`]
        The minimum length of the required input.
    max_length: Optional[:class:`int`]
        The maximum length of the required input.
    required: Optional[:class:`bool`]
        Whether or not the text field is required.
    value: Optional[:class:`str`]
        The default value that goes into the text field.
    """

    __slots__ = ("label", "style", "custom_id", "min_length", "max_length",)
    TYPE = ComponentType.input_text

    def __init__(
            self, *, label: str = None, custom_id: Optional[str] = None,
            style: TextStyle = TextStyle.short, placeholder: Optional[str] = None,
            min_length: int = None, max_length: int = None, required: bool = True,
            value: str = None):
        self.label = label
        self.style = style
        self.placeholder = placeholder
        self.custom_id = custom_id or str(uuid.uuid1())
        self.min_length = min_length
        self.max_length = max_length
        self.required = required
        self.value = value

    def __repr__(self) -> str:
        attrs = (
            ('label', self.label),
            ('style', self.style),
            ('placeholder', self.placeholder),
            ('custom_id', self.custom_id),
            ('min_length', self.min_length),
            ('max_length', self.max_length),
            ('required', self.required),
            ('value', self.value),
        )
        inner = ' '.join('%s=%r' % t for t in attrs)
        return f'{self.__class__.__name__}({inner})'

    def to_dict(self) -> InputTextPayload:
        v = {
            "type": self.TYPE.value,
            "label": self.label,
            "style": self.style.value,
            "custom_id": self.custom_id,
            "placeholder": self.placeholder,
            "min_length": self.min_length,
            "max_length": self.max_length,
            "required": self.required,
            "value": self.value,
        }
        return v  # type: ignore

    @classmethod
    def from_dict(cls, data: InputTextPayload) -> InputText:
        """
        Construct an instance of an input text component from an API response.
        Because these aren't sent to bots, this is almost entirely useless.

        Parameters
        -----------
        data: :class:`dict`
            The payload data that the component should be constructed from.

        Returns
        -------
        :class:`discord.ui.InputText`
            The component that the payload describes.
        """

        return cls(
            style=TextStyle(data.get("style", TextStyle.short.value)),
            custom_id=data.get("custom_id"),
            label=data.get("label"),
            placeholder=data.get("placeholder"),
            min_length=data.get("min_length"),
            max_length=data.get("max_length"),
            required=data.get("required"),
            value=data.get("value"),
        )
