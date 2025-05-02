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
    "TextDisplay",
)


class TextDisplay(Component):
    """
    A display component for text.

    .. note:: This component can only be sent as part of components v2.

    Parameters
    ----------
    content : str
        The content of the text display.
    id : int | None
        An ID for the component.

    Attributes
    ----------
    content : str
        The content of the text display.
    id : int | None
        An ID for the component.
    """

    type = ComponentType.TEXT_DISPLAY

    content: str
    id: int | None

    def __init__(self, content: str, *, id: int | None = None):
        self.content = content
        self.id = id

    def _to_data(self) -> payloads.TextDisplay:
        v: payloads.TextDisplay = {
            "type": self.type,
            "content": self.content
        }
        if self.id is not None:
            v["id"] = self.id
        return v

    @classmethod
    def _from_data(cls, data: payloads.TextDisplay) -> Self:
        v = cls(data["content"])
        if "id" in data:
            v.id = data["id"]
        return v
