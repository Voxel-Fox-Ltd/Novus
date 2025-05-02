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

from ...enums import ComponentType
from .action_row import ActionRow
from .button import Button
from .container import Container
from .file import FileComponent
from .media_gallery import MediaGallery
from .section import Section
from .select_menu import (
    ChannelSelectMenu,
    MentionableSelectMenu,
    RoleSelectMenu,
    StringSelectMenu,
    UserSelectMenu,
)
from .separator import Separator
from .text_display import TextDisplay
from .text_input import TextInput
from .thumbnail import Thumbnail

if TYPE_CHECKING:
    from ... import payloads
    from .component import Component


def component_builder(data: payloads.Component) -> Component:
    factory: type
    match data["type"]:
        case ComponentType.ACTION_ROW:
            factory = ActionRow
        case ComponentType.BUTTON:
            factory = Button
        case ComponentType.STRING_SELECT:
            factory = StringSelectMenu
        case ComponentType.TEXT_INPUT:
            factory = TextInput
        case ComponentType.USER_SELECT:
            factory = UserSelectMenu
        case ComponentType.ROLE_SELECT:
            factory = RoleSelectMenu
        case ComponentType.MENTIONABLE_SELECT:
            factory = MentionableSelectMenu
        case ComponentType.CHANNEL_SELECT:
            factory = ChannelSelectMenu
        case ComponentType.TEXT_DISPLAY:
            factory = TextDisplay
        case ComponentType.THUMBNAIL:
            factory = Thumbnail
        case ComponentType.SEPARATOR:
            factory = Separator
        case ComponentType.FILE:
            factory = FileComponent
        case ComponentType.MEDIA_GALLERY:
            factory = MediaGallery
        case ComponentType.CONTAINER:
            factory = Container
        case ComponentType.SECTION:
            factory = Section
        case _:
            raise ValueError()
    return factory._from_data(data)  # type: ignore
