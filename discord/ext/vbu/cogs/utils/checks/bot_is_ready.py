from discord.ext import commands


class BotNotReady(commands.CheckFailure):
    """
    The generic error for the bot failing the :func:`voxelbotutils.checks.bot_is_ready` check.
    """


def bot_is_ready():
    """
    The check for whether or not the bot has processed all of its startup methods (as defined by
    the :attr:`Bot.startup_method` task being completed), as well as having populated the cache
    (as defined by Discord.py having set :attr:`discord.ext.commands.Bot.is_ready` to true).

    Raises:
        BotNotReady: If the bot isn't yet marked as ready.
    """

    async def predicate(ctx: commands.Context):
        if ctx.bot.is_ready() and (ctx.bot.startup_method is None or ctx.bot.startup_method.done()):
            return True
        raise BotNotReady("The bot isn't marked as ready to process commands yet - please wait a minute or so.")
    return commands.check(predicate)
