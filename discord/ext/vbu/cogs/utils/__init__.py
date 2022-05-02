import re as _re
import gettext as _gettext
import typing as _typing

import discord as _discord
from discord.ext import commands as _dpy_commands

from . import checks, converters, errors, menus, types
from .context_embed import Embed
from .custom_bot import MinimalBot, Bot
from .custom_cog import Cog
from .custom_command import Command, Group
from .custom_context import Context, AbstractMentionable, PrintContext, SlashContext
from .database import DatabaseWrapper, DatabaseTransaction
from .redis import RedisConnection, RedisChannelHandler, redis_channel_handler
from .statsd import StatsdConnection
from .time_value import TimeValue
from .paginator import Paginator
from .help_command import HelpCommand
from .string import Formatter
from .component_check import component_check
from .embeddify import Embeddify
from .twitch_stream import TwitchStream


def command(*args, **kwargs):
    return _dpy_commands.command(*args, cls=Command, **kwargs)


def group(*args, **kwargs):
    if 'case_insensitive' not in kwargs:
        kwargs['case_insensitive'] = True
    return _dpy_commands.group(*args, cls=Group, **kwargs)


_html_minifier = _re.compile(r"\s{2,}|\n")


def minify_html(text: str) -> str:
    return _html_minifier.sub("", text)


def translation(
        ctx: _typing.Union[_dpy_commands.Context, _discord.Interaction, str],
        domain: str,
        *,
        use_guild: bool = False,
        **kwargs,
        ) -> _typing.Union[_gettext.GNUTranslations, _gettext.NullTranslations]:
    """
    Get a translation table for a given domain with the locale
    stored in a context.

    Examples
    ----------
    >>> # This will get the locale from your context,
    >>> # and will get the translation from the "errors" file.
    >>> vbu.translation(ctx, "errors").gettext("This command is currently unavailable")

    Parameters
    -----------
    ctx: Union[:class:`discord.ext.commands.Context`, :class:`discord.Interaction`, :class:`str`]
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

    if isinstance(ctx, (_dpy_commands.Context, _discord.Interaction)):
        languages = [ctx.locale, ctx.locale.split("-")[0]]
        if use_guild and ctx.guild and ctx.guild_locale:
            languages = [ctx.guild_locale, ctx.guild_locale.split("-")[0], *languages]
    elif isinstance(ctx, str):
        languages = [ctx]
    else:
        raise TypeError()
    return _gettext.translation(
        domain=domain,
        localedir=kwargs.get("localedir", "./locales"),
        languages=languages,
        fallback=kwargs.get("fallback", True),
    )


_formatter = Formatter()
format = _formatter.format
embeddify = Embeddify.send
DatabaseConnection = DatabaseWrapper
Database = DatabaseWrapper
Redis = RedisConnection
Stats = StatsdConnection
