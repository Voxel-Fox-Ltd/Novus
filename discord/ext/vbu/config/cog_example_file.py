from discord.ext import commands, vbu


class PingCommand(vbu.Cog):

    @commands.command()
    async def ping(self, ctx: vbu.Context):
        """
        An example ping command.
        """

        if isinstance(ctx, vbu.SlashContext):
            await ctx.interaction.response.send_message("Pong!")
        else:
            await ctx.send("Pong!")


def setup(bot: vbu.Bot):
    x = PingCommand(bot)
    bot.add_cog(x)
