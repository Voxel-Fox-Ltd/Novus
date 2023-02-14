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

import json
import logging
from typing import TYPE_CHECKING, Any, AsyncIterator, Callable, TypeAlias, TypeVar, cast

from ...models import Channel, Guild, GuildMember, Invite, Message, Role, User
from ...models.channel import channel_builder
from ...utils import try_snowflake

if TYPE_CHECKING:
    from ... import Intents, payloads
    from ...payloads import gateway as gw
    from .._http import HTTPConnection


__all__ = (
    'GatewayDispatch',
)


log = logging.getLogger("novus.gateway.dispatch")
dump = json.dumps


ReturnType = TypeVar("ReturnType")
AI = AsyncIterator
Ret: TypeAlias = AI[tuple[str, ReturnType]]
OptRet: TypeAlias = AI[tuple[str, ReturnType] | None]


class Event:

    def __init__(self, name: str, data: Any):
        self.name = name
        self.data = data


class GatewayDispatch:

    def __init__(self, parent: HTTPConnection) -> None:
        self.parent = parent
        self.cache = self.parent.cache
        self.EVENT_HANDLER: dict[
            str,
            Callable[
                [Any],  # dict, but we know about it
                # Awaitable[tuple[str, Any] | None],
                OptRet,
            ]
        ]
        self.EVENT_HANDLER = {
            # "Application command permissions update": None,
            # "Auto moderation rule create": None,
            # "Auto moderation rule update": None,
            # "Auto moderation rule delete": None,
            # "Auto moderation action execution": None,
            "CHANNEL_CREATE": self._handle_channel_create,
            "CHANNEL_UPDATE": self._handle_channel_update,
            "CHANNEL_DELETE": self._handle_channel_delete,
            "CHANNEL_PINS_UPDATE": self._handle_channel_pins_update,
            # "Thread create": None,
            # "Thread update": None,
            # "Thread delete": None,
            # "Thread list sync": None,
            # "Thread member update": None,
            # "Thread members update": None,
            "GUILD_CREATE": self._handle_guild_create,
            "GUILD_UPDATE": self._handle_guild_update,
            # "Guild delete": None,
            # "Guild audit log entry create": None,
            "GUILD_BAN_ADD": self._handle_guild_ban,
            "GUILD_BAN_REMOVE": self._handle_guild_unban,
            # "Guild emojis update": None,
            # "Guild stickers update": None,
            # "Guild integrations update": None,
            "GUILD_MEMBER_ADD": self._handle_guild_member_add,
            "GUILD_MEMBER_REMOVE": self._handle_guild_member_remove,
            "GUILD_MEMBER_UPDATE": self._handle_guild_member_update,
            # "Guild members chunk": None,
            "GUILD_ROLE_CREATE": self._handle_role_create,
            "GUILD_ROLE_UPDATE": self._handle_role_update,
            "GUILD_ROLE_DELETE": self._handle_role_delete,
            # "Guild scheduled event create": None,
            # "Guild scheduled event update": None,
            # "Guild scheduled event delete": None,
            # "Guild scheduled event user add": None,
            # "Guild scheduled event user remove": None,
            # "Integration create": None,
            # "Integration update": None,
            # "Integration delete": None,
            # "Interaction create": None,
            "INVITE_CREATE": self._handle_invite_create,
            "INVITE_DELETE": self._handle_invite_delete,
            "MESSAGE_CREATE": self._handle_message_create,
            "MESSAGE_UPDATE": self._handle_message_edit,
            "MESSAGE_DELETE": self._handle_message_delete,
            # "Message delete bulk": None,
            # "MESSAGE_REACTION_ADD": self._handle_message_reaction_add,
            # "Message reaction remove": None,
            # "Message reaction remove all": None,
            # "Message reaction remove emoji": None,
            "PRESENCE_UPDATE": self._handle_presence_update,
            # "Stage instance create": None,
            # "Stage instance update": None,
            # "Stage instance delete": None,
            "TYPING_START": self._handle_typing,
            # "User update": None,
            # "Voice state update": None,
            # "Voice server update": None,
            # "Webhooks update": None,
        }

    @property
    def intents(self) -> Intents:
        return self.parent.gateway.intents

    async def handle_dispatch(self, event_name: str, data: dict) -> None:
        """
        Handle a Dispatch message from Discord.
        """

        if event_name == "READY":
            self.cache.user = User(state=self.parent, data=data['user'])
            self.cache.application_id = try_snowflake(data['application']['id'])
            self.resume_url = data['resume_gateway_url']
            self.session_id = data['session_id']
            return None

        coro = self.EVENT_HANDLER.get(event_name)
        results: list[tuple[str, Any]] = []
        if coro is None:
            log.warning(
                "Failed to parse event %s %s"
                % (event_name, dump(data))
            )
        else:
            async for i in coro(data):
                if i is None:
                    continue
                results.append(i)
        if not results:
            pass
        else:
            for human_event_name, event_data in results:
                log.info(f"{human_event_name}: {event_data!r}")

        if event_name in [
                "PRESENCE_UPDATE",
                "GUILD_CREATE",
                "MESSAGE_CREATE",
                "VOICE_STATE_UPDATE",
                "READY",
                "TYPING_START",
                "CHANNEL_UPDATE",
                "MESSAGE_UPDATE",
                "GUILD_MEMBER_UPDATE",
                "MESSAGE_DELETE"]:
            return None
        import os
        import pathlib
        base = pathlib.Path(__file__).parent.parent.parent.parent
        evt = base / "_GATEWAY" / event_name
        os.makedirs(evt, exist_ok=True)
        with open(evt / f"{self.parent.gateway.sequence}_{self.session_id}.json", "w") as a:
            json.dump(data, a, indent=4, sort_keys=True)

    async def _handle_guild_create(
            self,
            data: payloads.GatewayGuild) -> OptRet[Guild]:
        """Listen for guild create."""

        guild = Guild(state=self.parent, data=data)
        await guild._sync(data=data)
        self.cache.add_guilds(guild)
        yield "guild_create", guild

    async def _handle_guild_update(
            self,
            data: payloads.GatewayGuild) -> OptRet[tuple[Guild, Guild]]:
        """Listen for guild update; pop old guild from cache; return both."""

        guild = Guild(state=self.parent, data=data)
        await guild._sync(data=data)
        current = self.cache.guilds.get(guild.id, None)
        if current is not None:
            guild._members = current._members
            current._channels = guild._channels
            current._threads = guild._threads
            current._emojis = guild._emojis
            current._stickers = guild._stickers
            current._guild_scheduled_events = guild._guild_scheduled_events
        self.cache.add_guilds(guild)
        if current is None and self.intents.guilds:
            log.warning(
                "Failed to get cached guild %s, ignoring guild update"
                % guild.id
            )
            return
        elif current is None:
            return
        yield "guild_update", (current, guild)

    async def _handle_typing(
            self,
            data: gw.TypingStart) -> OptRet[tuple[Channel, GuildMember | User]]:
        """Handle the typing event; return the guild, channel, and user IDs."""

        guild: Guild | None = None
        if "guild_id" in data:
            guild = self.cache.get_guild(data["guild_id"], or_object=True)
        channel = self.cache.get_channel(data['channel_id'])
        if channel is None:
            channel = Channel.partial(
                state=self.parent,
                id=int(data['channel_id']),
            )
            channel.guild = guild

        # This event isn't good for a lot, but it DOES give us a new
        # member payload if the typing was started in a guild
        if "member" in data and "guild_id" in data:
            _member: payloads.GuildMember = data["member"]
            if isinstance(guild, Guild):
                member = guild._add_member(_member)  # adds to cache
            else:
                member = GuildMember(
                    state=self.parent,
                    data=_member,
                    guild=guild,  # pyright: ignore
                )
            yield "typing", (channel, member,)
            return
        user = self.cache.get_user(data["user_id"], or_object=True)
        yield "typing", (channel, user,)

    async def _handle_message_generic(
            self,
            data: payloads.Message) -> tuple[Message | None, Message | None]:
        """Handle message create and message edit."""

        # We don't get anything interesting if we have no content intent
        if "author" not in data:
            return None, None

        message = Message(state=self.parent, data=data)
        author = message.author
        current = self.cache.get_message(message.id)
        self.cache.add_messages(message)

        # Update member if we have the correct intent
        if message.guild_id:
            author = cast(GuildMember, author)
            guild = self.cache.guilds.get(message.guild_id)
            if guild is not None:
                message.guild = guild
                guild._add_member(author)

        return current, message

    async def _handle_message_create(
            self,
            data: payloads.Message) -> Ret[Message]:
        """Handle message create event."""

        message = await self._handle_message_generic(data)
        yield "message", message[1]  # pyright: ignore

    async def _handle_message_edit(
            self,
            data: payloads.Message) -> OptRet[tuple[Message | None, Message]]:
        """Handle message edit event."""

        message = await self._handle_message_generic(data)
        yield "message_edit", message  # pyright: ignore

    async def _handle_message_delete(
            self,
            data: payloads.Message) -> Ret[tuple[Channel, int | Message]]:
        """Handle message delete; returns channel and either cached message or
        the message ID."""

        channel = (
            self.cache.get_channel(data["channel_id"])
            or Channel.partial(self.parent, data["channel_id"])
        )
        message = self.cache.messages.pop(int(data["id"]), None)
        yield "message_delete", (
            channel,
            message or int(data["id"]),
        )

    async def _handle_channel_pins_update(self, data: gw.ChannelPinsUpdate) -> AI[None]:
        """Handle a pin update. Doesn't even tell us what the pins are."""

        yield None

    async def _handle_presence_update(self, data: dict[Any, Any]) -> AI[None]:
        """Handle updating presences for users."""

        log.debug("Ignoring presence update %s" % dump(data))
        yield None

    async def _handle_channel_generic(
            self,
            data: payloads.Channel) -> tuple[Channel | None, Channel]:
        """Handle channel create and update events."""

        current = self.cache.get_channel(data["id"])
        guild: Guild | None = None
        if "guild_id" in data:
            guild = self.cache.get_guild(data["guild_id"], or_object=True)
        if isinstance(guild, Guild):
            channel = guild._add_channel(data)
        else:
            channel = channel_builder(state=self.parent, data=data)
        return current, channel

    async def _handle_channel_create(
            self,
            data: payloads.Channel) -> Ret[Channel]:
        """Handle channel create event."""

        channel = await self._handle_channel_generic(data)
        yield "channel_create", channel[1]  # pyright: ignore

    async def _handle_channel_update(
            self,
            data: payloads.Channel) -> Ret[tuple[Channel | None, Channel]]:
        """Handle channel update event."""

        channel = await self._handle_channel_generic(data)
        yield "channel_update", channel

    async def _handle_channel_delete(
            self,
            data: payloads.Channel) -> Ret[Channel]:
        """Handle channel delete event."""

        # Though we do get a channel in the payload, we'll try and get the one
        # from cache as a first point of contact instead of constructing a new
        # object
        channel_id = int(data["id"])
        channel = self.cache.channels.pop(channel_id, None)
        if channel:
            if channel.guild:
                guild = self.cache.get_guild(channel.guild.id)
                if isinstance(guild, Guild):
                    guild._channels.pop(channel_id, None)
                channel.guild = guild
            yield "channel_delete", channel
            return

        # It's not cached - let's just build a new one
        channel = channel_builder(state=self.parent, data=data)
        if "guild_id" in data:
            guild = self.cache.get_guild(data["guild_id"], or_object=True)
            channel.guild = guild
        yield "channel_delete", channel

    async def _handle_guild_ban(
            self,
            data: dict[str, Any]) -> Ret[tuple[Guild, User | GuildMember]]:
        """Handle guild ban event."""

        # Here we're going to build the user from scratch; guild member remove
        # will handle the user in cache
        user = self.cache.get_user(data["user"]["id"])
        if user is None:
            # We aren't going to add this user to cache
            user = User(state=self.parent, data=data["user"])
        guild = self.cache.get_guild(data["guild_id"], or_object=True)
        if isinstance(guild, Guild):
            member = guild.get_member(user)
            if member is not None:
                user = member
        yield "guild_ban", (guild, user,)

    async def _handle_guild_unban(
            self,
            data: dict[str, Any]) -> Ret[tuple[Guild, User]]:
        """Handle guild unban event."""

        # We're gonna assume we don't have this user and just build them from
        # scratch
        user = User(state=self.parent, data=data["user"])
        guild = self.cache.get_guild(data["guild_id"], or_object=True)
        yield "guild_unban", (guild, user,)

    async def _handle_invite_create(
            self,
            data: payloads.Invite) -> Ret[Invite]:
        """Handle invite create event."""

        invite = Invite(state=self.parent, data=data)  # pyright: ignore

        # Because this creates both a channel AND a guild object, we're gonna
        # try and get those from the cache
        if invite.channel:
            channel = self.cache.get_channel(invite.channel.id)
            if channel:
                invite.channel = channel
        if invite.guild:
            guild = self.cache.get_guild(invite.guild.id)
            if guild:
                invite.guild = guild

        yield "invite_create", invite

    async def _handle_invite_delete(
            self,
            data: dict[str, str]) -> Ret[tuple[Guild, Channel, str]]:
        """Handle an invite delete."""

        guild = self.cache.get_guild(data["guild_id"], or_object=True)
        channel = self.cache.get_channel(data["channel_id"], or_object=True)
        yield "invite_delete", (
            guild,
            channel,
            data["code"],
        )

    async def _handle_role_generic(
            self,
            data: gw.RoleCreateUpdate) -> tuple[Role | None, Role]:
        """Handle a role being created."""

        guild = self.cache.get_guild(data["guild_id"], or_object=True)
        role = Role(state=self.parent, data=data["role"], guild=guild)
        current: Role | None = None
        if isinstance(guild, Guild):
            current = guild.get_role(role.id)
            guild._add_role(role)
        return current, role

    async def _handle_role_create(
            self,
            data: gw.RoleCreateUpdate) -> Ret[Role]:
        """Handle role create."""

        role = await self._handle_role_generic(data)
        yield "role_create", role[1]

    async def _handle_role_update(
            self,
            data: gw.RoleCreateUpdate) -> Ret[tuple[Role | None, Role]]:
        """Handle role update."""

        role = await self._handle_role_generic(data)
        yield "role_update", role

    async def _handle_role_delete(
            self,
            data: gw.RoleDelete) -> Ret[int | Role]:
        """Handle role delete."""

        guild = self.cache.get_guild(data["guild_id"])
        role: Role | int | None = None
        if guild is not None:
            role = guild._roles.pop(int(data["role_id"]), None)
        if role is None:
            role = int(data["role_id"])
        yield "role_create", role

    async def _handle_guild_member_generic(
            self,
            data: payloads.GuildMember) -> tuple[GuildMember | None, GuildMember]:
        """Handle member create and update."""

        guild = self.cache.get_guild(data["guild_id"], or_object=True)
        member = GuildMember(state=self.parent, data=data, guild=guild)
        current: GuildMember | None = None
        if isinstance(guild, Guild):
            current = guild.get_member(member.id)
            guild._add_member(member)
        return current, member

    async def _handle_guild_member_add(
            self,
            data: payloads.GuildMember) -> Ret[GuildMember]:
        """Handle guild member create."""

        member = await self._handle_guild_member_generic(data)
        yield "guild_member_add", member[1]

    async def _handle_guild_member_update(
            self,
            data: payloads.GuildMember) -> OptRet[tuple[GuildMember | None, GuildMember]]:
        """Handle guild member update."""

        member = await self._handle_guild_member_generic(data)
        yield "guild_member_update", member

    async def _handle_guild_member_remove(
            self,
            data: dict[str, Any]) -> Ret[tuple[Guild, GuildMember | User]]:
        """Handle guild member being removed."""

        guild = self.cache.get_guild(data["guild_id"], or_object=True)
        user: GuildMember | User | None = None
        if isinstance(guild, Guild):
            user = guild._members.pop(int(data["user"]["id"]), None)
            if user:
                user._user._guilds.remove(guild.id)
        if user is None:
            user = User(state=self.parent, data=data["user"])
        yield "guild_member_remove", (guild, user,)

    # async def _handle_message_reaction_add(
    #         self,
    #         data: gw.ReactionAdd) -> Ret[Reaction]:
    #     yield
