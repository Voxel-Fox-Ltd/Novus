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

from typing import Any, ClassVar, Iterable, Iterator

from typing_extensions import Self

from ...utils import MISSING, generate_repr
from ..emoji import PartialEmoji

__all__ = (
    'Component',
    'InteractableComponent',
    'LayoutComponentHolder',
)


class Component:
    """
    Abstract base class for all Discord UI components.
    """

    __slots__ = ()

    type: ClassVar[int]

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


class InteractableComponent(Component):
    """
    Abstract base class for Discord UI components that users can interact with.
    """

    custom_id: str

    __repr__ = generate_repr(('custom_id',))


class LayoutComponentIterator:

    def __init__(self, row: LayoutComponentHolder):
        self.row = row
        self.index = 0

    def __iter__(self) -> Iterator[Component]:
        return self

    def __next__(self) -> Component:
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


class LayoutComponentHolder(Component):
    """
    A generic layout component that holds other components.

    This class implements a ``__getitem__`` and an ``__iter__`` method to allow
    for eady indexing and iterating.

    Parameters
    ----------
    components : Iterable[novus.Component]
        A list of components to be initially added to the section.
        Only supports one to three text display components.
    accessory : novus.Component
        An accessory for the section.
        Only supports thumbnail or button components.

    Attributes
    ----------
    components : list[novus.Component | None]
        The components inside of the section.
    accessory : novus.Component | None
    """

    components: list[Component | None]

    def __init__(
            self,
            components: Iterable[Component] = MISSING):
        self.components = []
        if components:
            self.components.extend(components)

    def add(self, component: Component) -> Self:
        """
        Add a component to the end of the section.

        Parameters
        ----------
        component : novus.Component
            The component that you want to add to the section.

        Returns
        -------
        novus.LayoutComponentHolder
            The instance, allowing for easy chaining.
        """

        self.components.append(component)
        return self

    def set(self, index: int, component: Component | None) -> Self:
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
        novus.LayoutComponentHolder
            The instance, allowing for easy chaining.
        """

        while len(self.components) < index:
            self.components.append(None)
        self.components[index] = component
        return self

    def pop(self) -> Self:
        """
        Pop a component from the end of the instance.

        Returns
        -------
        novus.LayoutComponentHolder
            The instance, allowing for easy chaining.
        """

        self.components.pop()
        return self

    def clear(self) -> Self:
        """
        Clear all of the components from the instance.

        Returns
        -------
        novus.LayoutComponentHolder
            The instance, allowing for easy chaining.
        """

        self.components.clear()
        return self

    def __getitem__(self, index: int) -> Component | None:
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

    def __setitem__(self, index: int, value: Component | None) -> None:
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

    def __iter__(self) -> Iterator[Component]:
        """
        An iterator over the components of the instance.
        """

        return LayoutComponentIterator(self)

    # def _to_data(self) -> payloads.ActionRow:
    #     return {
    #         "type": self.type,
    #         "components": [
    #             i._to_data()
    #             for i in self.components
    #             if i is not None
    #         ]
    #     }

    # @classmethod
    # def _from_data(cls, data: payloads.ActionRow) -> Self:
    #     v = cls()
    #     from ._builder import component_builder
    #     for d in data["components"]:
    #         v.add(component_builder(d))  # pyright: ignore
    #     return v
