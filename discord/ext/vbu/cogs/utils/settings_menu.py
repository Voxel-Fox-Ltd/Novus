from __future__ import annotations

import asyncio
import typing

import discord
from discord.ext import commands

from .errors import InvokedMetaCommand


def do_nothing(value):
    return value


class SettingsMenuError(commands.CommandError):
    pass


class SettingsMenuConverter(object):

    __slots__ = ('prompt', 'asking_for', 'converter', 'emojis', 'serialize')

    def __init__(
            self, prompt: str, converter: typing.Union[typing.Callable, commands.Converter], asking_for: str = 'item',
            emojis: typing.Optional[typing.List[discord.Emoji]] = None,
            serialize_function: typing.Callable[[typing.Any], typing.Any] = lambda x: x,
            ):
        self.prompt = prompt
        self.asking_for = asking_for
        self.converter = converter
        self.emojis = emojis or list()
        self.serialize = serialize_function


class SettingsMenuOption(object):
    """
    An option that can be chosen for a settings menu's selectable item,
    eg an option that refers to a sub-menu, or a setting that refers to grabbing
    a role list, etc.
    """

    __slots__ = ('context', '_display', 'converter_args', 'callback', 'emoji', 'allow_nullable',)

    def __init__(
            self,
            ctx: commands.Context,
            display: typing.Union[str, typing.Callable[[commands.Context], str]],
            converter_args: typing.List[SettingsMenuConverter] = None,
            callback: typing.Callable[['SettingsMenuOption', typing.List[typing.Any]], None] = lambda x: None,
            emoji: str = None,
            allow_nullable: bool = True,
            ):
        """
        Args:
            ctx (commands.Context): The context for which the menu is being invoked.
            display (Union[str, Callable[[commands.Context], str]]): A string (or callable that returns string) that gives the
                display prompt for the option.
            converter_args (List[SettingsMenuConverter], optional): A list of converter arguments that should be used to
                convert the user-provided arguments. Tuples are passed directly into `convert_prompted_information`.
            callback (Callable[['SettingsMenuOption', List[Any]], None], optional): A callable that's passed the
                information from the converter for you do to whatever with.
            emoji (str, optional): The emoji that this option refers to.
            allow_nullable (bool, optional): Whether or not this option is allowed to return None.
        """

        self.context: commands.Context = ctx
        self._display: typing.Union[str, typing.Callable[[commands.Context], str]] = display
        self.converter_args: typing.List[SettingsMenuConverter] = converter_args or list()
        self.callback: typing.Callable[['SettingsMenuOption', typing.List[typing.Any]], None] = callback
        self.allow_nullable: bool = allow_nullable

    def get_display(self) -> str:
        """
        Get the display prompt for this option.

        Returns:
            str: The string to be displayed
        """

        if isinstance(self._display, str):
            return self._display
        return self._display(self.context)

    async def perform_action(self) -> None:
        """
        Runs through the converters before calling the instance's callback method with the converted data.
        """

        # Get data
        returned_data = []
        for arg in self.converter_args:
            try:
                data = await self.convert_prompted_information(arg.prompt, arg.asking_for, arg.converter, arg.emojis)
            except SettingsMenuError as e:
                if not self.allow_nullable:
                    raise e
                data = None
            returned_data.append(data)
            if data is None:
                break

        # Do callback
        if isinstance(self.callback, commands.Command):
            await self.callback.invoke(self.context)
        elif isinstance(self.callback, SettingsMenu):
            await self.callback.start(self.context)
        else:
            called_data = self.callback(self, *returned_data)
            if asyncio.iscoroutine(called_data):
                await called_data

    async def convert_prompted_information(
            self,
            prompt: str,
            asking_for: str,
            converter: commands.Converter,
            reactions: typing.List[discord.Emoji] = None,
            ) -> typing.Any:
        """
        Ask the user for some information, convert said information, and then return that converted value.

        Args:
            prompt (str): The text that we sent to the user -- something along the lines of "what
                channel do you want to use" etc.
            asking_for (str): Say what we're looking for them to send - doesn't need to be anything important,
                it just goes to the timeout message.
            converter (commands.Converter): The converter used to work out what to change the given user value to.
            reactions (typing.List[discord.Emoji], optional): The reactions that should be added to the prompt
                message. If provided then the content of the added reaction is thrown into the converter instead.

        Returns:
            typing.Any: The converted information.

        Raises:
            InvokedMetaCommand: If converting the information timed out, raise this error to signal to
                the menu that we should exit.
            SettingsMenuError: If the converting failed for some other reason.
        """

        # Send prompt
        sendable: typing.Dict[str, typing.Any] = {"content": prompt}
        if reactions:
            x = discord.ui.MessageComponents.add_buttons_with_rows(*[
                discord.ui.Button(emoji=i, custom_id=str(i))
                for i in reactions
            ])
            sendable["components"] = x
        bot_message = await self.context.send(**sendable)

        # Wait for a response from the user
        user_message = None
        try:
            if reactions:
                def check(payload: discord.Interaction):
                    return all([
                        payload.message.id == bot_message.id,
                        payload.user.id == self.context.author.id,
                    ])
                payload = await self.context.bot.wait_for("component_interaction", timeout=120, check=check)
                await payload.response.defer_update()
                content = str(payload.component.custom_id)
            else:
                def check(message: discord.Message):
                    return all([
                        message.channel.id == self.context.channel.id,
                        message.author.id == self.context.author.id,
                    ])
                user_message = await self.context.bot.wait_for("message", timeout=120, check=check)
                content = user_message.content
        except asyncio.TimeoutError:
            await self.context.send(f"Timed out asking for {asking_for}.")
            raise InvokedMetaCommand()

        # Run converter
        conversion_failed = False
        value = None
        if hasattr(converter, 'convert'):
            try:
                converter = converter()
            except TypeError:
                pass
            try:
                value = await converter.convert(self.context, content)
            except commands.CommandError:
                conversion_failed = True
        else:
            try:
                value = converter(content)
            except Exception:
                conversion_failed = True

        # Delete prompt messages
        try:
            await bot_message.delete()
        except discord.NotFound:
            pass
        try:
            await user_message.delete()
        except (discord.Forbidden, discord.NotFound, AttributeError):
            pass

        # Check conversion didn't fail
        if conversion_failed:
            raise SettingsMenuError()

        # Return converted value
        return value

    @classmethod
    def get_guild_settings_mention(
            cls,
            ctx: commands.Context,
            attr: str,
            default: str = 'none',
            ) -> str:
        """
        Get an item from the cached `Bot.guild_settings` object for the running guild and return
        either it's mention string, or the `default` arg.

        Args:
            ctx (commands.Context): The context for the command.
            attr (str): The attribute we want to mention.
            default (str, optional): If not found, what should the default be.

        Returns:
            str: The mention string.
        """

        settings = ctx.bot.guild_settings[ctx.guild.id]
        return cls.get_settings_mention(ctx, settings, attr, default)

    @classmethod
    def get_user_settings_mention(
            cls,
            ctx: commands.Context,
            attr: str,
            default: str = 'none',
            ) -> str:
        """
        Get an item from the cached `Bot.user_settings` object for the running user and return
        either it's mention string, or the `default` arg.

        Args:
            ctx (commands.Context): The context for the command.
            attr (str): The attribute we want to mention.
            default (str, optional): If not found, what should the default be.

        Returns:
            str: The mention string.
        """

        settings = ctx.bot.user_settings[ctx.author.id]
        return cls.get_settings_mention(ctx, settings, attr, default)

    @classmethod
    def get_settings_mention(
            cls,
            ctx: commands.Context,
            settings: dict,
            attr: str,
            default: str = 'none',
            ) -> str:
        """
        Get an item from the bot's settings.

        :meta private:

        Args:
            ctx (commands.Context): The context for the command.
            settings (dict): The dictionary with the settings in it that we want to grab.
            attr (str): The attribute we want to mention.
            default (str, optional): If not found, what should the default be.

        Returns:
            str: The mention string.
        """

        # Run converters
        if 'channel' in attr.lower().split('_'):
            data = ctx.bot.get_channel(settings[attr])
        elif 'role' in attr.lower().split('_'):
            data = ctx.guild.get_role(settings[attr])
        else:
            data = settings[attr]
            if isinstance(data, bool):
                return str(data).lower()
            return data

        # Get mention
        return cls.get_mention(data, default)

    @staticmethod
    def get_mention(
            data: typing.Union[discord.abc.GuildChannel, discord.Role, None],
            default: str,
            ) -> str:
        """
        Get the mention of an object.

        :meta private:

        Args:
            data (typing.Union[discord.abc.GuildChannel, discord.Role, None]): The object we want to mention.
            default (str): The default string that should be output if we can't mention the object.

        Returns:
            str: The mention string.
        """

        mention = data.mention if data else default
        return mention

    @classmethod
    def get_set_guild_settings_callback(
            cls,
            table_name: str,
            column_name: str,
            serialize_function: typing.Callable[[typing.Any], typing.Any] = None,
            ) -> typing.Callable[[typing.Any], None]:
        """
        Return an async method that takes the data given by `convert_prompted_information`, then
        saves it into the database - should be used in the SettingsMenu init.

        :meta private:

        Args:
            table_name (str): The name of the table the data should be inserted into. This is
                not used when caching information. This should NOT be a user supplied value.
            column_name (str): The name of the column that the data should be inserted into.
                This is the same name that's used for caching. This should NOT be a user supplied value.
            serialize_function (typing.Callable[[typing.Any], typing.Any], optional): The function that is called to convert the
                input data in the callback into a database-friendly value. This is *not* called for caching the value, only
                for databasing. The default serialize function doesn't do anything, but is provided so you don't have to provide
                one yourself.

        Returns:
            typing.Callable[[typing.Any], None]: A callable function that sets the guild settings when provided with data
        """

        if serialize_function is None:
            serialize_function = do_nothing
        return cls.get_set_settings_callback(table_name, "guild_id", column_name, serialize_function)

    @classmethod
    def get_set_user_settings_callback(
            cls,
            table_name: str,
            column_name: str,
            serialize_function: typing.Callable[[typing.Any], typing.Any] = None,
            ) -> typing.Callable[[dict], None]:
        """
        Return an async method that takes the data given by `convert_prompted_information`, then
        saves it into the database - should be used in the SettingsMenu init.

        :meta private:

        Args:
            table_name (str): The name of the table the data should be inserted into. This is not used when caching information.
                This should NOT be a user supplied value.
            column_name (str): The name of the column that the data should be inserted into. This is the same name that's used for
                caching the value. This should NOT be a user supplied value.
            serialize_function (typing.Callable[[typing.Any], typing.Any], optional): The function that is called to convert the input data
                in the callback into a database-friendly value. This is *not* called for caching the value, only for databasing. The default
                serialize function doesn't do anything, but is provided so you don't have to provide one yourself.

        Returns:
            typing.Callable[[dict], None]: A callable function that sets the user settings when provided with data
        """

        if serialize_function is None:
            serialize_function = do_nothing
        return cls.get_set_settings_callback(table_name, "user_id", column_name, serialize_function)

    @staticmethod
    def get_set_settings_callback(
            table_name: str,
            primary_key: str,
            column_name: str,
            serialize_function: typing.Callable[[typing.Any], typing.Any] = None
            ) -> typing.Callable[[dict], None]:
        """
        Return an async method that takes the data given by `convert_prompted_information`, then
        saves it into the database - should be used in the SettingsMenu init.

        Args:
            table_name (str): The name of the table the data should be inserted into. This is not used when caching information.
                This should NOT be a user supplied value.
            primary_key (str): The primary key of the table that you want to insert to. This *only* supports single primary keys and not
                compound ones.
            column_name (str): The name of the column that the data should be inserted into. This is the same name that's used for
                caching the value. This should NOT be a user supplied value.
            serialize_function (typing.Callable[[typing.Any], typing.Any], optional): The function that is called to convert the input data
                in the callback into a database-friendly value. This is *not* called for caching the value, only for databasing. The default
                serialize function doesn't do anything, but is provided so you don't have to provide one yourself.

        Returns:
            typing.Callable[[dict], None]: A callable function that sets the user settings when provided with data
        """

        async def callback(self, data):
            """
            The function that actually sets the data in the specified table in the database.
            Any input to this function should be a direct converted value from `convert_prompted_information`.
            If the input is a discord.Role or discord.TextChannel, it is automatcally converted to that value's ID,
            which is then put into the datbase and cache.
            """

            # See if we need to get the object's ID
            if isinstance(data, (discord.Role, discord.TextChannel, discord.User, discord.Member, discord.Object, discord.CategoryChannel)):
                data = data.id

            # Serialize via the passed serialize function
            original_data, data = data, serialize_function(data)

            # Add to the database
            async with self.context.bot.database() as db:
                await db(
                    "INSERT INTO {0} ({1}, {2}) VALUES ($1, $2) ON CONFLICT ({1}) DO UPDATE SET {2}=$2".format(table_name, primary_key, column_name),
                    self.context.guild.id, data,
                )

            # Cache
            self.context.bot.guild_settings[self.context.guild.id][column_name] = original_data

        # Return the callback
        return callback

    @staticmethod
    def get_set_iterable_delete_callback(
            table_name: str,
            column_name: str,
            cache_key: str,
            database_key: str,
            ) -> typing.Callable[[SettingsMenu, commands.Context, int], None]:
        """
        Return an async method that takes the data retuend by `convert_prompted_information` and then
        saves it into the database - should be used for the SettingsMenu init.

        Args:
            table_name (str): The name of the database that you want to remove data from.
            column_name (str): The column name that the key is inserted into in the table.
            cache_key (str): The key that's used to access the cached value for the iterable in `bot.guilds_settings`.
            database_key (str): The key that's used to refer to the role ID in the `role_list` table.

        Returns:
            Callable[[SettingsMenu, commands.Context, int], None]: A callable for `SettingsMenuIterable` objects to use.
        """

        def wrapper(menu, ctx, delete_key: int):
            """
            A sync wrapper so that we can return an async callback that deletes from the database.
            """

            async def callback(menu):
                """
                The function that actually deletes the role from the database
                Any input to this function will be silently discarded, since the actual input to this function is defined
                in the callback definition.
                """

                # Database it
                async with ctx.bot.database() as db:
                    await db(
                        "DELETE FROM {0} WHERE guild_id=$1 AND {1}=$2 AND key=$3".format(table_name, column_name),
                        ctx.guild.id, delete_key, database_key
                    )

                # Remove the converted value from cache
                try:
                    ctx.bot.guild_settings[ctx.guild.id][cache_key].remove(delete_key)
                except AttributeError:
                    ctx.bot.guild_settings[ctx.guild.id][cache_key].pop(delete_key)

            return callback

        return wrapper

    @staticmethod
    def get_set_iterable_add_callback(
            table_name: str, column_name: str, cache_key: str, database_key: str,
            serialize_function: typing.Callable[[typing.Any], str] = None,
            original_data_type: type = None,
            ) -> typing.Callable[['SettingsMenu', commands.Context], None]:
        """
        Return an async method that takes the data retuend by `convert_prompted_information` and then
        saves it into the database - should be used for the SettingsMenu init. This particular iterable
        can only deal with one convertable datapoint (for a list) or two (for a mapping). Any more than that
        and you will need to provide your own callback.

        Args:
            table_name (str): The name of the database that you want to add data to.
            column_name (str): The column name that the key is inserted into in the table.
            cache_key (str): This is the key that's used when caching the value in `bot.guild_settings`.
            database_key (str): This is the key that the value is added to the database table `role_list`.
            serialize_function (Callable[[Any], str], optional): The function run on the value to convert it
                into to make it database-safe. Values are automatically cast to strings after being run through the serialize function.
                The serialize_function is called when caching the value, but the cached value is not cast to a string. The default
                serialize function doesn't do anything, but is provided so you don't have to provide one yourself.

        Returns:
            Callable[[SettingsMenu, commands.Context], Callable[[SettingsMenu, Any, Optional[Any]], None]]:
                A callable for `SettingsMenuIterable` objects to use.
        """

        if serialize_function is None:
            serialize_function = do_nothing

        def wrapper(menu, ctx):
            """
            A sync wrapper so that we can return an async callback that deletes from the database.
            """

            async def callback(menu, *data):
                """
                The function that actually adds the role to the table in the database
                Any input to this function will be direct outputs from perform_action's convert_prompted_information
                This is a function that creates a callback, so the expectation of `data` in this instance is that data is either
                a list of one item for a listing, eg [role_id], or a list of two items for a mapping, eg [role_id, value]
                """

                # Unpack the data
                try:
                    role, original_value = data
                    value = str(serialize_function(original_value))
                except ValueError:
                    role, value = data[0], None

                # Database it
                async with ctx.bot.database() as db:
                    await db(
                        """INSERT INTO {0} (guild_id, {1}, key, value) VALUES ($1, $2, $3, $4)
                        ON CONFLICT (guild_id, {1}, key) DO UPDATE SET value=excluded.value""".format(table_name, column_name),
                        ctx.guild.id, role.id, database_key, value
                    )

                # Set the original value for the cache
                if original_data_type is not None:
                    ctx.bot.guild_settings[ctx.guild.id].setdefault(cache_key, original_data_type())

                # Cache the converted value
                if value:
                    ctx.bot.guild_settings[ctx.guild.id][cache_key][role.id] = serialize_function(original_value)
                else:
                    if role.id not in ctx.bot.guild_settings[ctx.guild.id][cache_key]:
                        ctx.bot.guild_settings[ctx.guild.id][cache_key].append(role.id)

            return callback

        return wrapper


class SettingsMenu:
    """
    A settings menu object for setting up sub-menus or bot settings using reactions.
    Each menu object must be added as its own command, with sub-menus being
    referred to by string in the MenuItem's action.

    Examples:

        ::

            # We can pull out the settings menu mention method so that we can more easily refer to it in our lambdas.
            settings_mention = vbu.menus.SettingsMenuOption.get_guild_settings_mention

            # Make an initial menu.
            menu = vbu.menus.SettingsMenu()

            # And now we add some options.
            menu.add_multiple_options(

                # Every option that's added needs to be an instance of SettingsMenuOption.
                vbu.menus.SettingsMenuOption(

                    # The first argument is the context, always.
                    ctx=ctx,

                    # Display is either a string, or a function that takes context as an argument to *return*
                    # a string.
                    display=lambda c: "Set quote channel (currently {0})".format(settings_mention(c, 'quote_channel_id')),

                    # Converter args should be a list of SettingsMenuConverter options if present. These are the questions
                    # asked to the user to get the relevant information out of them.
                    converter_args=(
                        vbu.menus.SettingsMenuConverter(

                            # Prompt is what's asked to the user
                            prompt="What do you want to set the quote channel to?",

                            # Converter is either a converter or a function that's run to convert the given argument.
                            converter=commands.TextChannelConverter,
                        ),
                    ),

                    # Callback is a function that's run with the converted information to store the data in a database
                    # or otherwise.
                    callback=vbu.menus.SettingsMenuOption.get_set_guild_settings_callback('guild_settings', 'quote_channel_id'),
                ),

                # This is an option that calls a subcommand, also running some SettingsMenu code.
                vbu.menus.SettingsMenuOption(
                    ctx=ctx,
                    display="Set up VC max members",
                    callback=self.bot.get_command("setup vcmaxmembers"),
                ),
            )

            # And now we can run the menu
            try:
                await menu.start(ctx)
                await ctx.send("Done setting up!")
            except voxelbotutils.errors.InvokedMetaCommand:
                pass
    """

    TICK_EMOJI = "\N{HEAVY CHECK MARK}"
    PLUS_EMOJI = "\N{HEAVY PLUS SIGN}"

    def __init__(self):
        self.options: typing.List[SettingsMenuOption] = list()
        self.emoji_options: typing.Dict[str, SettingsMenuOption] = {}

    def add_option(self, option: SettingsMenuOption):
        """
        Add an option to the settings list.

        Args:
            option (SettingsMenuOption): The option that you want to add to the menu.
        """

        self.options.append(option)

    def add_multiple_options(self, *option: SettingsMenuOption):
        """
        Add multiple options to the settings list at once.

        Args:
            *option (SettingsMenuOption): A list of options that you want to add to the menu.
        """

        self.options.extend(option)

    async def start(self, ctx: commands.Context, *, timeout: float = 120):
        """
        Starts the menu running.

        Args:
            ctx (commands.Context): The context object for the called command.
            timeout (float, optional): How long the bot should wait for a reaction.
        """

        message = None
        while True:

            # Send message
            self.emoji_options.clear()
            data, emoji_list = self.get_sendable_data(ctx)
            if message is None:
                message = await ctx.send(**data)
            else:
                await message.edit(**data)

            # Get the reaction
            try:
                def check(payload):
                    return all([
                        payload.message.id == message.id,
                        payload.user.id == ctx.author.id,
                    ])
                payload = await ctx.bot.wait_for("component_interaction", check=check, timeout=timeout)
                await payload.response.defer_update()
            except asyncio.TimeoutError:
                break
            picked_emoji = str(payload.component.custom_id)

            # Get the picked option
            try:
                picked_option = self.emoji_options[picked_emoji]
            except KeyError:
                continue

            # Process the picked option
            if picked_option is None:
                break
            try:
                await picked_option.perform_action()
            except SettingsMenuError:
                pass

        # Delete all the processing stuff
        try:
            await message.delete()
        except (discord.NotFound, discord.Forbidden, discord.HTTPException):
            pass

    def get_sendable_data(
            self,
            ctx: commands.Context
            ) -> typing.Tuple[dict, typing.List[str]]:
        """
        Get a valid set of sendable data for the destination.

        Args:
            ctx (commands.Context): Just so we can set the invoke meta flag.

        Returns:
            Tuple[dict, List[str]]: A tuple of the sendable data for the destination that
                can be unpacked into a `discord.abc.Messageable.send`, and a list of emoji
                to add to the message in question.
        """

        ctx.invoke_meta = True

        # Create embed
        embed = discord.Embed()
        lines = []
        emoji_list = []
        index = 0
        for index, i in enumerate(self.options):
            emoji = i.emoji
            if emoji is None:
                emoji = f"{index}"
                index += 1
            display = i.get_display()
            if display:
                lines.append(f"{emoji}) {i.get_display()}")
            self.emoji_options[emoji] = i
            emoji_list.append(emoji)

        # Finish embed
        text_lines = '\n'.join(lines)
        embed.description = text_lines or "No set data"

        # Add tick
        self.emoji_options[self.TICK_EMOJI] = None
        emoji_list.append(self.TICK_EMOJI)

        buttons = [
            discord.ui.Button(emoji=i, custom_id=i)
            for i in emoji_list
        ]
        buttons += [
            discord.ui.Button(label="Done", custom_id="done", style=discord.ui.ButtonStyle.success)
        ]
        components = discord.ui.MessageComponents.add_buttons_with_rows(*buttons)

        # Return data
        return {'embed': embed, "components": components}, emoji_list


class SettingsMenuIterable(SettingsMenu):
    """
    A version of the settings menu for dealing with things like lists and dictionaries.
    """

    def __init__(
            self,
            table_name: str,
            column_name: str,
            cache_key: str,
            database_key: str,
            key_display_function: typing.Callable[[typing.Any], str],
            value_display_function: typing.Callable[[typing.Any], str] = str,
            converters: typing.List[SettingsMenuConverter] = None, *,
            iterable_add_callback: typing.Callable[['SettingsMenu', commands.Context], None] = None,
            iterable_delete_callback: typing.Callable[['SettingsMenu', commands.Context, int], None] = None,
            ):
        """
        Args:
            table_name (str): The name of the table that the data should be inserted into.
            column_name (str): The column name for the table where the key should be inserted to.
            cache_key (str): The key that goes into `bot.guild_settings` to get to the cached iterable.
            database_key (str): The key that would be inserted into the default `role_list` or `channel_list`
                tables. If you're not using this field then this will probably be pretty useless to you.
            key_display_function (typing.Callable[[typing.Any], str]): A function used to take the raw data from the key and
                change it into a display value.
            value_display_function (typing.Callable[[typing.Any], str], optional): The function used to take the saved raw value
                from the database and nicely show it to the user in the embed.
            converters (typing.List[SettingsMenuConverter], optional): A list of the converters that should be used for the user to provide
                their new values for the menu.
            iterable_add_callback (typing.Callable[['SettingsMenu', commands.Context], None], optional): A function that's run with the
                params of the database name, the column name, the cache key, the database key, and the value serialize function.
                If left blank then it defaults to making a new callback for you that just adds to the `role_list` or `channel_list`
                table as specified. These methods are only directly compatible with lists and dictionaries - nothing that requires multiple
                arguments to be saved in a database; for those you will need to write your own method.
            iterable_delete_callback (typing.Callable[['SettingsMenu', commands.Context, int], None], optional): A function that's run
                with the params of the database name, the column name, the item to be deleted, the cache key, and the database key.
                If left blank then it defaults to making a new callback for you that just deletes from the `role_list` or `channel_list`
                table as specified. These methods are only directly compatible with lists and dictionaries - nothing that requires multiple
                arguments to be saved in a database; for those you will need to write your own method.
        """

        try:
            if converters or not converters[0]:
                pass
        except Exception as e:
            raise ValueError("You need to provide at least one converter.") from e

        super().__init__()

        # Set up the storage data
        self.table_name = table_name
        self.column_name = column_name
        self.cache_key = cache_key
        self.database_key = database_key

        # Converters
        self.key_display_function = key_display_function
        self.value_display_function = value_display_function
        self.converters = converters

        # Add callback
        self.iterable_add_callback = iterable_add_callback or SettingsMenuOption.get_set_iterable_add_callback(
            table_name=table_name,
            column_name=column_name,
            cache_key=cache_key,
            database_key=database_key,
            serialize_function=str if len(self.converters) == 1 else self.converters[1].serialize,
            original_data_type=list if len(self.converters) == 1 else dict,
        )
        # This default returns an async function which takes the content of the converted values which adds to the db.
        # Callable[
        #     [SettingsMenu, commands.Context],
        #     Callable[
        #         [SettingsMenu, *typing.Any],
        #         None
        #     ]
        # ]

        # Delete callback
        self.iterable_delete_callback = iterable_delete_callback or SettingsMenuOption.get_set_iterable_delete_callback(
            table_name=table_name,
            column_name=column_name,
            cache_key=cache_key,
            database_key=database_key,
        )
        # This default returns an async function which takes the content of the converted values which removes from the db.
        # Callable[
        #     [SettingsMenu, commands.Context, int],
        #     Callable[
        #         [SettingsMenu],
        #         None
        #     ]
        # ]

    def get_sendable_data(self, ctx: commands.Context):

        # Get the current data
        data_points = ctx.bot.guild_settings[ctx.guild.id][self.cache_key]

        # See what our display function should be
        if isinstance(data_points, dict):
            display_function = lambda i, o: f"{self.key_display_function(i)} - {self.value_display_function(o)!s}"
            corrected_data_points = data_points.items()
        elif isinstance(data_points, list):
            display_function = lambda i, _: self.key_display_function(i)
            corrected_data_points = [(i, _) for _, i in enumerate(data_points)]
        else:
            raise ValueError("Invalid cache type from database to use in an iterable.")

        # Delete buttons
        self.options = [
            SettingsMenuOption(
                ctx=ctx,
                display=display_function(i, o),
                converter_args=(),
                callback=self.iterable_delete_callback(self, ctx, i),
                allow_nullable=False,
            )
            for i, o in corrected_data_points
        ]

        # Add more buttons
        # TODO add pagination so that users can add more than 10 options
        if len(self.options) < 10:
            self.options.append(
                SettingsMenuOption(
                    ctx=ctx,
                    display="",
                    converter_args=self.converters,
                    callback=self.iterable_add_callback(self, ctx),
                    emoji=self.PLUS_EMOJI,
                    allow_nullable=False,
                )
            )

        # Generate the data as normal
        return super().get_sendable_data(ctx)
