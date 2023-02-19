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
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

from typing_extensions import Self

from ...utils import generate_repr
from ..emoji import PartialEmoji

if TYPE_CHECKING:
    from ...enums import ComponentType

__all__ = (
    'Component',
    'LayoutComponent',
    'InteractableComponent',
)


class Component:
    """
    Abstract base class for all Discord UI components.
    """

    __slots__ = ()

    type: ClassVar[ComponentType]

    def _to_data(self) -> Any:
        raise NotImplementedError()

    @classmethod
    def _from_data(cls, data: Any) -> Self:
        raise NotImplementedError()


class ComponentEmojiMixin:

    _emoji: PartialEmoji | None

    @property
    def emoji(self) -> PartialEmoji | None:
        return self._emoji

    @emoji.setter
    def emoji(self, value: str | PartialEmoji | None) -> None:
        if value is None:
            self._emoji = None
        elif isinstance(value, PartialEmoji):
            self._emoji = value
        else:
            self._emoji = PartialEmoji.from_str(value)


class LayoutComponent(Component):
    """
    Abstract base class for Discord UI components dealing with layout.
    """

    __repr__ = generate_repr(('components',))


class InteractableComponent(Component):
    """
    Abstract base class for Discord UI components that users can interact with.
    """

    __repr__ = generate_repr(('custom_id',))
