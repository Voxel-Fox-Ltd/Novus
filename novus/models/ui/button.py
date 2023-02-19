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

from typing import TYPE_CHECKING, ClassVar, Type

from typing_extensions import Self

from ...enums import ButtonStyle, ComponentType
from .component import ComponentEmojiMixin, InteractableComponent

if TYPE_CHECKING:
    from ... import PartialEmoji, payloads

__all__ = (
    'Button',
)


class Button(InteractableComponent, ComponentEmojiMixin):
    """
    A button component.

    Parameters
    ----------
    label : str
        The label of the button. Either this or ``emoji`` needs to be set.
    style : novus.ButtonStyle
        The style of the button.
    custom_id : str
        The custom ID of the component.
    emoji : novus.PartialEmoji | novus.Emoji | str
        The emoji attached to the button. Either this or ``label`` needs to be
        set.
    url : str
        The URL that the button leads to, if the style is
        `novus.ButtonStyle.url`.
    disabled : bool
        Whether or not the button is disabled.

    Attributes
    ----------
    label : str | None
        The label of the button. Either this or ``emoji`` needs to be set.
    style : novus.ButtonStyle
        The style of the button.
    custom_id : str
        The custom ID of the component.
    emoji : novus.PartialEmoji | novus.Emoji | None
        The emoji attached to the button. Either this or ``label`` needs to be
        set.
    url : str | None
        The URL that the button leads to, if the style is
        `novus.ButtonStyle.url`.
    disabled : bool
        Whether or not the button is disabled.
    """

    __slots__ = (
        'label',
        'style',
        'custom_id',
        '_emoji',
        'url',
        'disabled',
    )

    type = ComponentType.button
    styles: ClassVar[Type[ButtonStyle]] = ButtonStyle

    label: str | None
    style: ButtonStyle
    custom_id: str
    url: str | None
    disabled: bool
    emoji: PartialEmoji | None  # From mixin

    def __init__(
            self,
            label: str | None = None,
            *,
            style: ButtonStyle = ButtonStyle.secondary,
            custom_id: str,
            emoji: str | PartialEmoji | None = None,
            url: str | None = None,
            disabled: bool = False):
        self.label = label
        self.style = style
        self.custom_id = custom_id
        self.emoji = emoji  # pyright: ignore
        self.url = url
        self.disabled = disabled

    def _to_data(self) -> payloads.Button:
        d: payloads.Button = {
            "type": self.type.value,
            "style": self.style.value,
            "custom_id": self.custom_id,
            "disabled": self.disabled,
        }
        if self.label:
            d["label"] = self.label
        if self.emoji:
            d["emoji"] = self.emoji._to_data()
        if self.url:
            d["url"] = self.url
        return d

    @classmethod
    def _from_data(cls, data: payloads.Button) -> Self:
        emoji_data = data.get("emoji")
        if emoji_data:
            emoji_object = PartialEmoji(data=emoji_data)
        else:
            emoji_object = None
        return cls(
            label=data.get("label"),
            emoji=emoji_object,
            style=ButtonStyle(data["style"]),
            custom_id=data["custom_id"],
            url=data.get("url"),
            disabled=data.get("disabled", False),
        )
