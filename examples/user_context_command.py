import discord


# Make the client we're going to use
client = discord.Client()


# Make the application commands that should be added
commands = [
    discord.ApplicationCommand(
        name="Get user avatar",
        type=discord.ApplicationCommandType.user,
    ),
]


# Classic "on ready" event
@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')


# Pinged whenever the bot receives a slash command
@client.event
async def on_slash_command(interaction: discord.Interaction):
    """Send a response if the command is ping."""

    command_name = interaction.command_name
    if command_name == "Get user avatar":
        user = interaction.resolved.users[0]
        await interaction.response.send_message(str(user.display_avatar.with_size(1024)))


async def main():
    await client.login('TOKEN')  # Validate our token
    await client.register_application_commands(commands)  # Upsert our commands
    await client.connect()  # Run a websocket connection


loop = client.loop
loop.run_until_complete(main())
