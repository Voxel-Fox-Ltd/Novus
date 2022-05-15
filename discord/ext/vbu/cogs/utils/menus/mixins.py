from discord.ext import commands


class MenuDisplayable(object):

    async def get_display(self, ctx: commands.Context) -> str:
        """
        Get the display string for the given displayable.
        """

        if self.display is None:
            return None
        if isinstance(self.display, str):
            return self.display.format(ctx)
        return self.display(ctx)
