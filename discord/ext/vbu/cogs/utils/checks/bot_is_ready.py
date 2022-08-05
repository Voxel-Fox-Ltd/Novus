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

    error_text = "The bot isn't marked as ready to process commands yet - please wait a minute or so."

    async def predicate(ctx: commands.Context):
        if not (ctx.bot.startup_method is None or ctx.bot.startup_method.done()):
            raise BotNotReady(error_text)
        if getattr(ctx.bot, "is_interactions_only", False) or ctx.bot.is_ready():
            return True
        raise BotNotReady(error_text)
    return commands.check(predicate)
