import discord

from . import utils as vbu


class CommandEvent(vbu.Cog):

    CONTENT_LIMIT = 50

    @vbu.Cog.listener("on_command")
    async def on_command_log(self, ctx: vbu.Context):
        """
        Pinged when a command is invoked.
        """

        if ctx.command is None:
            return
        logger = getattr(getattr(ctx, 'cog', self), 'logger', self.logger)
        try:
            content = ctx.message.content.replace('\n', '\\n')[:self.CONTENT_LIMIT]
        except AttributeError:
            content = ""
        if len(content) > self.CONTENT_LIMIT:
            content += '...'
        invoke_text = "Command invoked"
        if ctx.supports_ephemeral:
            if getattr(ctx, "given_values", None) is not None:
                invoke_text = "Context invoked"
            else:
                invoke_text = "Interaction invoked"
        logger_prefix = f"{invoke_text} ({ctx.command.qualified_name.strip()})"
        if ctx.guild is None:
            return logger.info(f"{logger_prefix} ~ (G0/C{ctx.channel.id}/U{ctx.author.id}) {'::' if content else ''} {content}".rstrip())
        logger.info(f"{logger_prefix} ~ (G{ctx.guild.id}/C{ctx.channel.id}/U{ctx.author.id}) {'::' if content else ''} {content}".rstrip())

    @vbu.Cog.listener("on_command")
    async def on_command_statsd(self, ctx: vbu.Context):
        """
        Ping statsd.
        """

        if not ctx.command:
            return
        command_stats_name = ctx.command.qualified_name.replace(' ', '_')
        is_slash_command = hasattr(ctx, "interaction")
        command_stats_tags = {
            "command_name": command_stats_name,
            "slash_command": is_slash_command,
            "guild_id": ctx.guild.id if ctx.guild else None,
            "shard_id": getattr(ctx.guild, "shard_id", 0) if ctx.guild else 0,
            "cluster": self.bot.cluster,
        }
        if is_slash_command:
            interaction: discord.Interaction = ctx.interaction  # type: ignore
            command_stats_tags.update({
                "user_locale": interaction.user_locale,
                "guild_locale": interaction.guild_locale,
            })
        async with vbu.Stats() as stats:
            stats.increment("discord.bot.commands", tags=command_stats_tags)


def setup(bot: vbu.Bot):
    x = CommandEvent(bot)
    bot.add_cog(x)
