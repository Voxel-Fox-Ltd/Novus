from __future__ import annotations

import typing

import discord
from discord.ext import commands

if typing.TYPE_CHECKING:
    from .custom_bot import Bot


MISSING = discord.utils.MISSING


class Embeddify:
    """
    A class to handle auto-embeddifying of messages.
    """

    bot: typing.Optional[Bot] = None

    @classmethod
    async def send(
            cls,
            dest: typing.Union[discord.abc.Messageable, discord.Webhook],
            content: typing.Optional[str],
            **kwargs,
            ) -> discord.Message:
        return await dest.send(**cls.get_embeddify(dest, content, **kwargs))

    @classmethod
    def get_embeddify(
            cls,
            dest: typing.Union[discord.abc.Messageable, discord.Webhook],
            content: typing.Optional[str] = MISSING,
            *,
            embed: discord.Embed = MISSING,
            embeds: typing.List[discord.Embed] = MISSING,
            file: discord.File = MISSING,
            embeddify: bool = MISSING,
            image_url: str = MISSING,
            **kwargs,
            ) -> dict:
        """
        Embeddify your given content.
        """

        # # Make sure we have a bot to read the config of
        # try:
        #     assert cls.bot
        # except AssertionError:
        #     return {
        #         "content": content,
        #         "embeds": embeds if embeds else [embed] if embed else None,
        #         **kwargs
        #     }

        # Initial dataset
        data = {
            "content": content,
            "embeds": [],
            **kwargs,
        }
        if embed and embeds:
            raise ValueError("Can't set embeds and embed")
        if embed:
            data['embeds'].append(embed)
        elif embeds:
            data['embeds'].extend(embeds)

        # If embeddify isn't set, grab from the config
        if embeddify is MISSING and cls.bot:
            embeddify = cls.bot.embeddify
        elif embeddify is MISSING:
            embeddify = True

        # See if we're done now
        if embeddify is False:
            return data

        # People testing can do anything
        if dest is None:
            can_send_embeds = True

        # Slash commands can do anything
        elif isinstance(dest, (commands.SlashContext, discord.User, discord.Member)):
            can_send_embeds = True

        # Otherwise we have permissions to check
        else:

            # Grab the channel
            if isinstance(dest, commands.Context):
                channel = dest.channel
            else:
                channel = dest

            # Check permissions
            if isinstance(channel, discord.TextChannel):
                channel_permissions: discord.Permissions = channel.permissions_for(dest.guild.me)  # type: ignore
                can_send_embeds = discord.Permissions(embed_links=True).is_subset(channel_permissions)
            else:
                can_send_embeds = True

        # See if we should bother generating embeddify
        should_generate_embeddify = can_send_embeds and embeddify

        # Can't embed or have no content? Just send it normally
        if not should_generate_embeddify:
            return data

        # Okay it's embed time
        if cls.bot:
            colour = discord.Colour.random() or cls.bot.config.get("embed", dict()).get("colour", 0)
        else:
            colour = discord.Colour.random()
        embed = discord.Embed(
            description=data.pop("content"),
            colour=colour,
        )
        if cls.bot:
            cls.bot.set_footer_from_config(embed)

        # Add image
        if image_url not in (None, MISSING):
            embed.set_image(url=image_url)
        elif file not in (None, MISSING) and file and file.filename and file.filename.endswith((".png", ".jpg", ".jpeg", ".webm", ".gif")):
            data["file"] = file
            embed.set_image(url=f"attachment://{file.filename}")

        # Reset content
        if cls.bot:
            content = cls.bot.config.get("embed", dict()).get("content", "").format(bot=cls.bot)
        else:
            content = None
        if not content:
            content = None
        data["content"] = content

        # Set author
        if cls.bot:
            author_data = cls.bot.config.get("embed", dict()).get("author", {})
        else:
            author_data = {}
        if author_data.get("enabled", False):
            name = author_data.get("name", "").format(bot=cls.bot) or discord.Embed.Empty
            url = author_data.get("url", "").format(bot=cls.bot) or discord.Embed.Empty
            try:
                icon_url: typing.Optional[str] = cls.bot.user.display_avatar.url  # type: ignore
            except AttributeError:
                icon_url = None
            embed.set_author(name=name, url=url, icon_url=icon_url)

        # And we're done and sick and sexy
        data['embeds'].insert(0, embed)
        return data
