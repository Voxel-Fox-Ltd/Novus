from typing import TYPE_CHECKING

from .models import BaseComponent, ComponentHolder
from .button import Button, ButtonStyle
from .select_menu import SelectMenu
from ..enums import ComponentType
from ..components import _component_factory
from ..types.components import (
    MessageComponents as MessageComponentsPayload,
    ActionRow as ActionRowPayload,
)


class ActionRow(ComponentHolder):
    """
    The main UI component for adding and ordering components on Discord
    messages.
    """

    def to_dict(self) -> ActionRowPayload:
        return {
            "type": ComponentType.action_row.value,
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
    def boolean_buttons(cls, yes_id: str = None, no_id: str = None):
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
        """

        return cls(
            ActionRow(
                Button("Yes", style=ButtonStyle.success, custom_id=yes_id or "YES"),
                Button("No", style=ButtonStyle.danger, custom_id=no_id or "NO"),
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
