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
from typing import Optional, TYPE_CHECKING, Union

from .models import DisableableComponent
from ..enums import ButtonStyle, ComponentType
from ..partial_emoji import PartialEmoji, _EmojiTag
from ..errors import InvalidArgument

if TYPE_CHECKING:
    from ..emoji import Emoji
    from ..types.components import (
        Button as ButtonPayload,
    )


class Button(DisableableComponent):
    """Represents a UI button.

    Attributes
    ------------
    style: :class:`discord.ButtonStyle`
        The style of the button.
    custom_id: Optional[:class:`str`]
        The ID of the button that gets received during an interaction.
        If this button is for a URL, it does not have a custom ID.
    url: Optional[:class:`str`]
        The URL this button sends you to.
    disabled: :class:`bool`
        Whether the button is disabled or not.
    label: Optional[:class:`str`]
        The label of the button, if any.
    emoji: Optional[Union[:class:`.PartialEmoji`, :class:`.Emoji`, :class:`str`]]
        The emoji of the button, if available.
    """

    __slots__ = ("label", "style", "custom_id", "emoji", "url", "disabled",)
    TYPE = ComponentType.button

    def __init__(
            self, *, label: Optional[str] = None, custom_id: Optional[str] = None,
            style: Optional[ButtonStyle] = None,
            emoji: Optional[Union[str, Emoji, PartialEmoji]] = None, url: Optional[str] = None,
            disabled: Optional[bool] = False):
        self.label = label
        self.style = style or ButtonStyle.secondary
        self.custom_id = custom_id or str(uuid.uuid1())
        if emoji is not None:
            if isinstance(emoji, str):
                self.emoji = PartialEmoji.from_str(emoji)
            elif isinstance(emoji, _EmojiTag):
                self.emoji = emoji._to_partial()
            else:
                raise TypeError(f'expected emoji to be str, Emoji, or PartialEmoji not {emoji.__class__}')
        else:
            self.emoji = None
        self.url = url
        self.disabled = disabled
        if url is None and self.style == ButtonStyle.link:
            raise InvalidArgument("Missing URL for button type of link")
        if url is not None and self.style != ButtonStyle.link:
            raise InvalidArgument("Incompatible URL passed for button not of type link")
        if not label and not emoji:
            raise InvalidArgument("Both label and emoji cannot be empty")

    def __repr__(self) -> str:
        attrs = (
            ('label', self.label),
            ('style', self.style),
            ('custom_id', self.custom_id),
            ('emoji', self.emoji),
            ('url', self.url),
            ('disabled', self.disabled),
        )
        inner = ' '.join('%s=%r' % t for t in attrs)
        return f'{self.__class__.__name__}({inner})'

    def to_dict(self) -> ButtonPayload:
        v = {
            "type": self.TYPE.value,
            "label": self.label,
            "style": self.style.value,
            "disabled": self.disabled,
        }
        if self.emoji:
            v.update({"emoji": self.emoji.to_dict()})
        if self.url:
            v.update({"url": self.url})
        else:
            v.update({"custom_id": self.custom_id})
        return v

    @classmethod
    def from_dict(cls, data: ButtonPayload) -> Button:
        """
        Construct an instance of a button from an API response.

        Parameters
        -----------
        data: :class:`dict`
            The payload data that the button should be constructed from.

        Returns
        -------
        :class:`discord.ui.Button`
            The button that the payload describes.
        """

        emoji = data.get("emoji")
        if emoji is not None:
            emoji = PartialEmoji.from_dict(emoji)
        return cls(
            label=data.get("label"),
            style=ButtonStyle(data.get("style", ButtonStyle.secondary.value)),
            custom_id=data.get("custom_id"),
            url=data.get("url"),
            emoji=emoji,
            disabled=data.get("disabled", False),
        )

    @classmethod
    def confirm(cls, **kwargs) -> Button:
        """
        Give you a button instance with the text "Confirm", custom ID "CONFIRM", and
        a style of success.
        """

        return cls(
            label=kwargs.pop("label", "Confirm"),
            custom_id=kwargs.pop("custom_id", "CONFIRM"),
            style=kwargs.pop("style", ButtonStyle.success),
            **kwargs,
        )

    @classmethod
    def cancel(cls, **kwargs) -> Button:
        """
        Give you a button instance with the text "Cancel", custom ID "CANCEL", and
        a style of danger.
        """

        return cls(
            label=kwargs.pop("label", "Cancel"),
            custom_id=kwargs.pop("custom_id", "CANCEL"),
            style=kwargs.pop("style", ButtonStyle.danger),
            **kwargs,
        )
