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
from ...utils import MISSING, generate_repr
from .component import ComponentEmojiMixin, InteractableComponent

if TYPE_CHECKING:
    from ... import ChannelType, PartialEmoji, payloads

__all__ = (
    'SelectOption',
    'StringSelectMenu',
    'UserSelectMenu',
    'RoleSelectMenu',
    'MentionableSelectMenu',
    'ChannelSelectMenu',
)


class SelectMenu(InteractableComponent):
    """
    Any generic select menu component.
    """

    __slots__ = (
        'custom_id',
        'placeholder',
        'min_values',
        'max_values',
        'disabled',
    )

    placeholder: str | None
    min_values: int
    max_values: int
    disabled: bool

    def __init__(
            self,
            *,
            custom_id: str,
            placeholder: str | None = None,
            min_values: int = 1,
            max_values: int = 1,
            disabled: bool = False):
        self.custom_id = custom_id
        self.placeholder = placeholder
        self.min_values = min_values
        self.max_values = max_values
        self.disabled = disabled

    def _to_data(self) -> payloads.SelectMenu:
        v: payloads.SelectMenu = {
            "type": self.type.value,
            "custom_id": self.custom_id,
            "min_values": self.min_values,
            "max_values": self.max_values,
            "disabled": self.disabled,
        }
        if self.placeholder:
            v["placeholder"] = self.placeholder
        return v

    @classmethod
    def _from_data(cls, data: payloads.SelectMenu) -> Self:
        return cls(
            custom_id=data["custom_id"],
            placeholder=data.get("placeholder"),
            min_values=data.get("min_values", 1),
            max_values=data.get("max_values", 1),
            disabled=data.get("disabled", False),
        )


class SelectOption(ComponentEmojiMixin):
    """
    An option inside of a select menu.

    Parameters
    ----------
    label : str
        The label shown on the option.
    value : str
        The value given back to your application when selected.
    description : str
        The description shown on the option.
    emoji : novus.PartialEmoji | novus.Emoji | str
        The emoji shown on the option.
    default : bool
        Whether the option is selected by default or not.

    Attributes
    ----------
    label : str
        The label shown on the option.
    value : str
        The value given back to your application when selected.
    description : str | None
        The description shown on the option.
    emoji : novus.PartialEmoji | novus.Emoji | None
        The emoji shown on the option.
    default : bool
        Whether the option is selected or not.
    """

    __slots__ = (
        'label',
        'value',
        'description',
        'default',
        '_emoji',
    )

    label: str
    value: str
    description: str | None
    default: bool
    emoji: PartialEmoji | None  # From mixin

    def __init__(
            self,
            label: str,
            value: str,
            *,
            emoji: str | PartialEmoji | None = None,
            description: str | None = None,
            default: bool = False):
        self.label = label
        self.value = value
        self.emoji = emoji  # pyright: ignore
        self.description = description
        self.default = default

    __repr__ = generate_repr(('label', 'value',))

    @classmethod
    def _from_data(cls, data: payloads.SelectOption) -> Self:
        emoji_data = data.get("emoji")
        if emoji_data:
            emoji_object = PartialEmoji(data=emoji_data)
        else:
            emoji_object = None
        return cls(
            label=data["label"],
            value=data["value"],
            emoji=emoji_object,
            description=data.get("description"),
            default=data.get("default", False),
        )

    def _to_data(self) -> payloads.SelectOption:
        v: payloads.SelectOption = {
            "label": self.label,
            "value": self.value,
            "default": self.default,
        }
        if self.emoji:
            v["emoji"] = self.emoji._to_data()
        if self.description:
            v["description"] = self.description
        return v


class StringSelectIterator:

    def __init__(self, row: StringSelectMenu):
        self.row = row
        self.index = 0

    def __iter__(self) -> Iterator[SelectOption]:
        return self

    def __next__(self) -> SelectOption:
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


class StringSelectMenu(SelectMenu):
    """
    A string select menu component.

    Parameters
    ----------
    options : Iterable[SelectOption]
        A list of options to be added to the select menu by default.
    custom_id : str
        The custom ID for the menu.
    placeholder : str | None
        Placeholder text to be shown in the menu when nothing is selected.
    min_values : int | None
        The minimum number of values to be selected before the menu will submit.
    max_values : int | None
        The maximum number of values to be selected before the menu will submit.
    disabled : bool
        If the component is disabled.

    Attributes
    ----------
    options : list[SelectOption]
        A list of options to be added to the select menu by default.
    custom_id : str
        The custom ID for the menu.
    placeholder : str | None
        Placeholder text to be shown in the menu when nothing is selected.
    min_values : int
        The minimum number of values to be selected before the menu will submit.
    max_values : int
        The maximum number of values to be selected before the menu will submit.
    disabled : bool
        If the component is disabled.
    """

    __slots__ = (
        'options',
        'custom_id',
        'placeholder',
        'min_values',
        'max_values',
        'disabled',
    )

    type = ComponentType.string_select
    options: list[SelectOption | None]

    def __init__(
            self,
            *,
            options: Iterable[SelectOption] = MISSING,
            custom_id: str,
            placeholder: str | None = None,
            min_values: int = 1,
            max_values: int = 1,
            disabled: bool = False):
        super().__init__(
            custom_id=custom_id,
            placeholder=placeholder,
            min_values=min_values,
            max_values=max_values,
            disabled=disabled,
        )
        self.options = []
        if options:
            self.options.extend(options)

    __repr__ = generate_repr(('custom_id', 'options',))

    def add(self, option: SelectOption) -> Self:
        """
        Add an option to the select menu.

        Parameters
        ----------
        option: novus.SelectOption
            The option that you want to add.

        Returns
        -------
        novus.StringSelectMenu
            The menu instance, allowing for easy chaining.
        """

        self.options.append(option)
        return self

    def set(self, index: int, component: SelectOption | None) -> Self:
        """
        Set an option at a specified index. If the index given is larger than
        the current number of components, the components list will be filled
        with ``None`` values, which will be removed upon sending.

        Parameters
        ----------
        index : int
            The index that you want to set the component at.
        component: novus.SelectOption | None
            The option that you want to set.

        Returns
        -------
        novus.StringSelectMenu
            The menu instance, allowing for easy chaining.
        """

        while len(self.options) < index:
            self.options.append(None)
        self.options[index] = component
        return self

    def pop(self) -> Self:
        """
        Pop an from the end of the menu.

        Returns
        -------
        novus.StringSelectMenu
            The menu instance, allowing for easy chaining.
        """

        self.options.pop()
        return self

    def clear(self) -> Self:
        """
        Clear all of the options from the menu.

        Returns
        -------
        novus.StringSelectMenu
            The menu instance, allowing for easy chaining.
        """

        self.options.clear()
        return self

    def __getitem__(self, index: int) -> SelectOption | None:
        """
        Get an option at the specified index.

        Parameters
        ----------
        index : int
            The index that you want to get the option at.

        Returns
        -------
        novus.SelectOption | None
            The item at the index.

        Raises
        ------
        IndexError
            If the given index does not exist.
        """

        return self.options[index]

    def __setitem__(self, index: int, value: SelectOption | None) -> None:
        """
        Set an item at the specified index.

        Parameters
        ----------
        index : int
            The index that you want to set the option at.
        component: novus.SelectOption | None
            The option that you want to set.
        """

        self.set(index, value)

    def __iter__(self) -> Iterator[SelectOption]:
        """
        An iterator over the options of the select menu.
        """

        return StringSelectIterator(self)

    def _to_data(self) -> payloads.SelectMenu:
        v = super()._to_data()
        options: list[payloads.SelectOption] = []
        for i in self.options:
            if i is None:
                continue
            options.append(i._to_data())
        v["options"] = options
        return v

    @classmethod
    def _from_data(cls, data: payloads.SelectMenu) -> Self:
        option_data = data.get("options")
        if option_data:
            option_object = [SelectOption._from_data(d) for d in option_data]
        else:
            option_object = []
        v = super()._from_data(data)
        v.options.extend(option_object)
        return v


class UserSelectMenu(SelectMenu):
    """
    A select menu for users within a guild.

    Parameters
    ----------
    custom_id : str
        The custom ID for the menu.
    placeholder : str | None
        Placeholder text to be shown in the menu when nothing is selected.
    min_values : int | None
        The minimum number of values to be selected before the menu will submit.
    max_values : int | None
        The maximum number of values to be selected before the menu will submit.
    disabled : bool
        If the component is disabled.

    Attributes
    ----------
    custom_id : str
        The custom ID for the menu.
    placeholder : str | None
        Placeholder text to be shown in the menu when nothing is selected.
    min_values : int
        The minimum number of values to be selected before the menu will submit.
    max_values : int
        The maximum number of values to be selected before the menu will submit.
    disabled : bool
        If the component is disabled.
    """

    type = ComponentType.user_select


class RoleSelectMenu(SelectMenu):
    """
    A select menu for roles within a guild.

    Parameters
    ----------
    custom_id : str
        The custom ID for the menu.
    placeholder : str | None
        Placeholder text to be shown in the menu when nothing is selected.
    min_values : int | None
        The minimum number of values to be selected before the menu will submit.
    max_values : int | None
        The maximum number of values to be selected before the menu will submit.
    disabled : bool
        If the component is disabled.

    Attributes
    ----------
    custom_id : str
        The custom ID for the menu.
    placeholder : str | None
        Placeholder text to be shown in the menu when nothing is selected.
    min_values : int
        The minimum number of values to be selected before the menu will submit.
    max_values : int
        The maximum number of values to be selected before the menu will submit.
    disabled : bool
        If the component is disabled.
    """

    type = ComponentType.role_select


class MentionableSelectMenu(SelectMenu):
    """
    A select menu for both roles and users within a guild.

    Parameters
    ----------
    custom_id : str
        The custom ID for the menu.
    placeholder : str | None
        Placeholder text to be shown in the menu when nothing is selected.
    min_values : int | None
        The minimum number of values to be selected before the menu will submit.
    max_values : int | None
        The maximum number of values to be selected before the menu will submit.
    disabled : bool
        If the component is disabled.

    Attributes
    ----------
    custom_id : str
        The custom ID for the menu.
    placeholder : str | None
        Placeholder text to be shown in the menu when nothing is selected.
    min_values : int
        The minimum number of values to be selected before the menu will submit.
    max_values : int
        The maximum number of values to be selected before the menu will submit.
    disabled : bool
        If the component is disabled.
    """

    type = ComponentType.mentionable_select


class ChannelSelectMenu(SelectMenu):
    """
    A select menu for channels within a guild.

    Parameters
    ----------
    custom_id : str
        The custom ID for the menu.
    placeholder : str | None
        Placeholder text to be shown in the menu when nothing is selected.
    min_values : int | None
        The minimum number of values to be selected before the menu will submit.
    max_values : int | None
        The maximum number of values to be selected before the menu will submit.
    disabled : bool
        If the component is disabled.

    Attributes
    ----------
    custom_id : str
        The custom ID for the menu.
    placeholder : str | None
        Placeholder text to be shown in the menu when nothing is selected.
    min_values : int
        The minimum number of values to be selected before the menu will submit.
    max_values : int
        The maximum number of values to be selected before the menu will submit.
    disabled : bool
        If the component is disabled.
    """

    type = ComponentType.channel_select
    channel_types: list[ChannelType]

    def __init__(
            self,
            *,
            channel_types: Iterable[ChannelType] = MISSING,
            custom_id: str,
            placeholder: str | None = None,
            min_values: int = 1,
            max_values: int = 1,
            disabled: bool = False):
        super().__init__(
            custom_id=custom_id,
            placeholder=placeholder,
            min_values=min_values,
            max_values=max_values,
            disabled=disabled,
        )
        self.channel_types = []
        if channel_types:
            self.channel_types.extend(channel_types)

    __repr__ = generate_repr(('custom_id', 'channel_types',))

    def _to_data(self) -> payloads.SelectMenu:
        v = super()._to_data()
        channel_types: list[int] = []
        for i in self.channel_types:
            if i is None:
                continue
            channel_types.append(i.value)
        if channel_types:
            v["channel_types"] = channel_types
        return v

    @classmethod
    def _from_data(cls, data: payloads.SelectMenu) -> Self:
        type_data = data.get("channel_types")
        if type_data:
            type_object = [ChannelType(d) for d in type_data]
        else:
            type_object = []
        v = super()._from_data(data)
        v.channel_types.extend(type_object)
        return v
