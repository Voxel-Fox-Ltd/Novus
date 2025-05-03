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

from collections.abc import Generator
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models import InteractableComponent, LayoutComponentHolder

__all__ = (
    'walk_components',
)


def walk_components(holders: list[LayoutComponentHolder] | None) -> Generator[InteractableComponent, None, None]:
    if holders is None:
        return
    for actionrow in holders:
        for component in actionrow:
            if hasattr(component, "custom_id"):
                yield component  # pyright: ignore
            if hasattr(component, "components"):
                yield from walk_components([component])  # pyright: ignore
