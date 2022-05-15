import discord


class WebContext(object):

    def __init__(self, bot, user_id):
        self.bot = bot
        self.author = discord.Object(int(user_id))
        self.original_author_id = int(user_id)
