from importlib import metadata
import sys
import typing
import textwrap

import discord
from discord.ext import commands

from . import utils as vbu


class BotStats(vbu.Cog):

    @commands.command(
        application_command_meta=commands.ApplicationCommandMeta(),
    )
    @commands.defer()
    @vbu.checks.is_config_set('bot_info', 'enabled')
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def info(self, ctx: vbu.Context):
        """
        Gives you information about the bot, including some important links, such as its invite.
        """

        # Get the info embed
        bot_info = self.bot.config.get("bot_info", {})
        info_embed = vbu.Embed(
            description=textwrap.dedent(bot_info.get("content", "")).format(bot=self.bot),
        ).set_author_to_user(
            self.bot.user,
        )

        # See if we have images
        if bot_info.get("thumbnail"):
            info_embed.set_thumbnail(bot_info["thumbnail"])
        if bot_info.get("image"):
            info_embed.set_image(bot_info["image"])

        # Make up our buttons
        links = bot_info.get("links", dict())
        buttons = []
        if (invite_link := self.get_invite_link()):
            buttons.append(
                discord.ui.Button(
                    label="Invite",
                    url=invite_link,
                    style=discord.ui.ButtonStyle.link,
                )
            )
        for label, info in links.items():
            buttons.append(
                discord.ui.Button(
                    emoji=info.get("emoji") or None,
                    label=label,
                    url=info['url'],
                    style=discord.ui.ButtonStyle.link
                )
            )
        components = discord.ui.MessageComponents.add_buttons_with_rows(*buttons)

        # See if we want to include stats
        embeds = [info_embed]
        if bot_info.get("include_stats"):
            embeds.append(await self.get_stats_embed())

        # And send
        return await ctx.send(embeds=embeds, components=components)

    def get_invite_link(self):
        """
        Get the invite link for the bot.
        """

        if not self.bot.config.get("oauth", {}).get("enabled", True):
            return None
        oauth = self.bot.config.get("oauth", {}).copy()
        permissions = discord.Permissions.none()
        for i in oauth.pop('permissions', list()):
            setattr(permissions, i, True)
        oauth['permissions'] = permissions
        return self.bot.get_invite_link(**oauth)

    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    @vbu.checks.is_config_set('oauth', 'enabled')
    async def invite(self, ctx: vbu.Context):
        """
        Gives you the bot's invite link.
        """

        await ctx.send(f"<{self.get_invite_link()}>")

    @commands.command()
    @commands.bot_has_permissions(send_messages=True)
    @vbu.checks.is_config_set('bot_listing_api_keys', 'topgg_token')
    async def vote(self, ctx: vbu.Context):
        """
        Gives you a link to vote for the bot.
        """

        bot_user_id = self.bot.user.id
        output_strings = []
        if self.bot.config.get('bot_listing_api_keys', {}).get("topgg_token"):
            output_strings.append(f"<https://top.gg/bot/{bot_user_id}/vote>")
        if self.bot.config.get('bot_listing_api_keys', {}).get("discordbotlist_token"):
            output_strings.append(f"<https://discordbotlist.com/bots/{bot_user_id}/upvote>")
        if not output_strings:
            return await ctx.send("Despite being enabled, the vote command has no vote links to provide :/")
        return await ctx.send("\n".join(output_strings))

    async def get_stats_embed(self) -> typing.Union[discord.Embed, vbu.Embed]:
        """
        Get the stats embed - now as a function so I can use it in multiple places.
        """

        # Get creator info
        try:
            creator_id = self.bot.config["owners"][0]
            creator = self.bot.get_user(creator_id) or await self.bot.fetch_user(creator_id)
        except IndexError:
            creator_id = None
            creator = None

        # Make embed
        embed = vbu.Embed(use_random_colour=True)
        if creator_id:
            embed.add_field("Creator", f"{creator!s}\n{creator_id}")

        # Add version info
        novus_meta = metadata.metadata("novus")
        embed.add_field("Library", (
            f"Python `{sys.version.split(' ', 1)[0]}`\n"
            f"[Novus]({novus_meta['Home-page']}) `{novus_meta['Version']}`\n"
        ))

        # Add guild count
        if self.bot.guilds:
            if self.bot.shard_count != len((self.bot.shard_ids or [0])):
                embed.add_field(
                    "Approximate Guild Count",
                    f"{int((len(self.bot.guilds) / len(self.bot.shard_ids or [0])) * self.bot.shard_count):,}",
                )
            else:
                embed.add_field("Guild Count", f"{len(self.bot.guilds):,}")
        if self.bot.latency >= 0:
            embed.add_field("Shard Count", f"{self.bot.shard_count or 1:,}")
            embed.add_field("Average WS Latency", f"{(self.bot.latency * 1000):.2f}ms")

        # Get topgg data
        if self.bot.config.get('bot_listing_api_keys', {}).get("topgg_token"):
            params = {"fields": "points,monthlyPoints"}
            headers = {"Authorization": self.bot.config['bot_listing_api_keys']['topgg_token']}
            async with self.bot.session.get(f"https://top.gg/api/bots/{self.bot.user.id}", params=params, headers=headers) as r:
                try:
                    data = await r.json()
                except Exception:
                    data = {}
            if "points" in data and "monthlyPoints" in data:
                embed.add_field(
                    "Bot Votes",
                    f"[Top.gg](https://top.gg/bot/{self.bot.user.id}): {data['points']:,} ({data['monthlyPoints']:,} this month)",
                )

        # Get discordbotlist data
        if self.bot.config.get('bot_listing_api_keys', {}).get("discordbotlist_token"):
            async with self.bot.session.get(f"https://discordbotlist.com/api/v1/bots/{self.bot.user.id}") as r:
                try:
                    data = await r.json()
                except Exception:
                    data = {}
            if "upvotes" in data and "metrics" in data:
                content = {
                    "name": "Bot Votes",
                    "value": f"[DiscordBotList.com](https://discordbotlist.com/bots/{self.bot.user.id}): {data['metrics'].get('upvotes', 0):,} ({data['upvotes']:,} this month)"
                }
                try:
                    current_data = embed.get_field_by_key("Bot Votes")
                    content['value'] = current_data['value'] + '\n' + content['value']
                    embed.edit_field_by_key("Bot Votes", **content)
                except KeyError:
                    embed.add_field(**content)
            elif "upvotes" in data:
                content = {
                    "name": "Bot Votes",
                    "value": f"[DiscordBotList.com](https://discordbotlist.com/bots/{self.bot.user.id}): {data['upvotes']:,}"
                }
                try:
                    current_data = embed.get_field_by_key("Bot Votes")
                    content['value'] = current_data['value'] + '\n' + content['value']
                    embed.edit_field_by_key("Bot Votes", **content)
                except KeyError:
                    embed.add_field(**content)

        return embed

    @commands.command(aliases=['status', 'botinfo'])
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def stats(self, ctx: vbu.Context):
        """
        Gives you the stats for the bot.
        """

        embed = await self.get_stats_embed()
        await ctx.send(embed=embed)


def setup(bot: vbu.Bot):
    x = BotStats(bot)
    bot.add_cog(x)
