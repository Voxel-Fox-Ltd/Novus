import re

from discord.ext import commands


class UserID(int):
    """
    A conveter that takes the given value and tries to grab the ID from it.
    When used, this would provide the ID of the user. This isn't guarenteed to be
    a real user, but rather an ID that looks like a user's.
    """

    @classmethod
    async def convert(cls, ctx: commands.Context, value: str) -> int:
        """
        Converts the given value to a valid user ID.
        """

        match = commands.IDConverter()._get_id_match(value) or re.match(r'<@!?([0-9]+)>$', value)
        if match is not None:
            return int(match.group(1))
        raise commands.UserNotFound(value)
