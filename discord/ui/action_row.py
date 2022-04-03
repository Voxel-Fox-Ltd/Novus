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

import typing

from .models import LayoutComponent, ComponentHolder
from .button import Button, ButtonStyle
from ..enums import ComponentType
from ..components import _component_factory
from ..types.components import (
    MessageComponents as MessageComponentsPayload,
    ActionRow as ActionRowPayload,
)
from ..utils import MISSING


class ActionRow(LayoutComponent, ComponentHolder):
    """
    The main UI component for adding and ordering components on Discord
    messages.

    Parameters
    -----------
    components: Union[:class:`discord.ui.InteractableComponent`, :class:`discord.ui.LayoutComponent`]
        The components that you want to add to the row.
    """

    TYPE = ComponentType.action_row

    def to_dict(self) -> ActionRowPayload:
        return {
            "type": self.TYPE.value,
            "components": [i.to_dict() for i in self.components],
        }

    @classmethod
    def from_dict(cls, data: ActionRowPayload):
        components = data.get("components", list())
        new_components = []
        for i in components:
            v = _component_factory(i)
            new_components.append(v)
        return cls(*new_components)


class MessageComponents(ComponentHolder):
    """
    A set of components that are attached to a message.

    Parameters
    -----------
    components: :class:`discord.ui.LayoutComponent`
        The components that you want to add to the message.
    """

    def to_dict(self) -> MessageComponentsPayload:
        return [i.to_dict() for i in self.components]

    @classmethod
    def from_dict(cls, data: MessageComponentsPayload):
        new_components = []
        for i in data:
            v = _component_factory(i)
            new_components.append(v)
        return cls(*new_components)

    @classmethod
    def boolean_buttons(cls, yes_id: str = None, no_id: str = None) -> MessageComponents:
        """
        Return a set of message components with yes/no buttons, ready for use. If provided, the given IDs
        will be used for the buttons. If not, the button custom IDs will be set to the strings
        "YES" and "NO".

        Parameters
        -----------
        yes_id:  Optional[:class:`str`:
            The custom ID of the yes button.
        no_id:  Optional[:class:`str`:
            The custom ID of the no button.

        Returns
        --------
        :class:`discord.ui.MessageComponents`
            A message components instance with the given buttons.
        """

        return cls(
            ActionRow(
                Button(label="Yes", style=ButtonStyle.success, custom_id=yes_id or "YES"),
                Button(label="No", style=ButtonStyle.danger, custom_id=no_id or "NO"),
            ),
        )

    @classmethod
    def add_buttons_with_rows(cls, *buttons: Button):
        """
        Adds a list of buttons, breaking into a new :class:`ActionRow` automatically when it contains 5
        buttons. This does *not* check that you've added fewer than 5 rows.

        Parameters
        -----------
        buttons: :class:`discord.ui.Button`
            The buttons that you want to have added.
        """

        v = cls()
        while buttons:
            v.add_component(ActionRow(*buttons[:5]))
            buttons = buttons[5:]
        return v

    @classmethod
    def add_number_buttons(
            cls, numbers: typing.List[int] = MISSING, *,
            add_negative: bool = False):
        """
        Creates a message components object with a list of number buttons added.

        Each number is added as its own button. Numbers provided as a list will be added as
        primary, where numbers added as negatives (if ``add_negative`` is set to ``True``)
        will be added as secondary buttons.

        A confirm button will not be automatically added.

        Parameters
        -----------
        numbers: typing.List[:class:`int`]
            The numbers that you want to add. If not provided, then 1, 5, 10, 50, and 100 are used.
            A list of more than five values must not be given.
            These will be added as buttons with the custom ID ``NUMBER VALUE``, where ``VALUE``
            is the value shown on the button.
        add_negative: :class:`bool`
            Whether or not the negative versions of your numbers should be added as buttons.
            Defaults to ``False``.
        """

        if numbers is MISSING:
            numbers = [1, 5, 10, 50, 100]

        v = cls()
        if add_negative:
            v.add_component(ActionRow(*[
                Button(label=f"{i:+d}", custom_id=f"NUMBER {i}", style=ButtonStyle.primary)
                for i in numbers
            ]))
            v.add_component(ActionRow(*[
                Button(label=f"{-i:+d}", custom_id=f"NUMBER {-i}", style=ButtonStyle.secondary)
                for i in numbers
            ]))
        else:
            v.add_component(ActionRow(*[
                Button(label=str(i), custom_id=f"NUMBER {i}", style=ButtonStyle.primary)
                for i in numbers
            ]))
        return v
