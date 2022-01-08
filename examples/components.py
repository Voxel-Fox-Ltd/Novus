import discord
from discord.ext import commands


bot = commands.Bot(command_prefix=commands.when_mentioned_or('$'))


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')


@bot.command()
async def ask(ctx: commands.SlashContext):
    """Asks the user a question to confirm something."""

    # We create the components that we want to send with the message
    # "custom_id" is a hidden value that we can use to define certain actions
    components = discord.ui.MessageComponents(
        discord.ui.ActionRow(
            (yes_button := discord.ui.Button(label="Yes")),
            (no_button := discord.ui.Button(label="No")),
        ),
    )
    await ctx.send('Do you want to continue?', components=components)

    # Set up a check for our `wait_for`
    def check(interaction: discord.Interaction):
        if interaction.user != ctx.author:
            return False
        if interaction.custom_id not in [yes_button.custom_id, no_button.custom_id]:
            return False
        return True

    # Wait for the user to resopnd
    interaction = await bot.wait_for("component_interaction", check=check)

    # Now the user has responded, disable the buttons on the message
    components.disable_components()
    await interaction.response.edit_message(components=components)

    # Give different responses based on what they clicked
    if interaction.custom_id == "YES":
        await interaction.followup.send("You clicked yes!")
    else:
        await interaction.followup.send("You clicked no :<")


async def main():
    await bot.login('TOKEN')  # Validate our token
    await bot.register_application_commands()  # Upsert our commands so they're added as slashies
    await bot.connect()  # Run a websocket connection


loop = bot.loop
loop.run_until_complete(main())
