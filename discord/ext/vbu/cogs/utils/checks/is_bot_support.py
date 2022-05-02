from discord.ext import commands
import discord


class NotBotSupport(commands.MissingRole):
    """
    The generic error for the bot failing the :func:`voxelbotutils.checks.is_bot_support` check -
    is a subclass of :class:`discord.ext.commands.MissingRole`.
    """

    def __init__(self):
        super().__init__("Bot Support Team")


def is_bot_support():
    """
    Checks whether or not the calling user has the bot support role, as defined in the bot's configuration
    file (:attr:`config.bot_support_role_id`). As it checks a role ID, this will only work it the command in quesiton is called
    in a guild where the calling user *has* the given role.

    Raises:
        NotBotSupport: If the given user isn't a member of the bot's support team.
    """

    async def predicate(ctx: commands.Context):
        if ctx.author.id in ctx.bot.owner_ids:
            return True
        support_guild = await ctx.bot.fetch_support_guild()
        if support_guild is None:
            raise NotBotSupport()
        try:
            member = support_guild.get_member(ctx.author.id) or await support_guild.fetch_member(ctx.author.id)
            if member is None:
                raise AttributeError()
        except (discord.HTTPException, AttributeError):
            raise NotBotSupport()
        if ctx.bot.config.get("bot_support_role_id", None) in [i.id for i in member.roles] or ctx.author.id in ctx.bot.owner_ids:
            return True
        raise NotBotSupport()
    return commands.check(predicate)
