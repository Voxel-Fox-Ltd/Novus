from discord.ext import commands

from . import utils as vbu


class MiscCommands(vbu.Cog):

    @vbu.command(aliases=['support', 'guild'], add_slash_command=False)
    @vbu.checks.is_config_set('command_data', 'guild_invite')
    @commands.bot_has_permissions(send_messages=True)
    async def server(self, ctx: vbu.Context):
        """
        Gives the invite to the support server.
        """

        await ctx.send(f"{self.bot.config['command_data']['guild_invite']}")

    @vbu.command(aliases=['patreon'], add_slash_command=False)
    @vbu.checks.is_config_set('command_data', 'donate_link')
    @commands.bot_has_permissions(send_messages=True)
    async def donate(self, ctx: vbu.Context):
        """
        Gives you the bot's creator's donate link.
        """

        await ctx.send(f"{self.bot.config['command_data']['donate_link']}")

    @vbu.command(add_slash_command=False)
    @commands.bot_has_permissions(send_messages=True)
    @vbu.checks.is_config_set('command_data', 'website_link')
    async def website(self, ctx: vbu.Context):
        """
        Gives you a link to the bot's website.
        """

        await ctx.send(f"{self.bot.config['command_data']['website_link']}")


def setup(bot: vbu.Bot):
    x = MiscCommands(bot)
    bot.add_cog(x)
