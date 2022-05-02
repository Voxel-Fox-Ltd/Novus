from discord.ext import commands

from .custom_cog import Cog


class Command(commands.Command):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, cooldown_after_parsing=kwargs.pop('cooldown_after_parsing', True), **kwargs)


class Group(commands.Group):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, cooldown_after_parsing=kwargs.pop('cooldown_after_parsing', True), **kwargs)

    def group(self, *args, **kwargs):
        kwargs.setdefault('cls', Group)
        kwargs.setdefault('case_insensitive', self.case_insensitive)
        return super().group(*args, **kwargs)

    def command(self, *args, **kwargs):
        kwargs.setdefault('cls', Command)
        return super().command(*args, **kwargs)
