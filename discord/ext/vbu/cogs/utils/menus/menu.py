from __future__ import annotations

import asyncio
import typing
import inspect

import discord
from discord.ext import commands

from .errors import ConverterTimeout
from .option import Option
from .mixins import MenuDisplayable
from .callbacks import MenuCallbacks
from .converter import Converter
from ..custom_cog import Cog
from ..custom_command import Command
from ..custom_bot import Bot

if typing.TYPE_CHECKING:
    from ..custom_context import Context, SlashContext

    ContextCallable = typing.Callable[[Context], None]
    AwaitableContextCallable = typing.Awaitable[ContextCallable]
    MaybeCoroContextCallable = typing.Union[ContextCallable, AwaitableContextCallable]


T = typing.TypeVar("T")


@typing.overload
def _do_nothing(return_value: typing.Type[T]) -> typing.Callable[[], T]:
    ...


@typing.overload
def _do_nothing(return_value=None) -> typing.Callable[[], None]:
    ...


def _do_nothing(return_value: typing.Optional[typing.Type[T]] = None) -> typing.Callable[[], typing.Optional[T]]:
    def wrapper(*args, **kwargs) -> typing.Optional[T]:
        if return_value:
            return return_value()
        return return_value
    return wrapper


class Menu(MenuDisplayable):
    """
    A menu using components that's meant to ease up the process of doing settings within your bot.
    """

    callbacks = MenuCallbacks

    def __init__(
            self,
            *options: Option,
            display: str = None,
            component_display: str = None,
            ):
        """
        Args:
            options (typing.List[Option]): A list of options that should be displayed in the menu.
            display (str, optional): When using a nested submenu, this is the option that should be displayed.
            component_display (str, optional): When using a nested submenu, this is the option that
                should be displayed in the component.
        """

        self.display = display  # Used for nested menus
        self.component_display = component_display  # Used for nested menus
        self._options = list(options)

    @typing.overload
    def create_cog(
            self,
            bot=None,
            *,
            cog_name: str = "Bot Settings",
            name: str = "settings",
            aliases: typing.List[str] = ["setup"],
            permissions: typing.List[str] = None,
            post_invoke: MaybeCoroContextCallable = None,
            guild_only: bool = True,
            **command_kwargs
            ) -> typing.Type[commands.Cog]:
        ...

    @typing.overload
    def create_cog(
            self,
            bot: Bot,
            *,
            cog_name: str = "Bot Settings",
            name: str = "settings",
            aliases: typing.List[str] = ["setup"],
            permissions: typing.List[str] = None,
            post_invoke: MaybeCoroContextCallable = None,
            guild_only: bool = True,
            **command_kwargs
            ) -> commands.Cog:
        ...

    def create_cog(
            self,
            bot: typing.Optional[Bot] = None,
            *,
            cog_name: str = "Bot Settings",
            name: str = "settings",
            aliases: typing.List[str] = ["setup"],
            permissions: typing.List[str] = None,
            post_invoke: MaybeCoroContextCallable = None,
            guild_only: bool = True,
            **command_kwargs
            ) -> typing.Union[commands.Cog, typing.Type[commands.Cog]]:
        """
        Creates a cog that can be loaded into the bot in a setup method.

        Parameters
        ----------
        bot : Optional[Bot]
            The bot object. If given, the cog will be instantiated with that object.
        cog_name : Optional[str]
            The name of the cog to be added.
        name : Optional[str]
            The name of the command to be added.
        aliases : Optional[List[str]]
            A list of aliases to be added to the settings command.
        permissions : Optional[List[str]]
            A list of permission names should be required for the command run.
        post_invoke : Optional[MaybeCoroContextCallable]
            A post-invoke method that can be called.
        guild_only : Optional[bool]
            If the command should be guild-only.
        **command_kwargs
            Arguments to be passed down to the command decorator.

        Returns
        -------
        Union[commands.Cog, Type[commands.Cog]]
            Either a cog type to add to your bot, or if a bot instance was passed
            as a parameter, the added cog instance.
        """

        permissions = permissions if permissions is not None else ["manage_guild"]
        meta = commands.ApplicationCommandMeta(guild_only=guild_only)

        class NestedCog(Cog, name=cog_name):

            def __init__(nested_self, bot):
                super().__init__(bot)
                if guild_only:
                    nested_self.settings.add_check(commands.guild_only().predicate)

            def cog_unload(nested_self):
                nested_self.bot.remove_command(nested_self.settings.name)
                super().cog_unload()

            @commands.command(
                cls=Command,
                name=name,
                aliases=aliases,
                application_command_meta=command_kwargs.pop("application_command_meta", meta),
                **command_kwargs,
            )
            @commands.defer()
            @commands.has_permissions(**{i: True for i in permissions})
            @commands.bot_has_permissions(send_messages=True, embed_links=True)
            async def settings(nested_self, ctx):
                """
                Modify some of the bot's settings.
                """

                # Make sure it's a slashie
                if not isinstance(ctx, commands.SlashContext):
                    return await ctx.send("This command can only be run as a slash command.")

                # Get a guild if we need to
                if ctx.interaction.guild_id:
                    guild = await ctx.bot.fetch_guild(ctx.interaction.guild_id)
                    channels = await guild.fetch_channels()
                    guild._channels = {i.id: i for i in channels}  # Fetching a guild doesn't set channels :/
                    ctx._guild = guild

                # Start the menu
                await self.start(ctx)

                # Post invoke
                if post_invoke is None:
                    return
                if inspect.iscoroutine(post_invoke):
                    await post_invoke(ctx)
                else:
                    post_invoke(ctx)

        if bot:
            return NestedCog(bot)
        return NestedCog

    async def get_options(self, ctx: commands.SlashContext, force_regenerate: bool = False) -> typing.List[Option]:
        """
        Get all of the options for an instance.
        This method has an open database instance in :code:`ctx.database`.
        """

        return self._options

    async def start(self, ctx: commands.SlashContext, delete_message: bool = False) -> None:
        """
        Run the menu instance.

        Parameters
        ----------
        ctx : vbu.SlashContext
            A context object to run the settings menu from.
        delete_message : Optional[bool]
            Whether or not to delete the menu message when the menu is
            completed.
        """

        # Set up our base case
        sendable_data: dict = await self.get_sendable_data(ctx)
        sent_components: discord.ui.MessageComponents = sendable_data['components']
        menu_message: discord.Message

        # Send the initial message
        if not isinstance(ctx, commands.SlashContext):
            menu_message = await ctx.send(**sendable_data)  # No interaction?
        elif ctx.interaction.response.is_done:
            menu_message = await ctx.interaction.followup.send(**sendable_data)  # Deferred interaction
        else:
            await ctx.interaction.response.defer()
            menu_message = await ctx.interaction.followup.send(**sendable_data)

        # Set up a function so as to get
        def get_button_check(given_message):
            def button_check(payload):
                if payload.message.id != given_message.id:
                    return False
                if payload.user.id == ctx.interaction.user.id:
                    return True
                ctx.bot.loop.create_task(payload.respond(
                    f"Only {ctx.interaction.user.mention} can interact with these buttons.",
                    ephemeral=True,
                ))
                return False
            return button_check

        # Keep looping while we're expecting a user input
        while True:

            # Wait for the user to click on a button
            try:
                payload: discord.Interaction = await ctx.bot.wait_for(
                    "component_interaction",
                    check=get_button_check(menu_message),
                    timeout=60.0,
                )
                ctx.interaction = payload
                await payload.response.edit_message(components=sent_components.disable_components())
            except asyncio.TimeoutError:
                break

            # From this point onwards in the loop, we'll always have an interaction
            # within the context object.

            # Determine the option they clicked for
            clicked_option = None
            options = await self.get_options(ctx)
            for i in options:
                if i._component_custom_id == payload.custom_id:
                    clicked_option = i
                    break
            if clicked_option is None:
                break

            # Run the given option
            # This may change the interaction object within the context,
            # but at all points it should be deferred (update)
            try:
                if isinstance(clicked_option._callback, Menu):
                    await clicked_option._callback.start(ctx, delete_message=True)
                else:
                    await clicked_option.run(ctx)
            except ConverterTimeout as e:
                try:
                    await ctx.interaction.followup.send(
                        content=e.message,
                    )
                except:
                    pass
                break
            except asyncio.TimeoutError:
                break

            # Edit the message with our new buttons
            sendable_data = await self.get_sendable_data(ctx)
            sent_components = sendable_data['components']
            menu_message = await ctx.interaction.followup.send(**sendable_data)

        # Disable the buttons before we leave
        try:
            if delete_message:
                await ctx.interaction.delete_original_message()
            else:
                await ctx.interaction.edit_original_message(components=sent_components.disable_components())
        except Exception:
            pass

    async def get_sendable_data(self, ctx: commands.SlashContext) -> dict:
        """
        Gets a dictionary of sendable objects to unpack for the :func:`start` method.
        """

        # Make our output lists
        output_strings = []
        buttons = []

        # Add items to the list
        async with ctx.bot.database() as db:
            ctx.database = db
            options = await self.get_options(ctx, force_regenerate=True)
            for i in options:
                output = await i.get_display(ctx)
                if output:
                    output_strings.append(f"\N{BULLET} {output}")
                style = (discord.ui.ButtonStyle.secondary if isinstance(i._callback, Menu) else None) or i._button_style or discord.ui.ButtonStyle.primary
                buttons.append(discord.ui.Button(
                    label=i.component_display,
                    custom_id=i._component_custom_id,
                    style=style,
                ))
        ctx.database = None

        # Add a done button
        buttons.append(discord.ui.Button(label="Done", custom_id="Done", style=discord.ui.ButtonStyle.success))

        # Output
        components = discord.ui.MessageComponents.add_buttons_with_rows(*buttons)
        embed = discord.Embed(colour=0xffffff)
        embed.description = "\n".join(output_strings) or "No options added."
        return {
            "embed": embed,
            "components": components,
        }


class MenuIterable(Menu, Option):
    """
    A menu instance that takes and shows iterable data.
    """

    allow_none = False

    def __init__(
            self,
            *,
            select_sql: str,
            insert_sql: str,
            delete_sql: str,
            row_text_display: typing.Callable[[Context, dict], str],
            row_component_display: typing.Callable[[Context, dict], str],
            converters: typing.List[Converter],
            select_sql_args: typing.Callable[[Context], typing.Iterable[typing.Any]] = None,
            insert_sql_args: typing.Callable[[Context, typing.List[typing.Any]], typing.Iterable[typing.Any]] = None,
            delete_sql_args: typing.Callable[[Context, dict], typing.Iterable[typing.Any]] = None,
            cache_callback: typing.Optional[typing.Callable[[Context, typing.List[typing.Any]], None]] = None,
            cache_delete_callback: typing.Optional[typing.Callable[[Context, typing.List[typing.Any]], None]] = None,
            cache_delete_args: typing.Optional[typing.Callable[[dict], typing.Iterable[typing.Any]]] = None,
            ):
        """
        Args:
            select_sql (str): The SQL that should be used to select the rows to be displayed from the database.
            select_sql_args (typing.Callable[[commands.Context], typing.List[typing.Any]]): A function returning a
                list of arguments that should be passed to the database select. The list given is args that are passed
                to the select statement.
            insert_sql (str): The SQL that should be used to insert the data into the database.
            insert_sql_args (typing.Callable[[commands.Context, typing.List[typing.Any]], typing.List[typing.Any]]): A
                function returning a list of arguments that should be passed to the database insert. The list given is
                a list of items returned from the option.
            delete_sql (str): The SQL that should be used to delete a row from the database.
            delete_sql_args (typing.Callable[[commands.Context, dict], typing.List[typing.Any]]): A function returning a
                list of arguments that should be passed to the database delete. The dict given is a row from the database.
            row_text_display (typing.Callable[[commands.Context, dict], str]): A function returning a string which should
                be showed in the menu. The dict given is the row from the database.
            row_component_display (typing.Callable[[commands.Context, dict], typing.Union[str, typing.Tuple[str, str]]): A
                function returning a string which should be shown on the component. The dict given is the row from the database.
                If one string is returned, it's used for both the button and its custom ID. If two strings are given, the
                first is used for the button and the second for the custom ID.
            converters (typing.List[Converter]): A list of converters that the user should be asked for.
            cache_callback (typing.Optional[typing.Callable[[commands.Context, typing.List[typing.Any]], None]]): Description
            cache_delete_callback (typing.Optional[typing.Callable[[commands.Context, typing.List[typing.Any]], None]]): Description
            cache_delete_args (typing.Optional[typing.Callable[[dict], typing.List[typing.Any]]]): Description
        """

        self.row_text_display = row_text_display
        self.row_component_display = row_component_display
        self.converters = converters

        self.cache_callback = cache_callback or _do_nothing()
        self.cache_delete_callback = cache_delete_callback or _do_nothing()
        self.cache_delete_args = cache_delete_args or _do_nothing(list)

        self.select_sql = select_sql
        self.select_sql_args = select_sql_args or _do_nothing(list)

        self.insert_sql = insert_sql
        self.insert_sql_args = insert_sql_args or _do_nothing(list)

        self.delete_sql = delete_sql
        self.delete_sql_args = delete_sql_args or _do_nothing(list)

        self._options = None

    def insert_database_call(self):
        """
        Run the insert database call.
        """

        async def wrapper(ctx, data):
            args = self.insert_sql_args(ctx, data)
            async with ctx.bot.database() as db:
                await db(self.insert_sql, *args)
        return wrapper

    def delete_database_call(self, row):
        """
        Run the delete database call.
        """

        async def wrapper(ctx, data):
            args = self.delete_sql_args(ctx, row)
            async with ctx.bot.database() as db:
                await db(self.delete_sql, *args)
        return wrapper

    async def get_options(self, ctx: commands.SlashContext, force_regenerate: bool = False):
        """
        Get all of the options for an instance.
        This method has an open database instance in :code:`Context.database`.
        """

        # Let's not generate new ones if we don't need to
        if not force_regenerate and self._options is not None:
            return self._options

        # Grab our data from the database
        rows = await ctx.database(self.select_sql, *list(self.select_sql_args(ctx)))
        generated = []

        # Make buttons for deleting the data
        for i in rows:
            v = Option(
                display=self.row_text_display(ctx, i),
                component_display=self.row_component_display(ctx, i),
                callback=self.delete_database_call(i),
                cache_callback=self.cache_delete_callback(*list(self.cache_delete_args(i)))
            )
            v._button_style = discord.ui.ButtonStyle.danger
            generated.append(v)

        # Add "add new" button
        if len(generated) <= 20:
            v = Option(
                display=None,
                component_display="Add New",
                converters=self.converters,
                callback=self.insert_database_call(),
                cache_callback=self.cache_callback
            )
            v._button_style = discord.ui.ButtonStyle.secondary
            generated.append(v)

        # And return
        self._options = generated
        return generated
