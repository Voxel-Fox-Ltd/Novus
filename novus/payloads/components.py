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

from typing import TYPE_CHECKING, Literal, TypedDict, Union

from typing_extensions import NotRequired

if TYPE_CHECKING:
    from .emoji import PartialEmoji

__all__ = (
    'Button',
    'SelectOption',
    'SelectMenu',
    'TextInput',
    'ActionRow',
    'Section',
    'TextDisplay',
    'Thumbnail',
    'MediaGallery',
    'MediaGalleryItem',
    'File',
    'Separator',
    'Container',
    'UnfurledMediaItem',
    'Component',
)


class Button(TypedDict):
    custom_id: str
    type: Literal[2]
    style: int
    emoji: NotRequired[PartialEmoji]
    url: NotRequired[str]
    disabled: NotRequired[bool]
    label: NotRequired[str]


class SelectOption(TypedDict):
    label: str
    value: str
    description: NotRequired[str]
    emoji: NotRequired[PartialEmoji]
    default: NotRequired[bool]


class SelectMenu(TypedDict):
    type: int
    custom_id: str
    options: NotRequired[list[SelectOption]]
    channel_types: NotRequired[list[int]]
    placeholder: NotRequired[str]
    min_values: NotRequired[int]
    max_values: NotRequired[int]
    disabled: NotRequired[bool]


class TextInput(TypedDict):
    type: Literal[4]
    custom_id: str
    style: int
    label: str
    min_length: NotRequired[int]
    max_length: NotRequired[int]
    required: NotRequired[bool]
    value: NotRequired[str]
    placeholder: NotRequired[str]


class ActionRow(TypedDict):
    type: Literal[1]
    components: list[Component]


class Section(TypedDict):
    type: Literal[9]
    id: NotRequired[int]
    components: list[Component]
    accessory: Component


class TextDisplay(TypedDict):
    type: Literal[10]
    id: NotRequired[int]
    content: str


class Thumbnail(TypedDict):
    type: Literal[11]
    id: NotRequired[int]
    media: UnfurledMediaItem
    description: NotRequired[str]
    spoiler: NotRequired[bool]


class MediaGallery(TypedDict):
    type: Literal[12]
    id: NotRequired[int]
    items: list[MediaGalleryItem]


class MediaGalleryItem(TypedDict):
    media: UnfurledMediaItem
    description: NotRequired[str]
    spoiler: NotRequired[bool]


class File(TypedDict):
    type: Literal[13]
    id: NotRequired[int]
    file: UnfurledMediaItem
    spoiler: NotRequired[bool]


class Separator(TypedDict):
    type: Literal[14]
    id: NotRequired[int]
    divider: NotRequired[bool]
    spacing: NotRequired[Literal[1] | Literal[2]]


class Container(TypedDict):
    type: Literal[17]
    id: NotRequired[int]
    components: list[Component]
    accent_color: NotRequired[int | None]
    spoiler: NotRequired[bool]


class UnfurledMediaItem(TypedDict):
    url: str


Component = Union[
    Button,
    SelectMenu,
    TextInput,
    ActionRow,
    Section,
    TextDisplay,
    Thumbnail,
    MediaGallery,
    File,
    Separator,
    Container,
]
