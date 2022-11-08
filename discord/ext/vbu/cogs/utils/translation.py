import functools
from typing import Awaitable, Callable, Union, Coroutine
import gettext
import inspect

import discord
from discord.ext import commands
from contextvars import ContextVar


__all__ = (
    'translation',
    'i18n',
)


translator: ContextVar[Callable[[str], str]]
translator = ContextVar("translator", default=lambda s: s)


def translate_meta(val: str) -> str:
    return translator.get()(val)


def translation(
        ctx: Union[commands.Context, discord.Interaction, discord.Locale, str],
        domain: str,
        *,
        use_guild: bool = False,
        **kwargs,
        ) -> Union[gettext.GNUTranslations, gettext.NullTranslations]:
    """
    Get a translation table for a given domain with the locale
    stored in a context.

    Translations should be stored a la the following: ::

        root
        |-> cogs
        |-> config
        |-> locales
            |-> de
                |-> LC_MESSAGES
                    |-> foo.po
                    |-> bar.po
            |-> ru
                |-> LC_MESSAGES
                    |-> foo.po
                    |-> bar.po
            |-> foo.pot
            |-> bar.pot

    Examples
    ----------
    >>> # This will get the locale from your context,
    >>> # and will get the translation from the "errors" file.
    >>> vbu.translation(ctx, "errors").gettext("This command is currently unavailable")

    Parameters
    -----------
    ctx: Union[:class:`discord.ext.commands.Context`, :class:`discord.Interaction`, :class:`discord.Locale`, :class:`str`]
        The context that you want to get the translation within, or
        the name of the locale that you want to get anyway.
    domain: :class:`str`
        The domain of the translation.
    use_guild: :class:`bool`
        Whether or not to prioritize the guild locale over the user locale.

    Returns
    --------
    Union[:class:`gettext.GNUTranslations`, :class:`gettext.NullTranslations`]
        The transation table object that you want to ``.gettext`` for.
    """

    if isinstance(ctx, (commands.Context, discord.Interaction)):
        languages = [ctx.locale, ctx.locale.split("-")[0]]
        if use_guild and ctx.guild and ctx.guild_locale:
            languages = [
                ctx.guild_locale,
                ctx.guild_locale.split("-")[0],
                *languages,
            ]
    elif isinstance(ctx, discord.Locale):
        languages = [ctx.value, ctx.value.split("-")[0]]
    elif isinstance(ctx, str):
        languages = [ctx]
    else:
        raise TypeError()
    return gettext.translation(
        domain=domain,
        localedir=kwargs.get("localedir", "./locales"),
        languages=languages,
        fallback=kwargs.get("fallback", True),
    )


def i18n(i18n_name: str = "default", arg_index: Union[int, str] = 1):
    """
    Inject a ``_`` variable into a command's locals to allow for translation.

    .. versionadded:: 0.2.1

    Examples
    --------
    ::

        @commands.command()
        @vbu.i18n("example_commands")
        async def whatever(self, ctx: vbu.Context):
            await ctx.send(_("This text would be translated"))

    Parameters
    ----------
    i18n_name : str, optional
        The name of the file that you want to grab from. Defaults to ``default``
        if not provided.
    arg_index : Union[int, str], optional
        The index where the interaction or context object is stored.
        If this is a string, then that is used instead.
    """

    def inner(func):

        wrapper: Callable | Awaitable | Coroutine  # type: ignore

        if inspect.iscoroutinefunction(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                if isinstance(arg_index, int):
                    ctx = args[arg_index]
                else:
                    ctx = arg_index
                trans_func = translation(ctx, i18n_name).gettext
                translator.set(trans_func)
                func.__globals__["_"] = translate_meta
                return await func(*args, **kwargs)

        else:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if isinstance(arg_index, int):
                    ctx = args[arg_index]
                else:
                    ctx = arg_index
                trans_func = translation(ctx, i18n_name).gettext
                translator.set(trans_func)
                func.__globals__["_"] = translate_meta
                return func(*args, **kwargs)

        return wrapper
    return inner
