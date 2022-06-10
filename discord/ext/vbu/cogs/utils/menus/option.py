from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Awaitable,
    Callable,
    Any,
    Union,
    Tuple,
    Optional,
    List,
)

import discord
from discord.ext import commands

from .errors import ConverterFailure
from .mixins import MenuDisplayable
from .utils import async_wrap_callback

if TYPE_CHECKING:
    from .menu import Menu
    from .converter import Converter
    from ..custom_context import SlashContext
    AnyContext = Union[
        SlashContext,
        commands.SlashContext,
    ]
    Callback = Union[
        Callable[[AnyContext, List[Any]], Awaitable[None]],
        Callable[[AnyContext, List[Any]], None],
    ]


class Option(MenuDisplayable):
    """
    An object for use in menus so as to represent one of the clickable options in the settings menus.
    """

    def __init__(
            self,
            display: Optional[Union[str, Callable[[SlashContext], str]]],
            component_display: Optional[Union[str, Tuple[str, str]]] = None,
            converters: Optional[List[Converter]] = None,
            callback: Optional[Union[Callback, Menu]] = None,
            cache_callback: Optional[Callback] = None,
            allow_none: bool = False):
        """
        Attributes
        ----------
        display : Union[str, Callable[[commands.SlashContext], str]]
            The text that will be shown on the menu itself.
            If a string is passed, then it will be given ``.format(ctx)``.
            If a method is passed, then it will be given a
            :class:`discord.ext.commands.SlashContext` object as an argument.
        component_display : str
            The string that gets shown in the button for this option.
        converters : Optional[List[Converter]]
            A list of converters that the user should be asked for.
        callback : Callable[[commands.SlashContext, List[Any]], None]
            An [async] function that will be given the context object
            and a list of the converted user-provided arguments.
        cache_callback : Optional[Callable[[commands.SlashContext, List[Any]], None]]
            An [async] function that will be given the context object and a list of the
            converted user-provided arguments. This is provided as well as the
            :code:`callback` parameter so as to allow for the seperation of
            different reusable methods.
        allow_none : bool
            Whether or not the option should allow ``None`` as a valid input.

        Parameters
        ----------
        display : Optional[Union[str, Callable[[SlashContext], str]]]
            The text that will be shown on the menu itself.
            If a string is passed, then it will be given ``.format(ctx)``.
            If a method is passed, then it will be given a
            :class:`discord.ext.commands.SlashContext` object as an argument.
            If ``None`` is passed then no text will be displayed in the menu
            for this option.
        component_display : str
            The string that gets shown in the button for this option.
        converters : Optional[Optional[List[Converter]]]
            A list of converters that the user should be asked for.
        callback : Optional[Union[Callable[[SlashContext, List[Any]], MaybeCoro[None]], Menu]]
            An [async] function that will be given the context object
            and a list of the converted user-provided arguments.
        cache_callback : Optional[Optional[Callable[[SlashContext, List[Any]], MaybeCoro[None]]]]
            An [async] function that will be given the context object and a list of the
            converted user-provided arguments. This is provided as well as the
            :code:`callback` parameter so as to allow for the seperation of
            different reusable methods.
        allow_none : Optional[bool]
            Whether or not the option should allow ``None`` as a valid input.
        """

        self.display: Optional[Union[str, Callable[[SlashContext], str]]] = display

        self.component_display: str
        self._component_custom_id: str
        new_component_display = component_display or display
        if isinstance(new_component_display, (list, tuple)):
            self._component_custom_id = str(new_component_display[1])
            self.component_display = str(new_component_display[0])
        elif isinstance(new_component_display, str):
            self.component_display = new_component_display
            self._component_custom_id = str(new_component_display)
        else:
            raise TypeError("Cannot assign component display to a callable")

        self._button_style: Optional[discord.ButtonStyle] = None
        self.converters: List[Converter] = converters or list()
        self._callback = callback
        self.callback = async_wrap_callback(callback)
        self._cache_callback = cache_callback
        self.cache_callback = async_wrap_callback(cache_callback)
        self.allow_none: bool = allow_none

    async def run(self, ctx: commands.SlashContext):
        """
        Runs the converters and callback for this given option.
        """

        data = []
        messages_to_delete = []
        has_failed = False
        for i in self.converters:
            try:
                data.append(await i.run(ctx, messages_to_delete))
                if data[-1] is None and not self.allow_none:
                    has_failed = True
                    break
            except ConverterFailure:
                has_failed = True
                break
        if not has_failed:
            await self.callback(ctx, data)
            await self.cache_callback(ctx, data)
