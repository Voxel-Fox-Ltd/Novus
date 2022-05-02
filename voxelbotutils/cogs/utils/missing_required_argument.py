from discord.ext import commands


class MissingRequiredArgumentString(commands.MissingRequiredArgument):
    """
    This is a version of :class:`discord.ext.commands.MissingRequiredArgument`
    that just takes a string as a parameter so you can manually raise
    it inside commands.

    Attributes:
        param (str): The parameter that was missing from the command.
    """

    def __init__(self, param: str):
        self.param: str = param
