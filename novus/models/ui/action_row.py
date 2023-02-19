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

from typing import TYPE_CHECKING, Iterable, Iterator

from typing_extensions import Self

from ...enums import ComponentType
from ...utils import MISSING
from .component import InteractableComponent, LayoutComponent

if TYPE_CHECKING:
    from ... import payloads

__all__ = (
    'ActionRow',
)


class ActionRowIterator:

    def __init__(self, row: ActionRow):
        self.row = row
        self.index = 0

    def __iter__(self) -> Iterator[InteractableComponent]:
        return self

    def __next__(self) -> InteractableComponent:
        try:
            d = self.row[self.index]
            if d is None:
                raise ValueError
        except ValueError:
            self.index += 1
            return self.__next__()
        except IndexError:
            raise StopIteration
        else:
            self.index += 1
            return d


class ActionRow(LayoutComponent):
    """
    A generic layout component that holds other components.

    This class implements a ``__getitem__`` and an ``__iter__`` method to allow
    for eady indexing and iterating.

    Parameters
    ----------
    components : Iterable[novus.Component]
        A list of components to be initially added to the action row.

    Attributes
    ----------
    components : list[novus.Component | None]
        The components inside of the action row.
    """

    type = ComponentType.action_row

    components: list[InteractableComponent | None]

    def __init__(self, components: Iterable[InteractableComponent] = MISSING):
        self.components = []
        if components:
            self.components.extend(components)

    def add(self, component: InteractableComponent) -> Self:
        """
        Add a component to the end of the action row.

        Parameters
        ----------
        component : novus.Component
            The component that you want to add to the action row.

        Returns
        -------
        novus.ActionRow
            The action row instance, allowing for easy chaining.
        """

        self.components.append(component)
        return self

    def set(self, index: int, component: InteractableComponent | None) -> Self:
        """
        Set a component at a specified index. If the index given is larger than
        the current number of components, the components list will be filled
        with ``None`` values, which will be removed upon sending.

        Parameters
        ----------
        index : int
            The index that you want to set the component at.
        component: novus.Component | None
            The component that you want to set.

        Returns
        -------
        novus.ActionRow
            The action row instance, allowing for easy chaining.
        """

        while len(self.components) < index:
            self.components.append(None)
        self.components[index] = component
        return self

    def pop(self) -> Self:
        """
        Pop a component from the end of the action row.

        Returns
        -------
        novus.ActionRow
            The action row instance, allowing for easy chaining.
        """

        self.components.pop()
        return self

    def clear(self) -> Self:
        """
        Clear all of the components from the action row.

        Returns
        -------
        novus.ActionRow
            The action row instance, allowing for easy chaining.
        """

        self.components.clear()
        return self

    def __getitem__(self, index: int) -> InteractableComponent | None:
        """
        Get an item at the specified index.

        Parameters
        ----------
        index : int
            The index that you want to get the component at.

        Returns
        -------
        novus.Component | None
            The item at the index.

        Raises
        ------
        IndexError
            If the given index does not exist.
        """

        return self.components[index]

    def __setitem__(self, index: int, value: InteractableComponent | None) -> None:
        """
        Set an item at the specified index.

        Parameters
        ----------
        index : int
            The index that you want to set the component at.
        component: novus.Component | None
            The component that you want to set.
        """

        self.set(index, value)

    def __iter__(self) -> Iterator[InteractableComponent]:
        """
        An iterator over the components of the action row.
        """

        return ActionRowIterator(self)

    def _to_data(self) -> payloads.ActionRow:
        return {
            "type": self.type.value,
            "components": [
                i._to_data()
                for i in self.components
                if i is not None
            ]
        }

    @classmethod
    def _from_data(cls, data: payloads.ActionRow) -> Self:
        v = cls()
        from ._builder import component_builder
        for d in data["components"]:
            v.add(component_builder(d))  # pyright: ignore
        return v
