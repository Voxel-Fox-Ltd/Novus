from discord.ext import commands

from . import utils as vbu


class Help(vbu.Cog):

    def __init__(self, bot: vbu.Bot):
        super().__init__(bot)
        self._original_help_command = bot.help_command
        bot.help_command = vbu.HelpCommand()
        bot.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command = self._original_help_command

    @vbu.command(name="commands", hidden=True, add_slash_command=False)
    async def _commands(self, ctx: vbu.Context, *args):
        """
        An alias for help.
        """

        return await ctx.send_help(*args)

    @vbu.command(hidden=True, add_slash_command=False)
    @commands.has_permissions(manage_messages=True)
    async def channelhelp(self, ctx: vbu.Context, *args):
        """
        An alias for help that outputs into the current channel.
        """

        return await ctx.send_help(*args)


def setup(bot: vbu.Bot):
    x = Help(bot)
    bot.add_cog(x)
