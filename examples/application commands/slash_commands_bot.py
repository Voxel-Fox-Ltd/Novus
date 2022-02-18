import discord
from discord.ext import commands


# Make the client we're going to use
bot = commands.Bot(command_prefix=None)  # Setting the prefix to ``None`` means that it'll only run slash commands


# Make a simple command
@bot.command(
    application_command_meta=commands.ApplicationCommandMeta()  # This is where you would put information about the command
)
async def ping(ctx):
    await ctx.interaction.response.send_message("Pong!")


# Make a slightly more complex command
@bot.command(
    application_command_meta=commands.ApplicationCommandMeta(
        options=[
            discord.ApplicationCommandOption(
                name="one",
                type=discord.ApplicationCommandOptionType.integer,
                description="The first number that you want to add."
            ),
            discord.ApplicationCommandOption(
                name="two",
                type=discord.ApplicationCommandOptionType.integer,
                description="The second number that you want to add."
            ),
        ]
    )
)
async def ping(ctx, one: int, two: int):
    await ctx.interaction.response.send_message(one + two)


# Classic "on ready" event
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')


async def main():
    await bot.login('TOKEN')  # Validate our token
    await bot.register_application_commands()  # Upsert our commands
    await bot.connect()  # Run a websocket connection


loop = bot.loop
loop.run_until_complete(main())
