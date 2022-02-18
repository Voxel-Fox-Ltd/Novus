import discord
from discord.ext import commands


# Make the bot we're going to use
bot = commands.Bot(command_prefix=None)  # Setting the prefix to ``None`` means that it'll only run slash commands


# Make the context command
@commands.context_command(name="Get user avatar")
async def context_get_user_avatar(ctx, user: discord.Member):  # By setting the arg as a member it registers as a member context
    await ctx.interaction.response.send_message(str(user.display_avatar.with_size(1024)))


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
