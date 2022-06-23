import discord
from discord.ext import commands

from . import utils as vbu


_ = vbu.translation


class BotSettings(vbu.Cog):

    @commands.command(add_slash_command=False)
    @commands.bot_has_permissions(send_messages=True)
    @commands.guild_only()
    @vbu.checks.is_config_set('database', 'enabled')
    async def prefix(self, ctx: vbu.Context, *, new_prefix: str = None):
        """
        Changes the prefix that the bot uses.
        """

        # See if the prefix was actually specified
        prefix_column = self.bot.config.get('guild_settings_prefix_column', 'prefix')
        if new_prefix is None:
            current_prefix = self.bot.guild_settings[ctx.guild.id][prefix_column] or self.bot.config['default_prefix']
            return await ctx.send(
                _(ctx, "bot_settings").gettext(f"The current prefix is `{current_prefix}`."),
                allowed_mentions=discord.AllowedMentions.none(),
            )

        # See if the user has permission
        try:
            await commands.has_guild_permissions(manage_guild=True).predicate(ctx)
        except Exception:
            return await ctx.send(_(ctx, "bot_settings").gettext("You do not have permission to change the command prefix."))

        # Validate prefix
        if len(new_prefix) > 30:
            return await ctx.send(_(ctx, "bot_settings").gettext("The maximum length a prefix can be is 30 characters."))

        # Store setting
        self.bot.guild_settings[ctx.guild.id][prefix_column] = new_prefix
        async with self.bot.database() as db:
            await db(
                """INSERT INTO guild_settings (guild_id, {prefix_column}) VALUES ($1, $2)
                ON CONFLICT (guild_id) DO UPDATE SET {prefix_column}=excluded.prefix""".format(prefix_column=prefix_column),
                ctx.guild.id, new_prefix
            )
        await ctx.send(
            _(ctx, "bot_settings").gettext(f"My prefix has been updated to `{new_prefix}`."),
            allowed_mentions=discord.AllowedMentions.none(),
        )


def setup(bot: vbu.Bot):
    x = BotSettings(bot)
    bot.add_cog(x)
