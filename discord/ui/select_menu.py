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

from typing import List, Optional, Union
import uuid

from .models import BaseComponent, DisableableComponent
from ..emoji import Emoji
from ..enums import ComponentType
from ..partial_emoji import PartialEmoji, _EmojiTag
from ..utils import MISSING
from ..types.components import (
    Component, 
    SelectMenu as SelectMenuPayload,
    SelectOption as SelectOptionPayload,
)


class SelectOption(BaseComponent):
    """
    An option menu that can go into a :class:`discord.ui.SelectMenu` object.

    Attributes
    -----------
    label: :class:`str`
        The label that gets shown on the option.
    value: Optional[:class:`str`]
        The value that this option will give back to the bot.
    description: Optional[:class:`str`]
        A description for the option.
    emoji: Optional[[Union[:class:`str`, :class:`discord.Emoji`, :class:`discord.PartialEmoji`]]
        An emoji to be displayed with the option.
    default: Optional[bool]
        Whether or not the option is selected by default.
    """

    def __init__(
            self, *, label: str, value: Optional[str] = MISSING, description: Optional[str] = None,
            emoji: Optional[Union[str, Emoji, PartialEmoji]] = None, default: Optional[bool] = False):
        self.label = label
        self.value = value if value is not MISSING else label
        self.description = description
        if emoji is not None:
            if isinstance(emoji, str):
                self.emoji = PartialEmoji.from_str(emoji)
            elif isinstance(emoji, _EmojiTag):
                self.emoji = emoji._to_partial()
            else:
                raise TypeError(f'expected emoji to be str, Emoji, or PartialEmoji not {emoji.__class__}')
        else:
            self.emoji = None
        self.default = default or False

    def to_dict(self) -> SelectOptionPayload:
        v = {
            "label": self.label,
            "value": self.value,
        }
        if self.description:
            v.update({"description": self.description})
        if self.emoji:
            v.update({"emoji": self.emoji.to_dict()})
        if self.default:
            v.update({"default": self.default})
        return v

    @classmethod
    def from_dict(cls, data: dict):
        emoji = data.get("emoji")
        if emoji is not None:
            emoji = PartialEmoji.from_dict(emoji)
        return cls(
            label=data.get("label"),
            value=data.get("value"),
            description=data.get("description"),
            emoji=emoji,
            default=data.get("default", False),
        )


class SelectMenu(DisableableComponent):
    """
    Discord's dropdown component.

    Attributes
    -----------
    custom_id: :class:`str`
        The custom ID for this component.
    options: List[discord.ui.SelectOption]
        The options that should be displayed in this component.
    placeholder: Optional[:class:`str`]
        The placeholder text for when nothing is selected.
    min_values: Optional[:class:`int`]
        The minimum amount of selectable values.
    max_values: Optional[:class:`int`]
        The maximum amount of selectable values.
    disabled: Optional[:class:`bool`]
        Whether or not the select menu is clickable.
    """

    def __init__(
            self, *, custom_id: Optional[str] = MISSING, options: List[SelectOption] = MISSING, placeholder: Optional[str] = None,
            min_values: Optional[int] = 1, max_values: Optional[int] = 1, disabled: Optional[bool] = False):
        self.custom_id = custom_id if custom_id is not MISSING else str(uuid.uuid1())
        self.options = options
        self.placeholder = placeholder
        self.min_values = min_values
        self.max_values = max_values
        self.disabled = disabled

    def to_dict(self) -> SelectMenuPayload:
        return {
            "type": ComponentType.select_menu.value,
            "custom_id": self.custom_id,
            "placeholder": self.placeholder,
            "min_values": self.min_values,
            "max_values": self.max_values,
            "options": [i.to_dict() for i in self.options],
            "disabled": self.disabled
        }

    @classmethod
    def from_dict(cls, data: dict):
        v = data.get("options", list())
        options = [SelectOption.from_dict(i) for i in v]
        return cls(
            custom_id=data.get("custom_id"),
            options=options,
            placeholder=data.get("placeholder"),
            min_values=data.get("min_values"),
            max_values=data.get("max_values"),
            disabled=data.get("disabled", False)
        )
