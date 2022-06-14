import discord
from discord.ext import commands

client = commands.Bot(command_prefix='?')   #define our bot

@client.command()
async def menu_demo(ctx):   #define a dummy command

    embed = discord.Embed(title="Example", color=0x68B38C)  #create a embed as structure
    embed.add_field(    #add some text
        name="Menu",
        value="A example menu",
        inline=False,
    )
    options = []    #define a list for our options
    options.append(
        discord.ui.SelectOption(label="entry 1", value="entry 1"),  #add our option 1
    )
    options.append(
        discord.ui.SelectOption(label="entry 2", value="entry 2"),  #add our option 2
    )

    components = discord.ui.MessageComponents(  #add the menu itself to the embed
        discord.ui.ActionRow(   #create a actionrow
            discord.ui.SelectMenu(  #define the selectmenu
                custom_id="select", #define a id to use later
                options=options,    #add our options list as menu options
            ),
        ),
    )
    await ctx.interaction.user.send(embed=embed, components=components)  #send the embed to the user

    def check(interaction: discord.Interaction):    #add a dummy check to see if its the correct interaction (use a custom check, this is for demo only and just returns true!)
        return True

    interaction = await self.client.wait_for("component_interaction", check=check)  #wait for a interaction from the user
    components.disable_components() #disable the components, so the user can't interact with them anymore
    await interaction.response.edit_message(components=components)  #edit the message with the components

    print(interaction.values[0])    #output the selection
    embed = discord.Embed(title="Response", color=0xC92626)
    embed.add_field(
    name="You seleted:",
    value=interaction.values[0],
    inline=False,
    )
    await ctx.interaction.user.send(embed=embed)    #send the selection to the user
    

client.run("token") #put in your token!
