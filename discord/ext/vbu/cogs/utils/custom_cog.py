from __future__ import annotations

import typing
import logging
import re

import discord
from discord.ext import commands as _commands

from .redis import RedisChannelHandler

if typing.TYPE_CHECKING:
    from .custom_bot import Bot
    from .database import DatabaseWrapper


BotT = typing.TypeVar("BotT", bound="Bot")


class Cog(_commands.Cog, typing.Generic[BotT]):
    """
    A slightly modified cog class to allow for the ``cache_setup`` method and for the class' ``logger`` instance.

    Attributes:
        bot (Bot): The bot instance that the cog was added to.
        logger (logging.Logger): The logger that's assigned to the cog instance. This will be used
            for logging command calls, even if you choose not to use it yourself.
        qualified_name (str): The human-readable name for the cog.

            ::

                class MyCog(voxelbotutils.Cog): pass
                c = MyCog(bot)
                c.qualified_name  # "My Cog"

                class APICommands(voxelbotutils.Cog): pass
                c = APICommands(bot)
                c.qualified_name  # "API Commands"
    """

    def __init__(self, bot: BotT, logger_name: typing.Optional[str] = None):
        """
        Args:
            bot (Bot): The bot that should be added to the cog.
        """

        self.bot = bot
        bot_logger: logging.Logger = getattr(bot, "logger", logging.getLogger("bot"))
        if logger_name:
            self.logger = bot_logger.getChild(logger_name)
        else:
            self.logger = bot_logger.getChild(self.get_logger_name())

        # Add the cog instance to redis channel handlers
        for attr in dir(self):
            try:
                item = getattr(self, attr)
            except AttributeError:
                continue
            if isinstance(item, RedisChannelHandler):
                item.cog = self

    def get_logger_name(self, *prefixes, sep: str = '.') -> str:
        """
        Gets the name of the class with any given prefixes, with sep as a seperator. You
        tend to not need this yourself, but it is instead called internally by the bot
        when generating the :attr:`logger` instance.
        """

        return sep.join(['cog'] + list(prefixes) + [self.__cog_name__.replace(' ', '')])

    @property
    def qualified_name(self) -> str:
        """:meta private:"""

        return re.sub(
            r"(?:[A-Z])(?:(?:[a-z0-9])+|[A-Z]+$|[A-Z]+(?=[A-Z]))?", "\\g<0> ",
            super().qualified_name.replace(' ', '')
        ).strip()

    async def cache_setup(self, database: DatabaseWrapper):
        """
        A method that gets run when the bot's startup method is run -
        intended for setting up cached information in the bot object that aren't in the
        :attr:`voxelbotutils.Bot.guild_settings` or :attr:`voxelbotutils.Bot.user_settings`
        tables. This setup should *clear* your caches before setting them, as the :func:`voxelbotutils.Bot.startup`
        method may be called multiple times.
        """

        pass
