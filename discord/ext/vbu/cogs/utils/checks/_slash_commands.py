from discord.ext import commands


class IsSlashCommand(commands.DisabledCommand):
    """Raised when a given command failes the :func:`voxelbotutils.checks.is_not_slash_command` check."""


class IsNotSlashCommand(commands.DisabledCommand):
    """Raised when a given command failes the :func:`voxelbotutils.checks.is_slash_command` check."""


class BotNotInGuild(commands.DisabledCommand):
    """Raised when a given command failes the :func:`voxelbotutils.checks.bot_in_guild` check."""


def is_slash_command():
    """
    Checks that the command has been invoked from a slash command.

    Raises:
        IsNotSlashCommand: If the command was not run as a slash command.
    """

    async def predicate(ctx):
        if ctx.is_interaction:
            return True
        raise IsNotSlashCommand()
    return commands.check(predicate)


def is_not_slash_command():
    """
    Checks that the command has not been invoked from a slash command.

    Raises:
        IsSlashCommand: If the command was run as a slash command.
    """

    async def predicate(ctx):
        if not ctx.is_interaction:
            return True
        raise IsSlashCommand()
    return commands.check(predicate)


def bot_in_guild():
    """
    Checks that the bot is in the guild where this command is being called.

    Raises:
        BotNotInGuild: If the bot isn't in the guild where the command is being called.
    """

    async def predicate(ctx):
        if ctx.bot.get_guild(ctx.guild.id) is None:
            raise BotNotInGuild()
        return True
    return commands.check(predicate)
