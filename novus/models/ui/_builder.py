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

from ...enums import ComponentType
from .action_row import ActionRow
from .button import Button
from .select_menu import (
    ChannelSelectMenu,
    MentionableSelectMenu,
    RoleSelectMenu,
    StringSelectMenu,
    UserSelectMenu,
)
from .text_input import TextInput

if TYPE_CHECKING:
    from ... import payloads
    from .component import Component


def component_builder(data: payloads.Component) -> Component:
    factory: type
    match data["type"]:
        case ComponentType.action_row.value:
            factory = ActionRow
        case ComponentType.button.value:
            factory = Button
        case ComponentType.string_select.value:
            factory = StringSelectMenu
        case ComponentType.text_input.value:
            factoru = TextInput
        case ComponentType.user_select.value:
            factory = UserSelectMenu
        case ComponentType.role_select.value:
            factory = RoleSelectMenu
        case ComponentType.mentionable_select.value:
            factory = MentionableSelectMenu
        case ComponentType.channel_select.value:
            factory = ChannelSelectMenu
        case _:
            raise ValueError()
    return factory._from_data(data)  # pyright: ignore
