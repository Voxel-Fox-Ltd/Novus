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

from typing import Optional
import json


class BaseComponent:
    """
    The base message component for Discord UI interactions.
    """

    def to_dict(self) -> dict:
        """
        Convert the current component object into a dictionary that we can
        send to Discord as a payload.
        """

        raise NotImplementedError()

    @classmethod
    def from_dict(cls, data: dict) -> 'BaseComponent':
        """
        Convert a response from the API into an object of this type.
        """

        raise NotImplementedError()

    def __eq__(self, other: 'BaseComponent') -> bool:
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


class DisableableComponent(BaseComponent):
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
    A message component that holds other message components.

    Attributes
    -----------
    components: :class:`discord.ui.BaseComponent`
        A list of the components that this component holder holds.
    """

    def __init__(self, *components: BaseComponent):
        self.components = list(components)

    def add_component(self, component: BaseComponent):
        """
        Adds a component to this holder.

        Parameters
        -----------
        component: :class:`discord.ui.BaseComponent`
            The component that you want to add.
        """

        self.components.append(component)
        return self

    def remove_component(self, component: BaseComponent):
        """
        Removes a component from this holder.

        Parameters
        -----------
        component: :class:`discord.ui.BaseComponent`
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

    def get_component(self, custom_id: str) -> Optional[BaseComponent]:
        """
        Get a component from the internal :attr:`components` list using its :attr:`custom_id` attribute.

        Parameters
        -----------
        custom_id: :class:`str`
            The ID of the component that you want to find.

        Returns
        --------
        Optional[:class:`discord.ui.BaseComponent`]
            The component that was found, if any.
        """

        for i in self.components:
            if isinstance(i, ComponentHolder):
                v = i.get_component(custom_id)
                if v:
                    return v
            else:
                if i.custom_id == custom_id:
                    return i
        return None
