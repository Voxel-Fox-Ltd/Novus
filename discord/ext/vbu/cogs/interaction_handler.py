import io
import textwrap
from typing import Union

import discord
from discord.ext import commands

from . import utils as vbu


class InteractionHandler(vbu.Cog, command_attrs={'hidden': True, 'add_slash_command': False}):

    @vbu.Cog.listener()
    async def on_component_interaction(self, interaction: discord.Interaction):
        if not interaction.custom_id.startswith("RUNCOMMAND"):
            return
        command_name = interaction.custom_id[len("RUNCOMMAND "):]
        command = self.bot.get_command(command_name)
        ctx = await self.bot.get_slash_context(interaction=interaction)
        ctx.invoked_with = command_name
        ctx.command = command
        await self.bot.invoke(ctx)

    @classmethod
    def build_command_output_string(
            cls,
            command: Union[discord.ApplicationCommand, discord.ApplicationCommandOption, discord.ApplicationCommandOptionChoice]) -> str:

        # Get options and choices from the command
        options = None
        choices = None
        if isinstance(command, discord.ApplicationCommandOption):
            choices = command.choices
            command.choices = []
        if isinstance(command, (discord.ApplicationCommandOption, discord.ApplicationCommand)):
            options = command.options
            command.options = []

        # Make our initial string
        text = repr(command)

        # Replace options
        if options:
            all_options_strings = []
            for i in options:
                option_string = cls.build_command_output_string(i)
                all_options_strings.append(option_string)
            all_options_string = textwrap.indent("\n".join(all_options_strings), "    ")
            text = text.replace("options=[]", f"options=[\n{all_options_string}\n]")

        # Replace choices
        if choices:
            all_options_strings = []
            for i in choices:
                all_options_strings.append(repr(i))
            all_options_string = textwrap.indent("\n".join(all_options_strings), "    ")
            text = text.replace("choices=[]", f"choices=[\n{all_options_string}\n]")

        # Indent and return
        return text

    @commands.command(aliases=['addslashcommands', 'addslashcommand', 'addapplicationcommand'])
    @commands.is_owner()
    @commands.bot_has_permissions(send_messages=True, add_reactions=True, attach_files=True)
    async def addapplicationcommands(self, ctx, guild_id: int = None, *commands: str):
        """
        Adds all of the bot's interaction commands to the global interaction handler.
        """

        # Make a guild instance
        guild = guild_id if guild_id is None else discord.Object(guild_id)

        # Add commands
        added_commands = await self.bot.register_application_commands(guild=guild)

        # Build up output string
        output_strings = []
        for comm in added_commands:
            output_strings.append(self.build_command_output_string(comm))
        output_string = "\n".join(output_strings)

        # And output
        output = f"Added **{len(added_commands)}** slash commands:\n{output_string}\n"
        file = discord.File(
            io.StringIO(output_string),
            filename="CommandsAdded.txt",
        )
        output = f"Added **{len(added_commands)}** slash commands."
        await ctx.send(output, file=file)

    @commands.command(aliases=['removeslashcommands', 'removeslashcommand', 'removeapplicationcommand'])
    @commands.is_owner()
    @commands.bot_has_permissions(send_messages=True, add_reactions=True, attach_files=True)
    async def removeapplicationcommands(self, ctx, guild_id: int = None, *commands: str):
        """
        Removes the bot's interaction commands from the global interaction handler.
        """

        guild = guild_id if guild_id is None else discord.Object(guild_id)
        await self.bot.register_application_commands(commands=None, guild=guild)
        await ctx.send("Removed slash commands.")


def setup(bot: vbu.Bot):
    x = InteractionHandler(bot)
    bot.add_cog(x)
