"""
Copyright (c) Kae Bartlett

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

from __future__ import annotations

import asyncio
from typing import Any

import aiohttp

import novus as n
from novus.ext import client

__all__ = (
    'Twitch',
)


class LiveChannel:

    def __init__(self, data: dict):
        self.id = data["id"]
        self.user_id = data["user_id"]
        self.user_login = data["user_login"]
        self.user_name = data["user_name"]
        self.game_name = data["game_name"]
        self.title = data["title"]

    def __eq__(self, other: LiveChannel | Any) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return all((
            self.user_id == other.user_id,
            self.title == other.title,
            self.game_name == other.game_name,
        ))


class Twitch(client.Plugin):
    """
    A plugin saddled with checking if a Twitch account is live and changing
    the status accordingly.
    """

    CONFIG = {
        "twitch_client_id": "",
        "twitch_client_secret": "",
        "twitch_users": [],
    }
    USER_AGENT = "Novus Discord bot client live checker."

    async def on_load(self) -> None:
        self._access_token: str = None  # type: ignore
        self._previous_live_channels: list[LiveChannel] = []
        return await super().on_load()

    async def get_access_token(self) -> str | None:
        """
        Get the access token from Twitch and store it in a local parameter.
        """

        # See if there's already a token (and thus a running task to refresh it)
        if self._access_token is not None:
            return self._access_token

        # Format our params
        params = {
            "client_id": self.bot.config.twitch_client_id,
            "client_secret": self.bot.config.twitch_client_secret,
            "grant_type": "client_credentials",
        }
        if None in params.values() or "" in params.values():
            self.log.info("Ignoring getting Twitch client info for missing client data.")
            self.change_presence_to_live_loop.stop()
            return None  # Missing client ID or secret

        # Get the token
        async with aiohttp.ClientSession() as session:
            site = await session.post(
                "https://id.twitch.tv/oauth2/token",
                json=params,
                headers={
                    "User-Agent": self.USER_AGENT,
                },
            )
            data = await site.json()

        # Make sure we have a token
        if not data.get("access_token"):
            self.log.info("Failed to get access token from Twitch - %s", data)
            if site.status == 400:
                self.change_presence_to_live_loop.stop()
            return None

        # Store and score
        self._access_token = data["access_token"]
        expiry = data["expires_in"]
        async def get_new_token():
            await asyncio.sleep(expiry - 30)
            await self.get_access_token()
        asyncio.create_task(get_new_token())
        return self._access_token

    async def get_live_channels(self) -> list[LiveChannel] | None:
        """
        Get a list of live channels from our expected list of channels.
        """

        # Get the access token and list of people to check
        user_list: list[str] = self.bot.config.twitch_users
        if not user_list:
            return []  # Technically correct data!
        access_token = await self.get_access_token()
        if access_token is None:
            return []  # No token, let's just skip the whole loop

        # Ask the Twitch API for all the live users
        user_string = "&".join([f"user_login={i}" for i in user_list])
        async with aiohttp.ClientSession() as session:
            site = await session.get(
                f"https://api.twitch.tv/helix/streams?type=live&{user_string}",
                headers={
                    "User-Agent": self.USER_AGENT,
                    "Authorization": f"Bearer {access_token}",
                    "Client-Id": self.bot.config.twitch_client_id,
                }
            )
            try:
                data = await site.json()
            except Exception:
                return None
        self.log.info("Data back from Twitch for online streams: %s", data)

        # And return
        if not site.ok:
            return []
        return [
            LiveChannel(i)
            for i in data["data"]
        ]

    @client.loop(60)
    async def change_presence_to_live_loop(self) -> None:
        """
        Change the bot's presence to whichever channel may be live at that
        point in time.
        """

        live_channels = await self.get_live_channels()
        if live_channels is None:
            return  # Skip this loop

        self._previous_live_channels = live_channels
        if not live_channels:
            await self.bot.change_presence()
            return

        check = live_channels[0]
        await self.bot.change_presence(
            activities=[
                n.Activity(
                    f"{check.title} ({check.game_name})",
                    type=n.ActivityType.streaming,
                    url=f"https://twitch.tv/{check.user_name}",
                )
            ]
        )
