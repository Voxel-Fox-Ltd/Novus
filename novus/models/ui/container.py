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

from typing import TYPE_CHECKING, Iterable

from typing_extensions import Self

from ...enums import ComponentType
from ...utils import MISSING
from .component import Component, LayoutComponentHolder

if TYPE_CHECKING:
    from ... import payloads

__all__ = (
    "Container",
)


class Container(LayoutComponentHolder):
    """
    A container component.

    .. note:: This component can only be sent as part of components v2.

    Parameters
    ----------
    components : Iterable[Component]
        The components to add to the container.
    accent_color : int | None
        The accent color of the container.
    spoiler : bool
        Whether or not to show a spoiler tag on the container.
    id : int | None
        The ID of the component.

    Attributes
    ----------
    components : Iterable[Component]
        The components to add to the container.
    accent_color : int | None
        The accent color of the container.
    spoiler : bool
        Whether or not to show a spoiler tag on the container.
    id : int | None
        The ID of the component.
    """

    type = ComponentType.CONTAINER

    components: list[Component | None]
    accent_color: int | None
    spoiler: bool
    id: int | None

    def __init__(
            self,
            components: Iterable[Component] = MISSING,
            *,
            accent_color: int | None = None,
            spoiler: bool = False,
            id: int | None = None) -> None:
        super().__init__(components)
        self.accent_color = accent_color
        self.spoiler = spoiler
        self.id = id

    def _to_data(self) -> payloads.Container:
        data: payloads.Container = {
            "type": self.type,
            "components": [
                i._to_data()
                for i in self.components
                if i is not None
            ],
        }
        if self.id is not None:
            data["id"] = self.id
        if self.accent_color is not None:
            data["accent_color"] = self.accent_color
        if self.spoiler:
            data["spoiler"] = True
        return data

    @classmethod
    def _from_data(cls, data: payloads.Container) -> Self:
        from ._builder import component_builder
        components = [component_builder(c) for c in data["components"]]
        return cls(
            components=components,
            accent_color=data.get("accent_color"),
            spoiler=data.get("spoiler", False),
            id=data.get("id"),
        )
