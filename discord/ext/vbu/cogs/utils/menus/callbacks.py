from __future__ import annotations

import enum
from typing import (
    TYPE_CHECKING,
    Callable,
    List,
    Any,
    Union,
    Awaitable
)

import discord

if TYPE_CHECKING:
    from discord.ext import commands, vbu
    AnyContext = Union[
        vbu.Context,
        vbu.SlashContext,
        commands.Context,
        commands.SlashContext,
    ]


class DataLocation(enum.Enum):
    """
    A defined location for your bot to store information.

    Attributes:
        GUILD: If the information you want to store is guild-based.
        USER: If the information you want to store is user-based.
    """

    GUILD = enum.auto()
    USER = enum.auto()


class MenuCallbacks(object):

    @staticmethod
    def _is_discord_object(item) -> bool:
        return isinstance(
            item,
            (
                discord.TextChannel,
                discord.VoiceChannel,
                discord.Role,
                discord.Member,
                discord.Guild,
                discord.Object,
            )
        )

    @classmethod
    def set_table_column(
            cls,
            data_location: DataLocation,
            table_name: str,
            column_name: str,
            ) -> Callable[..., Awaitable[None]]:
        """
        Returns a wrapper that updates the guild settings table for the bot's database.

        Args:
            data_location (voxelbotutils.menus.DataLocation): The location of the content to be stored.
            table_name (str): The name of the table that you want to store the data in.
            column_name (str): The name of the column that should be set.

        Returns:
            typing.Callable[[discord.ext.commands.Context, typing.List[typing.Any]]]: An async wrapper method
                that does the actual work of adding data to your database. It takes the context object from
                the menu, and the list of returned converted arguments.
        """

        async def wrapper(ctx, data: list):
            prep = ctx.bot.database.driver().prepare()
            insert_sql = f"""INSERT INTO {{0}} ({{1}}, {{2}}) VALUES ({next(prep)}, {next(prep)})"""
            prep = ctx.bot.database.driver().prepare()
            conflict_sql = f"""UPDATE {{0}} SET {{2}}={next(prep)} WHERE {{1}}={next(prep)}"""
            args = (
                table_name,
                "guild_id" if data_location == DataLocation.GUILD else "user_id" if data_location == DataLocation.USER else None,
                column_name
            )
            data = [i.id if cls._is_discord_object(i) else i for i in data]
            async with ctx.bot.database() as db:
                try:
                    await db(
                        insert_sql.format(*args),
                        ctx.guild.id if data_location == DataLocation.GUILD else ctx.author.id if data_location == DataLocation.USER else None,
                        *data,
                    )
                except Exception:  # Hopefully it's a unique violation error
                    await db(
                        conflict_sql.format(*args),
                        *data,
                        ctx.guild.id if data_location == DataLocation.GUILD else ctx.author.id if data_location == DataLocation.USER else None,
                    )

        return wrapper

    @classmethod
    def set_cache_from_key(
            cls,
            data_location: DataLocation,
            *settings_path: str,
            ) -> Callable[[AnyContext, List[Any]], None]:
        """
        Returns a wrapper that changes the :attr:`voxelbotutils.Bot.guild_settings` internal cache.

        Args:
            data_location (voxelbotutils.menus.DataLocation): The location of the content to be stored.
            *settings_path (str): The path of keys in your cache dictionary to get to the location desired.
                The last key in the settings path should be the primary key that the converted data gets
                added as.

        Returns:
            typing.Callable[[discord.ext.commands.Context, typing.List[typing.Any]]]: A wrapper method
                that does the actual work of adding data to your cache. It takes the context object from
                the menu, and the list of returned converted arguments.
        """

        def wrapper(ctx, data: list):
            value = data[0]  # If we're here we definitely should only have one datapoint
            if cls._is_discord_object(value):
                value = value.id
            if data_location == DataLocation.GUILD:
                d = ctx.bot.guild_settings[ctx.guild.id]
            elif data_location == DataLocation.USER:
                d = ctx.bot.user_settings[ctx.author.id]
            for i in settings_path[:-1]:
                d = d.setdefault(i, dict())
            d[settings_path[-1]] = value

        return wrapper

    @classmethod
    def set_cache_from_keypair(
            cls,
            data_location: DataLocation,
            *settings_path: str,
            ) -> Callable[[AnyContext, List[Any]], None]:
        """
        Returns a wrapper that changes the :attr:`voxelbotutils.Bot.guild_settings` internal cache.

        Args:
            data_location (voxelbotutils.menus.DataLocation): The location of the content to be stored.
            *settings_path (str): The path of keys in your cache dictionary to get to the location desired.
                This method assumes that the data given includes both a key and a value, and the settings
                path leads to the *dictionary* that the data should be cached into.

        Returns:
            typing.Callable[[discord.ext.commands.Context, typing.List[typing.Any]]]: A wrapper method
                that does the actual work of adding data to your cache. It takes the context object from
                the menu, and the list of returned converted arguments.
        """

        def wrapper(ctx, data: list):
            key, value = data  # Two datapoints now; that's very sexy
            if cls._is_discord_object(key):
                key = key.id
            if cls._is_discord_object(value):
                value = value.id
            if data_location == DataLocation.GUILD:
                d = ctx.bot.guild_settings[ctx.guild.id]
            elif data_location == DataLocation.USER:
                d = ctx.bot.user_settings[ctx.author.id]
            for i in settings_path:
                d = d.setdefault(i, dict())
            d[key] = value

        return wrapper

    set_iterable_dict_cache = set_cache_from_keypair  # Just for consistency of method names

    @classmethod
    def set_iterable_list_cache(
            cls,
            data_location: DataLocation,
            *settings_path: str,
            ) -> Callable[[AnyContext, List[Any]], None]:
        """
        Returns a wrapper that changes the :attr:`voxelbotutils.Bot.guild_settings` internal cache.

        Args:
            data_location (voxelbotutils.menus.DataLocation): The location of the content to be stored.
            *settings_path (str): The path of keys in your cache dictionary to get to the location desired.
                This method assumes that the data given includes both a key and a value, and the settings
                path leads to the *list* that the data should be cached into.

        Returns:
            typing.Callable[[discord.ext.commands.Context, typing.List[typing.Any]]]: A wrapper method
                that does the actual work of adding data to your cache. It takes the context object from
                the menu, and the list of returned converted arguments.
        """

        def wrapper(ctx, data: list):
            value = data[0]  # If we're here we definitely should only have one datapoint
            if cls._is_discord_object(value):
                value = value.id
            if data_location == DataLocation.GUILD:
                d = ctx.bot.guild_settings[ctx.guild.id]
            elif data_location == DataLocation.USER:
                d = ctx.bot.user_settings[ctx.author.id]
            for i in settings_path[:-1]:
                d = d.setdefault(i, dict())
            settings_list = d.setdefault(settings_path[-1], list())
            if value in settings_list:
                return
            else:
                settings_list.append(value)

        return wrapper

    @classmethod
    def delete_iterable_dict_cache(
            cls,
            data_location: DataLocation,
            *settings_path: str,
            ) -> Callable[[str], Callable[[AnyContext, List[Any]], None]]:
        """
        Returns a wrapper that changes the :attr:`voxelbotutils.Bot.guild_settings` internal cache.
        Gives a nested function that takes a :code:`key` argument that acts as the primary key of the dict.

        Args:
            data_location (voxelbotutils.menus.DataLocation): The location of the content to be stored.
            *settings_path (str): The path of keys in your cache dictionary to get to the location desired.
                This method assumes that the settings path leads to the *dictionary* that the data
                should be removed from the cache of.

        Returns:
            typing.Callable[[str], typing.Callable[[discord.ext.commands.Context, typing.List[typing.Any]]]]: A
                wrapper method that does the actual work of removing data from your cache. The first wrapper takes
                the key of the dictionary that should be removed. The second wrapper takes the context object from
                the menu, and the list of returned converted arguments. Both wrappers are necessary as the outer wrapper
                is used internally by the :class:`voxelbotutils.menus.MenuIterable` to make it similar to a method that
                :class:`voxelbotutils.menus.Menu` uses.
        """

        def inner(key: str):
            def wrapper(ctx, data: list):
                if data_location == DataLocation.GUILD:
                    d = ctx.bot.guild_settings[ctx.guild.id]
                elif data_location == DataLocation.USER:
                    d = ctx.bot.user_settings[ctx.author.id]
                for i in settings_path:
                    d = d.setdefault(i, dict())
                d.pop(key, None)
            return wrapper
        return inner

    @classmethod
    def delete_iterable_list_cache(
            cls,
            data_location: DataLocation,
            *settings_path: str,
            ) -> Callable[[Any], Callable[[AnyContext, List[Any]], None]]:
        """
        Returns a wrapper that changes the :attr:`voxelbotutils.Bot.guild_settings` internal cache.
        Gives a nested function that takes a :code:`value` argument that acts as the data to delete.

        Args:
            data_location (voxelbotutils.menus.DataLocation): The location of the content to be stored.
            *settings_path (str): The path of keys in your cache dictionary to get to the location desired.
                This method assumes that the settings path leads to the *list* that the data
                should be removed from the cache of.

        Returns:
            typing.Callable[[Any], typing.Callable[[discord.ext.commands.Context, typing.List[typing.Any]]]]: A
                wrapper method that does the actual work of removing data from your cache. The first wrapper takes
                the value that should be removed. The second wrapper takes the context object from
                the menu, and the list of returned converted arguments. Both wrappers are necessary as the outer wrapper
                is used internally by the :class:`voxelbotutils.menus.MenuIterable` to make it similar to a method that
                :class:`voxelbotutils.menus.Menu` uses.
        """

        def inner(value: Any):
            def wrapper(ctx, data: list):
                if data_location == DataLocation.GUILD:
                    d = ctx.bot.guild_settings[ctx.guild.id]
                elif data_location == DataLocation.USER:
                    d = ctx.bot.user_settings[ctx.author.id]
                for i in settings_path[:-1]:
                    d = d.setdefault(i, dict())
                settings_list = d.setdefault(settings_path[-1], list())
                if value not in settings_list:
                    return
                else:
                    settings_list.remove(value)
            return wrapper
        return inner
