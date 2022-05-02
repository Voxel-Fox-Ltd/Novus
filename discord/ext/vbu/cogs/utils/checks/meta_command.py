from discord.ext import commands


class InvokedMetaCommand(commands.CheckFailure):
    """
    Raised on any command decorated with :func:`voxelbotutils.checks.meta_command`.
    This stops users from running commands that you've made for internal use only, such as
    settings subcommands or commands that should only be invoked via
    :func:`discord.ext.commands.Bot.invoke`.
    """


def meta_command():
    """
    Stops users from being able to run this command.
    Should be caught and then reinvoked, or should have :attr:`Context.invoke_meta`
    set to `True`.

    Examples:

        ::

            @voxelbotutils.command()
            @voxelbotutils.checks.meta_command()
            async def notrunnable(self, ctx, *args):
                '''This command can't be run by normal users, and will fail silently...'''

                await ctx.send('uwu time gamers')

            @voxelbotutils.command()
            async def runnable(self, ctx):
                '''But you can still run the command like this.'''

                ctx.invoke_meta = True
                await ctx.invoke(ctx.bot.get_command('notrunnable'))

    Raises:
        InvokedMetaCommand: If the command was run without the meta tag being set.
    """

    def predicate(ctx):
        if getattr(ctx, 'invoke_meta', False):
            return True
        raise InvokedMetaCommand()
    return commands.check(predicate)
