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

from .models import InteractableComponent, DisableableComponent
from ..emoji import Emoji
from ..enums import ComponentType, ChannelType
from ..partial_emoji import PartialEmoji, _EmojiTag
from ..channel import _channel_factory
from ..utils import MISSING
from ..types.components import (
    Component, 
    SelectMenu as SelectMenuPayload,
    ChannelSelectMenu as ChannelSelectMenuPayload,
    SelectOption as SelectOptionPayload,
)


class SelectOption(InteractableComponent):
    """
    An option menu that can go into a :class:`discord.ui.SelectMenu` object.

    Attributes
    -----------
    label: Optional[:class:`str`]
        The label that gets shown on the option. This is *not* optional if you are making
        the options yourself, but only optional when returned by the API (in which case, ``value``)
        will be used.
    value: Optional[:class:`str`]
        The value that this option will give back to the bot. If you don't provide a value, the label
        will be used in its place.
    description: Optional[:class:`str`]
        A description that will be shown in the select menu underneath the option.
    emoji: Optional[[Union[:class:`str`, :class:`discord.Emoji`, :class:`discord.PartialEmoji`]]
        An emoji to be displayed with the option.
    default: Optional[bool]
        Whether or not the option is selected by default. Only one option can have its ``default`` flag
        set to ``True`` per select menu. Defaults to ``False``.
    """

    __slots__ = ("label", "value", "description", "emoji", "default",)

    def __init__(
            self, *, label: Optional[str], value: Optional[str] = MISSING, description: Optional[str] = None,
            emoji: Optional[Union[str, Emoji, PartialEmoji]] = None, default: bool = False):
        self.label = label
        self.value = value if value is not MISSING else label
        self.description = description
        if emoji is not None:
            if isinstance(emoji, str):
                self.emoji = PartialEmoji.from_str(emoji)
            elif isinstance(emoji, _EmojiTag):
                self.emoji = emoji._to_partial()
            elif isinstance(emoji, dict):
                self.emoji = PartialEmoji(**emoji)
            else:
                raise TypeError(f'expected emoji to be str, Emoji, PartialEmoji, or dict not {emoji.__class__}')
        else:
            self.emoji = None
        self.default = default

    def __repr__(self) -> str:
        attrs = (
            ('label', self.label),
            ('value', self.value),
            ('description', self.description),
            ('emoji', self.emoji),
            ('default', self.default),
        )
        inner = ' '.join('%s=%r' % t for t in attrs)
        return f'{self.__class__.__name__}({inner})'

    def to_dict(self) -> SelectOptionPayload:
        v = {
            "label": self.label,
            "value": self.value,
            "default": self.default,
        }
        if self.description:
            v["description"] = self.description
        if self.emoji:
            v["emoji"] = self.emoji.to_dict()
        return v

    @classmethod
    def from_dict(cls, data: SelectOptionPayload):
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

    __slots__ = ("custom_id", "options", "placeholder", "min_values", "max_values", "disabled",)
    TYPE = ComponentType.select_menu

    def __init__(
            self, *, custom_id: str = MISSING, options: List[SelectOption] = MISSING, placeholder: Optional[str] = None,
            min_values: Optional[int] = 1, max_values: Optional[int] = 1, disabled: Optional[bool] = False):
        self.custom_id = custom_id if custom_id is not MISSING else str(uuid.uuid1())
        self.options = options
        self.placeholder = placeholder
        self.min_values = min_values
        self.max_values = max_values
        self.disabled = disabled

    def __repr__(self) -> str:
        attrs = (
            ('custom_id', self.custom_id),
            ('options ', self.options),
            ('placeholder ', self.placeholder),
            ('min_values ', self.min_values),
            ('max_values ', self.max_values),
            ('disabled', self.disable),
        )
        inner = ' '.join('%s=%r' % t for t in attrs)
        return f'{self.__class__.__name__}({inner})'

    def to_dict(self) -> SelectMenuPayload:
        v = {
            "type": self.TYPE.value,
            "custom_id": self.custom_id,
            "placeholder": self.placeholder,
            "min_values": self.min_values,
            "max_values": self.max_values,
            "disabled": self.disabled
        }
        if self.options:
            v["options"] = [i.to_dict() for i in self.options],
        return v

    @classmethod
    def from_dict(cls, data: SelectMenuPayload):
        v = data.get("options", list())
        options = [SelectOption.from_dict(i) for i in v]
        return cls(
            custom_id=data["custom_id"],
            options=options,
            placeholder=data.get("placeholder"),
            min_values=data.get("min_values"),
            max_values=data.get("max_values"),
            disabled=data.get("disabled", False)
        )


class UserSelectMenu(SelectMenu):
    """
    A dropdown component that lets you select a user.
    """

    TYPE = ComponentType.user_select_menu


class RoleSelectMenu(SelectMenu):
    """
    A dropdown component that lets you select a role.
    """

    TYPE = ComponentType.role_select_menu


class MentionableSelectMenu(SelectMenu):
    """
    A dropdown component that lets you select a mentionable (role or user).
    """

    TYPE = ComponentType.mentionable_select_menu


class ChannelSelectMenu(SelectMenu):
    """
    A dropdown component that lets you select a channel.
    """

    TYPE = ComponentType.channel_select_menu

    def __init__(self, *args, channel_types: Optional[List[ChannelType]] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.channel_types = channel_types or list()

    def to_dict(self) -> ChannelSelectMenuPayload:
        v: ChannelSelectMenuPayload = super().to_dict()  # type: ignore
        if self.channel_types:
            v["channel_types"] = [i.value for i in self.channel_types]
        return v

    def from_dict(self, data: ChannelSelectMenuPayload):
        v = super().from_dict(data)
        for channel_type in data.get('channel_types', list()):
            channel, _ = _channel_factory(channel_type)
            v.channel_types.append(channel)

