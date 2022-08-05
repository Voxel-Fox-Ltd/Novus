from typing import Callable, Union, Optional

from discord.ext import commands


class MenuDisplayable(object):

    display: Union[str, Callable[[Union[commands.Context, commands.SlashContext]], str]]

    async def get_display(self, ctx: commands.Context) -> Optional[str]:
        """
        Get the display string for the given displayable.
        """

        if self.display is None:
            return None
        if isinstance(self.display, str):
            return self.display.format(ctx)
        return self.display(ctx)
