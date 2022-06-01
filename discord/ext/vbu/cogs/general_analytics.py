import json

import discord
from discord.ext import tasks

from . import utils as vbu


class Analytics(vbu.Cog):

    FOUND_GATEWAY_OPCODES = {}

    def __init__(self, bot: vbu.Bot):
        super().__init__(bot)
        self.post_statsd_guild_count.start()
        self.post_topgg_guild_count.start()
        self.post_discordbotlist_guild_count.start()

    def cog_unload(self):
        self.logger.info("Stopping Statsd guild count poster loop")
        self.post_statsd_guild_count.cancel()
        self.logger.info("Stopping Top.gg guild count poster loop")
        self.post_topgg_guild_count.cancel()
        self.logger.info("Stopping DiscordbotList.com guild count poster loop")
        self.post_discordbotlist_guild_count.cancel()

    def get_effective_guild_count(self) -> int:
        return int((len(self.bot.guilds) / len(self.bot.shard_ids or [0])) * (self.bot.shard_count or 1))

    @tasks.loop(minutes=5)
    async def post_topgg_guild_count(self):
        """
        Post the average guild count to Top.gg.
        """

        # Only shard 0 can post
        if 0 not in (self.bot.shard_ids or [0]):
            return

        # Only post if there's actually a DBL token set
        if not self.bot.config.get('bot_listing_api_keys', {}).get('topgg_token'):
            self.logger.warning("No Top.gg token has been provided")
            self.post_topgg_guild_count.stop()
            return

        url = f'https://top.gg/api/bots/{self.bot.user.id}/stats'
        data = {
            'server_count': self.get_effective_guild_count(),
            'shard_count': self.bot.shard_count or 1,
            'shard_id': 0,
        }
        headers = {
            'Authorization': self.bot.config['bot_listing_api_keys']['topgg_token']
        }
        self.logger.info(f"Sending POST request to Top.gg with data {json.dumps(data)}")
        async with self.bot.session.post(url, json=data, headers=headers):
            pass

    @post_topgg_guild_count.before_loop
    async def before_post_guild_count(self):
        await self.bot.wait_until_ready()

    @tasks.loop(minutes=5)
    async def post_discordbotlist_guild_count(self):
        """
        Post the average guild count to DiscordBotList.com.
        """

        # Only shard 0 can post
        if self.bot.shard_count and self.bot.shard_count > 1 and 0 not in self.bot.shard_ids:
            return

        # Only post if there's actually a DBL token set
        if not self.bot.config.get('bot_listing_api_keys', {}).get('discordbotlist_token'):
            self.logger.warning("No DiscordBotList.com token has been provided")
            self.post_discordbotlist_guild_count.stop()
            return

        url = f'https://discordbotlist.com/api/v1/bots/{self.bot.user.id}/stats'
        data = {
            'guilds': self.get_effective_guild_count(),
        }
        headers = {
            'Authorization': self.bot.config['bot_listing_api_keys']['discordbotlist_token']
        }
        self.logger.info(f"Sending POST request to DiscordBotList.com with data {json.dumps(data)}")
        async with self.bot.session.post(url, json=data, headers=headers):
            pass

    @post_discordbotlist_guild_count.before_loop
    async def before_post_discordbotlist_guild_count(self):
        await self.bot.wait_until_ready()

    @tasks.loop(minutes=1)
    async def post_statsd_guild_count(self):
        """
        Post the average guild count to Statsd
        """

        # Work out how many guilds to a shard
        shard_guilds = {}
        for i in (self.bot.shard_ids or [0]):
            shard_guilds[i] = 0
        for guild in self.bot.guilds:
            shard_guilds[guild.shard_id] += 1

        # Post that value
        async with self.bot.stats() as stats:
            for shard_id, count in shard_guilds.items():
                stats.gauge(
                    "discord.stats.guild_count",
                    value=count,
                    tags={
                        "shard_id": shard_id,
                        "cluster": self.bot.cluster,
                    },
                )
            stats.gauge("discord.stats.shard_count", value=self.bot.shard_count or 1)

    @post_statsd_guild_count.before_loop
    async def before_post_statsd_guild_count(self):
        await self.bot.wait_until_ready()

    @vbu.Cog.listener()
    async def on_socket_raw_send(self, payload: dict):
        """
        A raw socket response message send Discord.
        """

        # Get the event opcode
        try:
            event_id = json.loads(payload)['op']
        except Exception:
            return  # there isn't one somehow but okay

        # Try and get a name from that opcode
        event_name = self.FOUND_GATEWAY_OPCODES.get(event_id)
        if event_name is None:
            for i in dir(discord.gateway.DiscordWebSocket):
                if i.isupper():
                    o = getattr(discord.gateway.DiscordWebSocket, i, None)
                    if type(o) is int:
                        self.FOUND_GATEWAY_OPCODES[o] = i
                        if event_id == o:
                            event_name = i
                            break

        # Post that to statsd
        async with self.bot.stats() as stats:
            try:
                stats.increment("discord.gateway.send", tags={"event_name": event_name})
            except KeyError:
                pass

    @vbu.Cog.listener()
    async def on_socket_response(self, payload: dict):
        """
        A raw socket response message from Discord.
        """

        async with self.bot.stats() as stats:
            try:
                stats.increment("discord.gateway.receive", tags={"event_name": payload['t']})
            except KeyError:
                pass

    @vbu.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        """
        Pinged when the bot joins a guild
        """

        async with self.bot.stats() as stats:
            stats.increment("discord.stats.guild_joins")

    @vbu.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        """
        Pinged when the bot joins a guild
        """

        async with self.bot.stats() as stats:
            stats.decrement("discord.stats.guild_joins")


def setup(bot: vbu.Bot):
    x = Analytics(bot)
    bot.add_cog(x)
