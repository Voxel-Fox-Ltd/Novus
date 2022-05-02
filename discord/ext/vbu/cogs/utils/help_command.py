import random
import typing
import collections

import discord
from discord.ext import commands

from .errors import InvokedMetaCommand, NotBotSupport


class HelpCommand(commands.MinimalHelpCommand):

    HELP_COMMAND_HIDDEN_ERRORS = (
        commands.DisabledCommand, commands.NotOwner,
        NotBotSupport, InvokedMetaCommand,
    )
    HELP_COMMAND_NAMES = ["help", "commands", "channelhelp"]

    @classmethod
    async def filter_commands_classmethod(cls, ctx, commands_to_filter: typing.List[commands.Command]) -> typing.List[commands.Command]:
        """
        Filter the command list down into a list of runnable commands.
        """

        if ctx.author.id in ctx.bot.owner_ids:
            return [i for i in commands_to_filter if i.name not in cls.HELP_COMMAND_NAMES]
        valid_commands = [i for i in commands_to_filter if i.hidden is False and i.enabled is True and i.name not in cls.HELP_COMMAND_NAMES]
        returned_commands = []
        for comm in valid_commands:
            try:
                await comm.can_run(ctx)
            except commands.CommandError as e:
                if isinstance(e, cls.HELP_COMMAND_HIDDEN_ERRORS):
                    continue
            returned_commands.append(comm)
        return returned_commands

    async def filter_commands(self, commands_to_filter: typing.List[commands.Command]) -> typing.List[commands.Command]:
        """
        Filter the command list down into a list of runnable commands.
        """

        return await self.filter_commands_classmethod(self.context, commands_to_filter)

    def get_command_signature(self, command: commands.Command):
        return '{0.context.clean_prefix}{1.qualified_name} {1.signature}'.format(self, command)

    async def send_cog_help(self, cog: commands.Cog):
        """
        Sends help command for a cog.
        """

        return await self.send_bot_help({
            cog: cog.get_commands()
        })

    async def send_group_help(self, group: commands.Group):
        """
        Sends the help command for a given group.
        """

        return await self.send_bot_help({
            group: group.commands
        })

    async def send_command_help(self, command: commands.Command):
        """
        Sends the help command for a given command.
        """

        return await self.send_bot_help({
            command: []
        })

    async def send_bot_help(self, mapping: typing.Dict[typing.Optional[commands.Cog], typing.List[commands.Command]]):
        """
        Sends all help to the given channel.
        """

        # Get the visible commands for each of the cogs
        runnable_commands = {}
        for cog, cog_commands in mapping.items():
            available_commands = await self.filter_commands(cog_commands)
            if len(available_commands) > 0 or isinstance(cog, (commands.Command, commands.Group,)):
                runnable_commands[cog] = available_commands

        # Make an embed
        help_embed = self.get_initial_embed()

        # Add each command to the embed
        command_string_dict = collections.defaultdict(str)
        for cog, cog_commands in runnable_commands.items():
            value = '\n'.join([self.get_help_line(command) for command in cog_commands]) + '\n'
            try:
                cog_name = cog.qualified_name
            except AttributeError:
                cog_name = "Uncategorized"
            command_string_dict[cog_name] += value

            # See if it's a command with subcommands
            if isinstance(cog, commands.Group):
                help_embed.description = self.get_help_line(cog, with_signature=cog.invoke_without_command)
            if isinstance(cog, commands.Command):
                help_embed.description = self.get_help_line(cog, with_signature=True)

        # Order embed by length before embedding
        command_strings = sorted(list(command_string_dict.items()), key=lambda x: x[1].count('\n'), reverse=True)
        for name, value in command_strings:
            if value.strip():
                help_embed.add_field(
                    name=name,
                    value=value.strip(),
                )

        # Send it to the destination
        data = {"embed": help_embed}
        content = self.context.bot.config.get("help_command", {}).get("content", None)
        if content:
            data.update({"content": content.format(bot=self.context.bot, prefix=self.context.clean_prefix)})
        await self.send_to_destination(**data)

    async def send_to_destination(self, *args, **kwargs):
        """
        Sends content to the given destination.
        """

        dest = self.get_destination()

        # If the destination is a user
        if isinstance(dest, (discord.User, discord.Member, discord.DMChannel)):
            try:
                await dest.send(*args, **kwargs)
                if self.context.guild:
                    try:
                        await self.context.send("Sent you a DM!")
                    except discord.Forbidden:
                        pass  # Fail silently
            except discord.Forbidden:
                try:
                    await self.context.send("I couldn't send you a DM :c")
                except discord.Forbidden:
                    pass  # Oh no now they won't know anything
            except discord.HTTPException as e:
                await self.context.send(f"I couldn't send you the help DM - {e}")  # We couldn't send the embed for some other reason
            return

        # If the destination is a channel
        try:
            await dest.send(*args, **kwargs)
        except discord.Forbidden:
            pass  # Can't talk in the channel? Shame
        except discord.HTTPException as e:
            await self.context.send(f"I couldn't send you the help DM - {e}")  # We couldn't send the embed for some other reason

    async def send_error_message(self, error):
        """
        Sends an error message to the user.
        """

        try:
            await self.context.send(error)
        except discord.Forbidden:
            pass

    def get_initial_embed(self) -> discord.Embed:
        """
        Get the initial embed for that gets sent.
        """

        embed = discord.Embed()
        embed.set_author(name=self.context.bot.user, icon_url=self.context.bot.user.display_avatar.url)
        embed.colour = random.randint(1, 0xffffff)
        return embed

    def get_help_line(self, command: commands.Command, with_signature: bool = False):
        """
        Gets a doc line of help for a given command.
        """

        if command.short_doc:
            v = f"**{self.context.clean_prefix}{command.qualified_name}** - {command.short_doc}"
        else:
            v = f"**{self.context.clean_prefix}{command.qualified_name}**"
        if with_signature:
            v += f"\n`{self.context.clean_prefix}{command.qualified_name} {command.signature}`"
        return v

    def get_destination(self):
        """
        Return where we want the bot to send the embed to
        """

        if self.context.invoked_with.lower() == "channelhelp" and self.context.channel.permissions_for(self.context.author).manage_messages:
            return self.context.channel
        if self.context.bot.config.get("help_command", {}).get("dm_help", True):
            return self.context.author
        return self.context.channel
