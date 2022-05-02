import asyncio
import typing

import discord
from discord.ext import tasks

from . import utils as vbu


class PresenceAutoUpdater(vbu.Cog):

    TWITCH_TOKEN_URL = "https://id.twitch.tv/oauth2/token"
    TWITCH_SEARCH_URL = "https://api.twitch.tv/helix/streams"
    TWITCH_USERNAME_URL = "https://api.twitch.tv/helix/users"

    def __init__(self, bot: vbu.Bot):
        super().__init__(bot)
        self.presence_auto_update_loop.start()
        self.presence_before = None
        self._twitch_app_token = None
        self._refresh_token_task = None
        self.twitch_user_ids = {}  # str: str
        self._user_streaming_status = None
        self._config_embed_footers = None

    def cog_unload(self):
        self.presence_auto_update_loop.cancel()

    async def get_app_token(self, force_refresh: bool = False) -> typing.Optional[str]:
        """
        Get a valid app token from Twitch
        """

        # See if there's already one set
        if self._twitch_app_token is not None and force_refresh is False:
            return self._twitch_app_token

        # See if there's a config set
        twitch_data = self.bot.config.get("presence", {}).get("streaming", {})
        if not twitch_data:
            return None

        # Grab the token from the API
        self.logger.info("Grabbing a new Twitch.tv app token")
        json = {
            "client_id": twitch_data["twitch_client_id"],
            "client_secret": twitch_data["twitch_client_secret"],
            "grant_type": "client_credentials",
        }
        async with self.bot.session.post(self.TWITCH_TOKEN_URL, json=json) as r:
            data = await r.json()
        self.logger.debug(f"POST {self.TWITCH_TOKEN_URL} returned {data}")

        # Store it
        try:
            self._twitch_app_token = data["access_token"]
        except KeyError:
            self.logger.error("The Twitch client ID or secret in the config is invalid")
            self.presence_auto_update_loop.cancel()
            return ""

        # Set up our refresh task
        async def refresh_token_coro():
            await asyncio.sleep(data["expires_in"] - 60)
            await self.get_app_token(force_refresh=True)
        if self._refresh_token_task:
            self._refresh_token_task.cancel()
        self._refresh_token_task = self.bot.loop.create_task(refresh_token_coro())

        # And return the app token
        return self._twitch_app_token

    async def get_twitch_user_id(self, username: str) -> str:
        """
        Get the user ID for a given Twitch username.
        """

        # See if we got it already
        if username in self.twitch_user_ids:
            return self.twitch_user_ids[username]

        # Make up our request
        app_token = await self.get_app_token()
        headers = {
            "Authorization": f"Bearer {app_token}",
            "Client-Id": self.bot.config.get("presence", {}).get("streaming", {}).get("twitch_client_id"),
        }
        self.logger.info(f"Asking Twitch for the username of {username}")

        # Send the request
        async with self.bot.session.get(self.TWITCH_USERNAME_URL, params={"login": username}, headers=headers) as r:
            data = await r.json()
        self.logger.debug(f"GET {self.TWITCH_USERNAME_URL} returned {data}")

        # Get the ID of the user
        try:
            self.twitch_user_ids[username] = data["data"][0]["id"]
        except KeyError:
            self.logger.error(f"Failed to get Twitch username from search - {data.get('message') or 'no error message'}")
            raise
        except IndexError:
            self.logger.error("Invalid Twitch username set in config")
            raise
        return self.twitch_user_ids[username]

    @tasks.loop(seconds=30)
    async def presence_auto_update_loop(self):
        """
        Automatically ping the Twitch servers every 30 seconds and see if we need
        to update the bot's status to the streaming status.
        """

        # See if we should bother doing this
        twitch_data = self.bot.config.get("presence", {}).get("streaming", {})
        if not twitch_data or "" in twitch_data.values() or not twitch_data.get("twitch_usernames", list()):
            self.logger.warning("Stream presence config is either missing or invalid")
            self.presence_auto_update_loop.cancel()
            return

        # Set up the headers we want to use
        app_token = await self.get_app_token()
        headers = {
            "Authorization": f"Bearer {app_token}",
            "Client-Id": twitch_data.get("twitch_client_id"),
        }

        # Set this up so we know who to set us to
        status_to_set = None
        stream_data = None

        # Let's go through each of the usernames available and see which of them is live
        for twitch_username in twitch_data.get("twitch_usernames", list()):

            # Get their username
            twitch_user_id = await self.get_twitch_user_id(twitch_username)

            # Get their data from Twitch
            params = {
                "user_id": twitch_user_id,
                "first": 1,
            }
            async with self.bot.session.get(self.TWITCH_SEARCH_URL, params=params, headers=headers) as r:
                data = await r.json()
            self.logger.debug(f"GET {self.TWITCH_SEARCH_URL} returned {data}")

            # See if they're live
            try:
                stream_data = data["data"][0]
            except (IndexError, KeyError):
                continue  # They aren't

            # Yo sick they're live
            status_to_set = discord.Streaming(name=stream_data["title"], url=f"https://twitch.tv/{stream_data['user_name']}")
            break

        # See if we need to set to default
        if status_to_set is None:

            # It should be default already
            if self._user_streaming_status is None:
                return

            # Alright let's set
            await self.bot.set_default_presence()
            self._user_streaming_status = None
            self.bot.config.setdefault('embed', dict())['footer'] = self._config_embed_footers
            self._config_embed_footers = None
            return

        # Let's set a new streaming activity
        else:

            # Let's change the default embed footer
            if self._config_embed_footers is None:
                self._config_embed_footers = self.bot.config.get('embed', dict()).get('footer', list()).copy()
                self.bot.config.setdefault('embed', dict())['footer'] = [{"text": "Currently live on Twitch!", "amount": 1}]

            # We currently aren't streaming
            if self._user_streaming_status is None:
                await self.bot.change_presence(activity=status_to_set)
                self._user_streaming_status = status_to_set
                return

            # The stream name or URL is different
            if (status_to_set.name, status_to_set.url) != (self._user_streaming_status.name, self._user_streaming_status.url):
                await self.bot.change_presence(activity=status_to_set)
                self._user_streaming_status = status_to_set
                if status_to_set.url != self._user_streaming_status.url:
                    self.bot.dispatch("twitch_stream", vbu.TwitchStream(data=stream_data))
                return

    @presence_auto_update_loop.before_loop
    async def presence_auto_update_loop_before_loop(self):
        await self.bot.wait_until_ready()
        await asyncio.sleep(1)  # Let's sleep here so we don't override our on_ready's set default presence


def setup(bot: vbu.Bot):
    x = PresenceAutoUpdater(bot)
    bot.add_cog(x)
