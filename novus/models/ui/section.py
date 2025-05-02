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
    "Section",
)


class Section(LayoutComponentHolder):
    """
    A generic layout component that holds other components.

    This class implements a ``__getitem__`` and an ``__iter__`` method to allow
    for eady indexing and iterating.

    .. note:: This component can only be sent as part of components v2.

    Parameters
    ----------
    components : Iterable[novus.Component]
        A list of components to be initially added to the section.
        Only supports one to three text display components.
    accessory : novus.Component
        An accessory for the section.
        Only supports thumbnail or button components.
    id : int | None
        An ID for the component.

    Attributes
    ----------
    components : list[novus.Component | None]
        The components inside of the section.
    accessory : novus.Component | None
        An accessory for the section.
    id : int | None
        An ID for the component.
    """

    type = ComponentType.SECTION

    components: list[Component | None]
    id: int | None

    def __init__(
            self,
            *,
            components: Iterable[Component] = MISSING,
            accessory: Component,
            id: int | None = None):
        super().__init__(components)
        self.accessory = accessory
        self.id = id

    def _to_data(self) -> payloads.Section:
        v: payloads.Section = {
            "type": self.type,
            "components": [
                i._to_data()
                for i in self.components
                if i is not None
            ],
            "accessory": self.accessory._to_data()
        }
        if self.id is not None:
            v["id"] = self.id
        return v

    @classmethod
    def _from_data(cls, data: payloads.Section) -> Self:
        v = cls()
        from ._builder import component_builder
        for d in data["components"]:
            v.add(component_builder(d))  # pyright: ignore
        if data.get("accessory"):
            v.accessory = component_builder(data["accessory"])
        if "id" in data:
            v.id = data["id"]
        return v
