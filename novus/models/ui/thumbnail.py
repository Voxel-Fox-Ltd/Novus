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
from .component import Component

if TYPE_CHECKING:
    from ... import payloads

__all__ = (
    "Thumbnail",
)


class Thumbnail(Component):
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
    id : int | None
        An ID for the component.

    Attributes
    ----------
    url : str
        The URL of the image to be displayed.
    description : str | None
        The description of the image.
    spoiler : bool
        Whether or not the image is marked as a spoiler.
    id : int | None
        An ID for the component.
    """

    type = ComponentType.THUMBNAIL

    url: str
    description: str | None
    spoiler: bool
    id: int | None

    def __init__(
            self,
            url: str,
            *,
            description: str | None = None,
            spoiler: bool = False,
            id: int | None = None):
        self.url = url
        self.description = description
        self.spoiler = spoiler
        self.id = id

    def _to_data(self) -> payloads.Thumbnail:
        v: payloads.Thumbnail = {
            "type": self.type,
            "media": {
                "url": self.url
            },
            "spoiler": self.spoiler,
        }
        if self.description:
            v["description"] = self.description
        if self.id is not None:
            v["id"] = self.id
        return v

    @classmethod
    def _from_data(cls, data: payloads.Thumbnail) -> Self:
        v = cls(url=data["media"]["url"])
        if "description" in data:
            v.description = data["description"]
        if "spoiler" in data:
            v.spoiler = data["spoiler"]
        if "id" in data:
            v.id = data["id"]
        return v
