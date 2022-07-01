import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='?')  # define our bot


@bot.event #onready event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')


@bot.command()
async def menu_demo(ctx):  # define a dummy command

    embed = discord.Embed(title="Example", color=0x68B38C)  # create a embed as structure
    embed.add_field(  # add some text
        name="Menu",
        value="A example menu",
        inline=False,
    )
    options = [discord.ui.SelectOption(label="entry 1", value="entry 1"),
               discord.ui.SelectOption(label="entry 2", value="entry 2")]  # define a list with our options

    components = discord.ui.MessageComponents(  # add the menu itself to the embed
        discord.ui.ActionRow(  # create a actionrow
            discord.ui.SelectMenu(  # define the selectmenu
                custom_id="select",  # define a id to use later
                options=options,  # add our options list as menu options
            ),
        ),
    )
    await ctx.send(embed=embed, components=components)  # send the embed to the user

    def check(interaction: discord.Interaction):  # add a check to see if its the correct interaction
        if interaction.custom_id == "select":
            return True

    interaction = await bot.wait_for("component_interaction", check=check)  # wait for a interaction from the user
    components.disable_components()  # disable the components, so the user can't interact with them anymore
    await interaction.response.edit_message(components=components)  # edit the message with the components

    embed = discord.Embed(title="Response", color=0xC92626)
    embed.add_field(
        name="You seleted:",
        value=interaction.values[0],
        inline=False,
    )
    await ctx.send(embed=embed)  # send the selection to the user


bot.run("TOKEN")  # put in your token!
