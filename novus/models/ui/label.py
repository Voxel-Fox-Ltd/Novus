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
    "Label",
)


class Label(Component):
    """
    A top level layout component. Labels wrap modal components with text as a label.
    """

    type = ComponentType.LABEL

    label: str
    component: Component
    description: str

    def __init__(
            self,
            label: str,
            component: Component,
            description: str = MISSING):
        self.label = label
        self.component = component
        self.description = description

    @classmethod
    def from_payload(cls, payload: payloads.Label) -> Self:
        from ._builder import component_builder
        return cls(
            label=payload["label"],
            component=component_builder(payload["component"]),
            description=payload.get("description", MISSING),
        )

    def _to_data(self) -> payloads.Label:
        v: payloads.Label = {
            "type": self.type,
            "label": self.label,
            "component": self.component._to_data(),
        }
        if self.description is not MISSING:
            v["description"] = self.description
        return v
