import asyncio

import discord
from discord.ext import commands


class BooleanConverter(commands.Converter):
    """
    Converts the given input into a boolean yes/no, defaulting to "no" if something couldn't be
    properly converted rather than raising an error.
    """

    TICK_EMOJIS = [
        "\N{HEAVY CHECK MARK}",
        "\N{HEAVY MULTIPLICATION X}",
    ]

    @classmethod
    async def add_tick_emojis(cls, message: discord.Message):
        """
        Add boolean reactions to the given message.
        """

        for e in cls.TICK_EMOJIS:
            await message.add_reaction(e)

    @classmethod
    def add_tick_emojis_non_async(cls, message: discord.Message):
        """
        Add boolean reactions to the given message as a non-awaitable.
        """

        return asyncio.Task(cls.add_tick_emojis(message))

    @classmethod
    async def convert(cls, ctx, argument):
        return any([
            argument.lower() in ['y', 'yes', 'true', 'definitely', 'ye', 'ya', 'yas', 'ok', 'okay', '1', 't'],
            argument in ['\N{HEAVY CHECK MARK}', '<:tick_yes:596096897995899097>'],
        ])
