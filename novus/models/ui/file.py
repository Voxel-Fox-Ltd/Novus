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
    "FileComponent",
)


class FileComponent(Component):
    """
    An item for display inside of a media gallery component.

    .. note:: This component can only be sent as part of components v2.

    Parameters
    ----------
    url : str
        The URL of the media item.
    spoiler : bool
        Whether or not the image is marked as a spoiler.
    id : int | None
        The ID of the component.

    Attributes
    ----------
    url : str
        The URL of the media item.
    spoiler : bool
        Whether or not the image is marked as a spoiler.
    id : int | None
        The ID of the component.
    """

    type = ComponentType.FILE

    def __init__(self, url: str, *, id: int | None = None, spoiler: bool = False):
        self.url = url
        self.id = id
        self.spoiler = spoiler

    def _to_data(self) -> payloads.File:
        v: payloads.File = {
            "type": self.type,
            "file": {
                "url": self.url
            },
            "spoiler": self.spoiler,
        }
        if self.id is not None:
            v["id"] = self.id
        return v

    @classmethod
    def _from_data(cls, data: payloads.File) -> Self:
        v = cls(url=data["file"]["url"])
        v.id = data.get("id")
        v.spoiler = data.get("spoiler", False)
        return v
