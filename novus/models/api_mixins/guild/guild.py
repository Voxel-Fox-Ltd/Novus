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
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, NoReturn, TypeAlias

from ....utils import MISSING, try_id, try_object

if TYPE_CHECKING:
    import io

    from ....api import HTTPConnection
    from ....enums import ContentFilterLevel, Locale, NotificationLevel, VerificationLevel
    from ....flags import SystemChannelFlags
    from ... import Guild, Invite
    from ...abc import Snowflake, StateSnowflake

    FileT: TypeAlias = str | bytes | io.IOBase


class GuildAPI:

    @classmethod
    async def create(cls, state: HTTPConnection, *, name: str) -> Guild:
        """
        Create a guild.

        Parameters
        ----------
        state : novus.HTTPConnection
            The API connection to create the entity with.
        name : str
            The name for the guild that you want to create.

        Returns
        -------
        novus.Guild
            The created guild.
        """

        return await state.guild.create_guild(name=name)

    @classmethod
    async def fetch(cls, state: HTTPConnection, guild: int | Snowflake) -> Guild:
        """
        Get an instance of a guild from the API. Unlike the gateway's
        ``GUILD_CREATE`` payload, this method does not return members,
        channels, or voice states.

        Parameters
        ----------
        state : HTTPConnection
            The API connection.
        guild : int | novus.abc.Snowflake
            A reference to the guild that you want to fetch.

        Returns
        -------
        novus.Guild
            The guild associated with the given ID.
        """

        return await state.guild.get_guild(try_id(guild))

    async def fetch_preview(self: StateSnowflake) -> NoReturn:
        raise NotImplementedError()

    async def edit(
            self: StateSnowflake,
            *,
            name: str = MISSING,
            verification_level: VerificationLevel | None = MISSING,
            default_message_notifications: NotificationLevel | None = MISSING,
            explicit_content_filter: ContentFilterLevel | None = MISSING,
            afk_channel: int | Snowflake | None = MISSING,
            icon: FileT | None = MISSING,
            owner: int | Snowflake = MISSING,
            splash: FileT | None = MISSING,
            discovery_splash: FileT | None = MISSING,
            banner: FileT | None = MISSING,
            system_channel: int | Snowflake | None = MISSING,
            system_channel_flags: SystemChannelFlags | None = MISSING,
            rules_channel: int | Snowflake | None = MISSING,
            preferred_locale: Locale | None = MISSING,
            public_updates_channel: int | Snowflake = MISSING,
            features: list[str] = MISSING,
            description: str | None = MISSING,
            premium_progress_bar_enabled: bool = MISSING,
            reason: str | None = None) -> Guild:
        """
        Edit the guild parameters.

        .. note::

            The updated guild is not immediately put into cache - the bot
            waits for the guild update notification to be sent over the
            gateway before updating (which will not happen if you don't have
            the correct gateway intents).

        Parameters
        ----------
        name : str
            The name you want to set the guild to.
        verification_level : novus.guild.VerificationLevel | None
            The verification level you want to set the guild to.
        default_message_notifications : novus.guild.NotificationLevel | None
            The default message notification level you want to set the guild to.
        explicit_content_filter : novus.guild.ContentFilterLevel | None
            The content filter level you want to set the guild to.
        afk_channel : int | novus.abc.Snowflake | None
            The channel you want to set as the guild's AFK channel.
        icon : str | bytes | io.IOBase | None
            The icon that you want to set for the guild. Can be its bytes, a
            file path, or a file object.
        owner : int | novus.abc.Snowflake
            The person you want to set as owner of the guild. Can only be run
            if the current user is the existing owner.
        splash : str | bytes | io.IOBase | None
            The splash that you want to set for the guild. Can be its bytes, a
            file path, or a file object.
        discovery_splash : str | bytes | io.IOBase | None
            The discovery splash for the guild. Can be its bytes, a file path,
            or a file object.
        banner : str | bytes | io.IOBase | None
            The banner for the guild. Can be its bytes, a file path, or a file
            object.
        system_channel : int | novus.abc.Snowflake | None
            The system channel you want to set for the guild.
        system_channel_flags : novus.guild.SystemChannelFlags | None
            The system channel flags you want to set.
        rules_channel : int | novus.abc.Snowflake | None
            The channel you want to set as the rules channel.
        preferred_locale : Locale | None
            The locale you want to set as the guild's preferred.
        public_updates_channel : int | novus.abc.Snowflake
            The channel you want to set as the updates channel for the guild.
        features : list[str]
            A list of features for the guild.
        description : str | None
            A description for the guild.
        premium_progress_bar_enabled : bool
            Whether or not to enable the premium progress bar for the guild.
        reason : str | None
            A reason for modifying the guild (shown in the audit log).

        Returns
        -------
        novus.Guild
            The updated guild.
        """

        updates: dict[str, Any] = {}

        if name is not MISSING:
            updates["name"] = name
        if verification_level is not MISSING:
            updates["verification_level"] = verification_level
        if default_message_notifications is not MISSING:
            updates["default_message_notifications"] = default_message_notifications
        if explicit_content_filter is not MISSING:
            updates["explicit_content_filter"] = explicit_content_filter
        if afk_channel is not MISSING:
            updates["afk_channel"] = try_object(afk_channel)
        if icon is not MISSING:
            updates["icon"] = icon
        if owner is not MISSING:
            updates["owner"] = try_object(owner)
        if splash is not MISSING:
            updates["splash"] = splash
        if discovery_splash is not MISSING:
            updates["discovery_splash"] = discovery_splash
        if banner is not MISSING:
            updates["banner"] = banner
        if system_channel is not MISSING:
            updates["system_channel"] = try_object(system_channel)
        if system_channel_flags is not MISSING:
            updates["system_channel_flags"] = system_channel_flags
        if rules_channel is not MISSING:
            updates["rules_channel"] = try_object(rules_channel)
        if preferred_locale is not MISSING:
            updates["preferred_locale"] = preferred_locale
        if public_updates_channel is not MISSING:
            updates["public_updates_channel"] = try_object(public_updates_channel)
        if features is not MISSING:
            updates["features"] = features
        if description is not MISSING:
            updates["description"] = description
        if premium_progress_bar_enabled is not MISSING:
            updates["premium_progress_bar_enabled"] = premium_progress_bar_enabled

        return await self.state.guild.modify_guild(
            self.id,
            reason=reason,
            **updates,
        )

    async def delete(self: StateSnowflake) -> None:
        """
        Delete the current guild permanently. You must be the owner of the
        guild to run this successfully.
        """

        await self.state.guild.delete_guild(self.id)
        return None

    async def edit_mfa_level(self) -> NoReturn:
        raise NotImplementedError()

    async def fetch_prune_count(self) -> NoReturn:
        raise NotImplementedError()

    async def prune(self) -> NoReturn:
        raise NotImplementedError()

    async def fetch_voice_regions(self) -> NoReturn:
        raise NotImplementedError()

    async def fetch_invites(self: StateSnowflake) -> list[Invite]:
        """
        Get the invites for the guild.

        Requires the ``MANAGE_GUILD`` permission.

        Returns
        -------
        list[novus.Invite]
            A list of invites.
        """

        return await self.state.guild.get_guild_invites(self.id)

    async def fetch_integrations(self) -> NoReturn:
        raise NotImplementedError()

    async def delete_integration(self) -> NoReturn:
        raise NotImplementedError()

    async def fetch_widget(self) -> NoReturn:
        raise NotImplementedError()

    async def edit_widget(self) -> NoReturn:
        raise NotImplementedError()

    async def edit_vainity_url(self) -> NoReturn:
        raise NotImplementedError()

    async def edit_widget_image(self) -> NoReturn:
        raise NotImplementedError()

    async def fetch_welcome_screen(self) -> NoReturn:
        raise NotImplementedError()

    async def edit_welcome_screen(self) -> NoReturn:
        raise NotImplementedError()

    async def edit_member_voice_state(self) -> NoReturn:
        raise NotImplementedError()

    async def edit_my_voice_state(self) -> NoReturn:
        raise NotImplementedError()
