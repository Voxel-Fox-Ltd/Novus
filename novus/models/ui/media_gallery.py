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

from typing_extensions import Self

from ...enums import ComponentType
from ...utils import MISSING
from .component import Component

if TYPE_CHECKING:
    from ... import payloads

__all__ = (
    "MediaGallery",
    "MediaGalleryItem",
)


class MediaGalleryItem:
    """
    An item for display inside of a media gallery component.

    Parameters
    ----------
    url : str
        The URL of the media item.
    description : str | None
        A description of the media item.
    spoiler : bool
        Whether or not the image is marked as a spoiler.

    Attributes
    ----------
    url : str
        The URL of the media item.
    description : str | None
        A description of the media item.
    spoiler : bool
        Whether or not the image is marked as a spoiler.
    """

    def __init__(self, url: str, *, description: str | None = None, spoiler: bool = False):
        self.url = url
        self.description = description
        self.spoiler = spoiler

    def _to_data(self) -> payloads.MediaGalleryItem:
        v: payloads.MediaGalleryItem = {
            "media": {
                "url": self.url,
            },
            "spoiler": self.spoiler,
        }
        if self.description:
            v["description"] = self.description
        return v

    @classmethod
    def _from_data(cls, data: payloads.MediaGalleryItem) -> Self:
        v = cls(url=data["media"]["url"])
        if "description" in data:
            v.description = data["description"]
        if "spoiler" in data:
            v.spoiler = data["spoiler"]
        return v


class MediaGallery(Component):
    """
    An image display that can go into a layout component.

    .. note:: This component can only be sent as part of components v2.

    Parameters
    ----------
    url : str
        The URL of the image to be displayed.
    description : str | None
        The description of the image.
    spoiler : bool
        Whether or not the image is marked as a spoiler.

    Attributes
    ----------
    url : str
        The URL of the image to be displayed.
    description : str | None
        The description of the image.
    spoiler : bool
        Whether or not the image is marked as a spoiler.
    """

    type = ComponentType.MEDIA_GALLERY

    items: list[MediaGalleryItem]
    id: int | None

    def __init__(
            self,
            items: list[MediaGalleryItem | str] = MISSING,
            *,
            id: int | None = None):
        self.items = []
        if items is not MISSING:
            for item in items:
                if isinstance(item, str):
                    item = MediaGalleryItem(item)
                self.items.append(item)
        self.id = id

    def _to_data(self) -> payloads.MediaGallery:
        v: payloads.MediaGallery = {
            "type": self.type,
            "items": [item._to_data() for item in self.items],
        }
        if self.id is not None:
            v["id"] = self.id
        return v

    @classmethod
    def _from_data(cls, data: payloads.MediaGallery) -> Self:
        v = cls()
        if "id" in data:
            v.id = data["id"]
        for item in data["items"]:
            v.items.append(MediaGalleryItem._from_data(item))
        return v
