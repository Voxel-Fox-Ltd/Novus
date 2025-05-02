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
    "Separator",
)


class Separator(Component):
    """
    A separator component.

    .. note:: This component can only be sent as part of components v2.

    Parameters
    ----------
    divider : bool
        Whether or not to show a divider.
    spacing : int
        The amount of spacing to add before the separator. Accepted values are 1 (small padding)
        and 2 (large padding).
    id : int | None
        The ID of the component.

    Attributes
    ----------
    divider : bool
        Whether or not a divider is shown.
    spacing : int
        The amount of spacing to add before the separator.
    id : int | None
        The ID of the component.
    """

    type = ComponentType.SEPARATOR

    divider: bool
    spacing: int
    id: int | None

    def __init__(
            self,
            *,
            divider: bool = True,
            spacing: int = 1,
            id: int | None = None) -> None:
        self.divider = divider
        self.spacing = spacing
        self.id = id

    def _to_data(self) -> payloads.Separator:
        data: payloads.Separator = {
            "type": self.type,
            "divider": self.divider,
            "spacing": self.spacing,
        }
        if self.id is not None:
            data["id"] = self.id
        return data

    @classmethod
    def _from_data(cls, data: payloads.Separator) -> Self:
        return cls(
            divider=data.get("divider", True),
            spacing=data.get("spacing", 1),
            id=data.get("id"),
        )
