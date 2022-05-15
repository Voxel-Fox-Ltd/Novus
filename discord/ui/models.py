"""
The MIT License (MIT)

Copyright (c) 2021-present Kae Bartlett

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from __future__ import annotations

from typing import Optional, Union, List
import json


class InteractedComponent:
    """
    A small component key: value store for components given back to the bot
    via the API. Should not be initialised yourself.

    .. versionadded:: 0.0.5

    Attributes
    ------------
    custom_id: Optional[:class:`str`]
        The custom ID given to the component.
    components: Optional[List[:class:`InteractionComponent`]]
        The components that are children of this component.
    value: Optional[:class:`str`]
        The value that the component was given.
    type: Optional[:class:`int`]
        The type of the component.
    """

    def __init__(self, *, custom_id: str = None, components: List[InteractedComponent] = None, value: str = None, type: int = None):
        self.custom_id = custom_id
        self.components = components
        self.value = value
        self.type = type

    def __repr__(self) -> str:
        attrs = (
            ('custom_id', self.custom_id),
            ('components', self.components),
            ('value', self.value),
        )
        inner = ' '.join('%s=%r' % t for t in attrs)
        return f'{self.__class__.__name__}({inner})'

    @classmethod
    def from_data(cls, payload: dict):
        components = None
        if "components" in payload:
            components = [InteractedComponent.from_data(i) for i in payload["components"]]
        return cls(
            custom_id=payload.get("custom_id"),
            type=payload.get("type"),
            components=components,
            value=payload.get("value"),
        )

    def get_component(self, custom_id: str) -> Optional[InteractedComponent]:
        """
        Search down through the component store for a given custom ID.

        .. versionadded:: 0.0.6

        Parameters
        -----------
        custom_id: :class:`str`
            The custom ID that you want to serach for.

        Returns
        --------
        Optional[:class:`InteractedComponent`]
            The component that was found.
        """

        if self.custom_id == custom_id:
            return self
        if self.components:
            for c in self.components:
                s = c.get_component(custom_id)
                if s:
                    return s
        return None

class BaseComponent:
    """
    The base message component for Discord UI interactions. All other components must inherit from this.
    """

    def to_dict(self) -> dict:
        """
        Convert the current component object into a dictionary that we can
        send to Discord as a payload.
        """

        raise NotImplementedError()

    @classmethod
    def from_dict(cls, data: dict) -> BaseComponent:
        """
        Convert a response from the API into an object of this type.
        """

        raise NotImplementedError()

    def __eq__(self, other: BaseComponent) -> bool:
        """
        Checks if two components are equal to one another.
        """

        if not isinstance(other, BaseComponent):
            return False
            # raise TypeError("Can't compare {} and {}".format(self.__class__, other.__class__))
        return self.to_dict() == other.to_dict()

    def __hash__(self):
        """:meta private:"""

        return hash(json.dumps(self.to_dict(), sort_keys=True))


class InteractableComponent(BaseComponent):
    """
    A component that users are able to interact with. Used as a base for all
    components that are interacted with.
    """

    custom_id: str


class LayoutComponent(BaseComponent):
    """
    A component for structuring the layout of other components.
    """

    pass


class DisableableComponent(InteractableComponent):
    """
    A message component that has a `disabled` flag.
    """

    def disable(self) -> None:
        """
        Set the disabled flag on the current component.
        """

        self.disabled = True

    def enable(self) -> None:
        """
        Unset the disabled flag on the current component.
        """

        self.disabled = False


class ComponentHolder(BaseComponent):
    """
    A mixin for components that hold other components.

    Attributes
    -----------
    components: Union[:class:`discord.ui.InteractableComponent`, :class:`discord.ui.LayoutComponent`]
        A list of the components that this component holder holds.
    """

    def __init__(self, *components: Union[InteractableComponent, LayoutComponent]):
        self.components = list(components)

    def __repr__(self) -> str:
        attrs = (
            ('components', self.components),
        )
        inner = ' '.join('%s=%r' % t for t in attrs)
        return f'{self.__class__.__name__}({inner})'

    def add_component(self, component: Union[InteractableComponent, LayoutComponent]):
        """
        Adds a component to this holder.

        Parameters
        -----------
        component: Union[:class:`discord.ui.InteractableComponent`, :class:`discord.ui.LayoutComponent`]
            The component that you want to add.
        """

        self.components.append(component)
        return self

    def remove_component(self, component: Union[InteractableComponent, LayoutComponent]):
        """
        Removes a component from this holder.

        Parameters
        -----------
        component: Union[:class:`discord.ui.InteractableComponent`, :class:`discord.ui.LayoutComponent`]
            The component that you want to remove.
        """

        self.components.remove(component)
        return self

    def disable_components(self):
        """
        Disables all of the components inside this component holder that
        inherit from :class:`discord.ui.DisableableComponent`.
        """

        for i in self.components:
            if isinstance(i, ComponentHolder):
                i.disable_components()
            elif isinstance(i, DisableableComponent):
                i.disable()
        return self

    def enable_components(self):
        """
        Enables all of the components inside this component holder that
        inherit from :class:`discord.ui.DisableableComponent`.
        """

        for i in self.components:
            if isinstance(i, ComponentHolder):
                i.enable_components()
            elif isinstance(i, DisableableComponent):
                i.enable()
        return self

    def get_component(self, custom_id: str) -> Optional[InteractableComponent]:
        """
        Get a component from the internal :attr:`components` list using its :attr:`custom_id` attribute.

        Parameters
        -----------
        custom_id: :class:`str`
            The ID of the component that you want to find.

        Returns
        --------
        Optional[:class:`discord.ui.InteractableComponent`]
            The component that was found, if any.
        """

        for i in self.components:
            if isinstance(i, ComponentHolder):
                v = i.get_component(custom_id)
                if v:
                    return v
            elif isinstance(i, InteractableComponent):
                if i.custom_id == custom_id:
                    return i
            elif type(i) == BaseComponent:
                if getattr(i, "custom_id", None) == custom_id:
                    return i
            else:
                raise TypeError(f"Invalid component type {i.__class__}")
        return None
