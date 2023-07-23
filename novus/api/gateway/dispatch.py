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
import json
import logging
from typing import TYPE_CHECKING, Any, AsyncIterator, Callable, TypeAlias, TypeVar

from novus.models.guild_member import ThreadMember

from ...models import (
    AuditLogEntry,
    BaseGuild,
    Channel,
    Emoji,
    Guild,
    GuildMember,
    Interaction,
    Invite,
    Message,
    Object,
    Reaction,
    Role,
    Sticker,
    Thread,
    User,
    VoiceState,
)
from ...models.channel import channel_builder
from ...utils import try_snowflake

if TYPE_CHECKING:
    from ... import payloads
    from ...flags import Intents
    from ...models import abc
    from ...payloads import gateway as gw
    from .._http import HTTPConnection
    from .gateway import GatewayShard


__all__ = (
    'GatewayDispatch',
)


log = logging.getLogger("novus.gateway.dispatch")
dump = json.dumps


ReturnType = TypeVar("ReturnType")
AI = AsyncIterator
Ret: TypeAlias = AI[ReturnType]
OptRet: TypeAlias = AI[ReturnType | None]


class Event:

    def __init__(self, name: str, data: Any):
        self.name = name
        self.data = data


class GatewayDispatch:

    def __init__(self, shard: GatewayShard) -> None:
        self.shard: GatewayShard = shard
        self.parent: HTTPConnection = self.shard.parent
        self.EVENT_HANDLER: dict[
            str,
            Callable[
                [Any],  # dict, but we know about it
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
            "THREAD_CREATE": self._handle_thread_create,
            "THREAD_UPDATE": self._handle_thread_update,
            # "Thread delete": None,
            # "Thread list sync": None,
            # "Thread member update": None,
            "THREAD_MEMBERS_UPDATE": self._handle_thread_member_list_update,
            "GUILD_CREATE": self._handle_guild_create,
            "GUILD_UPDATE": self._handle_guild_update,
            "GUILD_DELETE": self._handle_guild_delete,
            "GUILD_AUDIT_LOG_ENTRY_CREATE": self._handle_audit_log_entry,
            "GUILD_BAN_ADD": self._handle_guild_ban,
            "GUILD_BAN_REMOVE": self._handle_guild_unban,
            "GUILD_EMOJIS_UPDATE": self._handle_guild_emojis_update,
            "GUILD_STICKERS_UPDATE": self._handle_guild_stickers_update,
            "GUILD_INTEGRATIONS_UPDATE": self.ignore("GUILD_INTEGRATIONS_UPDATE"),
            "GUILD_MEMBER_ADD": self._handle_guild_member_add,
            "GUILD_MEMBER_REMOVE": self._handle_guild_member_remove,
            "GUILD_MEMBER_UPDATE": self._handle_guild_member_update,
            "GUILD_MEMBERS_CHUNK": self._handle_guild_member_chunk,
            "GUILD_ROLE_CREATE": self._handle_role_create,
            "GUILD_ROLE_UPDATE": self._handle_role_update,
            "GUILD_ROLE_DELETE": self._handle_role_delete,
            # "Guild scheduled event create": None,
            # "Guild scheduled event update": None,
            # "Guild scheduled event delete": None,
            # "Guild scheduled event user add": None,
            # "Guild scheduled event user remove": None,
            "INTEGRATION_CREATE": self.ignore("INTEGRATION_CREATE"),
            "INTEGRATION_UPDATE": self.ignore("INTEGRATION_UPDATE"),
            "INTEGRATION_DELETE": self.ignore("INTEGRATION_DELETE"),
            "INTERACTION_CREATE": self._handle_interaction,
            "INVITE_CREATE": self._handle_invite_create,
            "INVITE_DELETE": self._handle_invite_delete,
            "MESSAGE_CREATE": self._handle_message_create,
            "MESSAGE_UPDATE": self._handle_message_edit,
            "MESSAGE_DELETE": self._handle_message_delete,
            # "Message delete bulk": None,
            "MESSAGE_REACTION_ADD": self._handle_message_reaction_add,
            "MESSAGE_REACTION_REMOVE": self._handle_message_reaction_remove,
            "MESSAGE_REACTION_REMOVE_ALL": self._handle_message_reaction_remove_all,
            "MESSAGE_REACTION_REMOVE_EMOJI": self._handle_message_reaction_remove_all_emoji,
            "PRESENCE_UPDATE": self._handle_presence_update,
            # "Stage instance create": None,
            # "Stage instance update": None,
            # "Stage instance delete": None,
            "TYPING_START": self._handle_typing,
            # "User update": None,
            "VOICE_STATE_UPDATE": self._handle_voice_state,
            # "Voice server update": None,
            # "Webhooks update": None,
        }

    @property
    def cache(self):
        return self.parent.cache

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
            self.shard.resume_url = data['resume_gateway_url']
            self.shard.session_id = data['session_id']
            self.shard.ready.set()
            log.info("Received ready (shard %s)", self.shard.shard_id)
            return None
        elif event_name == "RESUMED":
            self.shard.ready.set()
            log.info("Received resumed (shard %s)", self.shard.shard_id)
            return None

        if self.parent.gateway.guild_ids_only:
            if event_name == "GUILD_CREATE":
                coro = self._handle_guild_create_id_only
            else:
                return
        coro = self.EVENT_HANDLER.get(event_name)
        if coro is None:
            log.warning(
                "Failed to parse event %s %s"
                % (event_name, dump(data))
            )
        else:
            async for i in coro(data):
                if i is None:
                    self.parent.dispatch(event_name)
                elif isinstance(i, tuple):
                    self.parent.dispatch(event_name, *i)
                else:
                    self.parent.dispatch(event_name, i)

        # if event_name in [
        #         "PRESENCE_UPDATE",
        #         "GUILD_CREATE",
        #         "MESSAGE_CREATE",
        #         "VOICE_STATE_UPDATE",
        #         "READY",
        #         "TYPING_START",
        #         "CHANNEL_UPDATE",
        #         "MESSAGE_UPDATE",
        #         "GUILD_MEMBER_UPDATE",
        #         "MESSAGE_DELETE"]:
        #     return None
        # import os
        # import pathlib
        # base = pathlib.Path(__file__).parent.parent.parent.parent
        # evt = base / "_GATEWAY" / event_name
        # os.makedirs(evt, exist_ok=True)
        # with open(evt / f"{self.parent.gateway.sequence}_{self.session_id}.json", "w") as a:
        #     json.dump(data, a, indent=4, sort_keys=True)

    @staticmethod
    def ignore(event_name: str):
        async def wrapper(data: Any):
            yield event_name, data
        return wrapper

    async def _handle_interaction(
            self,
            data: payloads.Interaction) -> Ret[Interaction]:
        """Handle interaction create."""

        yield Interaction(state=self.parent, data=data)

    async def _handle_guild_create(
            self,
            data: payloads.GatewayGuild) -> OptRet[Guild]:
        """Listen for guild create."""

        guild = Guild(state=self.parent, data=data)
        self.cache.add_guilds(guild)
        await guild._sync(data=data)
        yield guild

    async def _handle_guild_create_id_only(
            self,
            data: payloads.GatewayGuild) -> OptRet[BaseGuild]:
        """Listen for guild create."""

        # The only reason this returns a baseguild is so that you still have
        # an object you can perform API methods on.

        self.cache.guild_ids.add(int(data["id"]))
        yield BaseGuild(state=self.parent, data={"id": data["id"]})  # pyright: ignore

    async def _handle_guild_update(
            self,
            data: payloads.GatewayGuild) -> OptRet[tuple[Guild | None, Guild]]:
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
        yield current, guild

    async def _handle_guild_delete(self, data: dict[str, str]) -> Ret[Guild | int]:
        """Handle being removed from a guild."""

        # Get from cache if we can
        try:
            self.cache.guild_ids.remove(int(data["id"]))
        except KeyError:
            pass
        current = self.cache.guilds.pop(int(data["id"]), None)
        if not current:
            yield int(data["id"])
            return

        def try_delete(dict: dict, key: int) -> None:
            try:
                del dict[key]
            except KeyError:
                pass

        # Remove all cached stuff that we can
        for id in list(current._emojis.keys()):
            try_delete(self.cache.emojis, id)
            del current._emojis[id]
        for id in list(current._stickers.keys()):
            try_delete(self.cache.stickers, id)
            del current._stickers[id]
        for id in list(current._roles.keys()):
            del current._roles[id]
        for id, member in list(current._members.items()):
            try:
                member._user._guilds.remove(current.id)
            except KeyError:
                pass
            if not member._user._guilds:
                try_delete(self.cache.users, id)
            del current._members[id]
        for id in list(current._guild_scheduled_events.keys()):
            try_delete(self.cache.events, id)
            del current._guild_scheduled_events[id]
        for id in list(current._threads.keys()):
            try_delete(self.cache.channels, id)
            del current._threads[id]
        for id in list(current._voice_states.keys()):
            pass
        for id in list(current._channels.keys()):
            try_delete(self.cache.channels, id)
            del current._channels[id]

        yield current

    async def _handle_guild_emojis_update(
            self,
            data: gw.GuildEmojisUpdate) -> Ret[tuple[BaseGuild | Guild, list[Emoji]]]:
        """Handle guild emojis update. For whatever reason Discord gives us
        the entire guild emoji list for every update."""

        guild = self.cache.get_guild(data["guild_id"])
        if isinstance(guild, Guild):
            for k in guild._emojis.keys():
                try:
                    self.cache.emojis.pop(k)
                except KeyError:
                    pass
        emojis = [
            Emoji(state=self.parent, data=d)
            for d in data["emojis"]
        ]
        if isinstance(guild, Guild):
            guild._emojis.clear()
            for e in emojis:
                guild._add_emoji(e)
        yield guild, emojis,

    async def _handle_guild_stickers_update(
            self,
            data: gw.GuildStickersUpdate) -> Ret[tuple[BaseGuild | Guild, list[Sticker]]]:
        """Handle guild stickers update. For whatever reason Discord gives us
        the entire guild stickers list for every update."""

        guild = self.cache.get_guild(data["guild_id"])
        if isinstance(guild, Guild):
            for k in guild._stickers.keys():
                try:
                    self.cache.stickers.pop(k)  # remove stickers from our cache
                except KeyError:
                    pass
        stickers = [
            Sticker(state=self.parent, data=d)
            for d in data["stickers"]
        ]
        if isinstance(guild, Guild):
            guild._stickers.clear()  # remove stickers from guild cache
            for e in stickers:
                guild._add_sticker(e)  # add stickers to guild and our cache
        yield guild, stickers

    async def _handle_typing(
            self,
            data: gw.TypingStart) -> OptRet[tuple[Channel, GuildMember | User]]:
        """Handle the typing event; return the guild, channel, and user IDs."""

        # This will only dispatch an event if the typing is triggered inside of
        # a guild. Just for my own ease.

        guild: BaseGuild | None = None
        if "guild_id" in data:
            guild = self.cache.get_guild(data["guild_id"])
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
                )
            yield channel, member,
            return

        # Unfortunately it tells us nothing about a user (ie a non-guild
        # member) so we just have to build something that acts like it if they
        # don't exist in cache.
        user = self.cache.get_user(data["user_id"])
        if user is None:
            return
        yield channel, user,

    async def _handle_message_generic(
            self,
            data: payloads.Message) -> tuple[Message | None, Message] | None:
        """Handle message create and message edit."""

        # If there's no author, it's a webhook message being edited
        if "author" not in data:
            return None

        # Create our initial message
        message = Message(state=self.parent, data=data)
        current = self.cache.get_message(message.id)
        self.cache.add_messages(message)

        # Update channel with cached
        channel = self.cache.get_channel(message.channel.id)
        if channel is not None:
            message.channel = channel  # pyright: ignore

        # Update guild with cached
        if message.guild is not None:
            guild = self.cache.get_guild(message.guild.id)
            message.guild = guild

            # Update author with member
            constructed: bool = False
            cached_member: GuildMember | User | None = None
            if isinstance(guild, Guild):
                cached_member = guild.get_member(message.author.id)
            if cached_member is None and "member" in data:
                constructed = True
                cached_member = GuildMember(
                    state=self.parent,
                    data=data["member"],
                    user=data["author"],
                    guild_id=message.guild.id,
                )
            elif cached_member is None:
                cached_member = message.author
            if isinstance(guild, Guild) and constructed:
                assert isinstance(cached_member, GuildMember)
                guild._add_member(cached_member)
            message.author = cached_member

        return current, message

    async def _handle_message_create(
            self,
            data: payloads.Message) -> Ret[Message]:
        """Handle message create event."""

        message = await self._handle_message_generic(data)
        if message is None:
            return
        yield message[1]

    async def _handle_message_edit(
            self,
            data: payloads.Message) -> OptRet[tuple[Message | None, Message]]:
        """Handle message edit event."""

        message = await self._handle_message_generic(data)
        if message is None:
            return
        yield message[0], message[1]

    async def _handle_message_delete(
            self,
            data: payloads.Message) -> Ret[tuple[Channel, Message | Object]]:
        """Handle message delete; returns channel and either cached message or
        the message ID."""

        # Get cached message
        message = self.cache.messages.pop(int(data["id"]), None)

        # Get channel - either from our own cache or from the cached message
        channel = self.cache.get_channel(data["channel_id"])
        if channel is None and message:
            channel = message.channel
        if channel is None:
            return  # No cached channel to make use of

        # No message but we do have a channel? Just use an object
        if message is None:
            message = Object(data["id"], state=self.parent)
        yield channel, message,

    async def _handle_channel_pins_update(
            self,
            data: gw.ChannelPinsUpdate) -> AI[None]:
        """Handle a pin update. Doesn't even tell us what the pins are."""

        yield None

    async def _handle_presence_update(
            self,
            data: dict[Any, Any]) -> AI[None]:
        """Handle updating presences for users."""

        log.debug("Ignoring presence update %s" % dump(data))#
        # TODO
        yield None

    async def _handle_channel_generic(
            self,
            data: payloads.Channel) -> tuple[Channel | None, Channel]:
        """Handle channel create and update events."""

        current = self.cache.get_channel(data["id"])
        guild: BaseGuild | None = None
        guild_id: int | None = None
        if "guild_id" in data:
            guild = self.cache.get_guild(data["guild_id"])
            guild_id = guild.id
        if isinstance(guild, Guild):
            channel = guild._add_channel(data)
            channel.guild = guild
        else:
            channel = channel_builder(state=self.parent, data=data, guild_id=guild_id)
        return current, channel

    async def _handle_channel_create(
            self,
            data: payloads.Channel) -> Ret[Channel]:
        """Handle channel create event."""

        channel = await self._handle_channel_generic(data)
        yield channel[1]

    async def _handle_channel_update(
            self,
            data: payloads.Channel) -> Ret[tuple[Channel | None, Channel]]:
        """Handle channel update event."""

        channel = await self._handle_channel_generic(data)
        yield channel

    async def _handle_channel_delete(
            self,
            data: payloads.Channel) -> Ret[Channel]:
        """Handle channel delete event."""

        # Though we do get a channel in the payload, we'll try and get the one
        # from cache as a first point of contact instead of constructing a new
        # object. Although it may be slower, we'll need to do it anyway in order
        # to remove it from the cache.
        channel_id = int(data["id"])
        channel = self.cache.channels.pop(channel_id, None)
        if channel:
            if channel.guild:
                guild = self.cache.get_guild(channel.guild.id)
                if isinstance(guild, Guild):
                    guild._channels.pop(channel_id, None)
                channel.guild = guild
            yield channel
            return

        # It's not cached - let's just build a new one
        channel = channel_builder(state=self.parent, data=data)
        if "guild_id" in data:
            guild = self.cache.get_guild(data["guild_id"])
            channel.guild = guild
        yield channel

    async def _handle_guild_ban(
            self,
            data: dict[str, Any]) -> Ret[tuple[Guild, User | GuildMember]]:
        """Handle guild ban event."""

        user: User | GuildMember | None = self.cache.get_user(data["user"]["id"])
        if user is None:
            user = User(state=self.parent, data=data["user"])
        guild = self.cache.get_guild(data["guild_id"])
        try:
            user._guilds.remove(guild.id)
        except KeyError:
            pass
        if isinstance(guild, Guild):
            member = guild.get_member(user)
            if member is not None:
                user = member
        yield guild, user,

    async def _handle_guild_unban(
            self,
            data: dict[str, Any]) -> Ret[tuple[Guild, User]]:
        """Handle guild unban event."""

        # We're gonna assume we don't have this user and just build them from
        # scratch.
        # We won't cache them from this, but if they're already cached, we'll
        # use this new payload to update them.
        user = self.cache.get_user(data["user"]["id"])
        if user is None:
            user = User(state=self.parent, data=data["user"])
        else:
            user._sync(data["user"])
        guild = self.cache.get_guild(data["guild_id"])
        yield guild, user,

    async def _handle_invite_create(
            self,
            data: payloads.Invite) -> Ret[Invite]:
        """Handle invite create event."""

        # The invite object pulls both the guild and the channel objects from
        # cache in its constructor -
        # the guild is actually a more full object than one found in BaseGuild,
        # so we're just going to leave it as is and let it do what it wants.

        yield Invite(state=self.parent, data=data)

    async def _handle_invite_delete(
            self,
            data: dict[str, str]) -> Ret[tuple[BaseGuild, Channel | None, str]]:
        """Handle an invite delete."""

        guild = self.cache.get_guild(data["guild_id"])
        channel = self.cache.get_channel(data["channel_id"])
        yield guild, channel, data["code"],

    async def _handle_role_generic(
            self,
            data: gw.RoleCreateUpdate) -> tuple[Role | None, Role]:
        """Handle a role being created."""

        guild = self.cache.get_guild(data["guild_id"])
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
        yield role[1]

    async def _handle_role_update(
            self,
            data: gw.RoleCreateUpdate) -> Ret[tuple[Role | None, Role]]:
        """Handle role update."""

        role = await self._handle_role_generic(data)
        yield role

    async def _handle_role_delete(
            self,
            data: gw.RoleDelete) -> Ret[Role | abc.StateSnowflakeWithGuild]:
        """Handle role delete."""

        guild = self.cache.get_guild(data["guild_id"])
        role: Role | Object | None = None
        if isinstance(guild, Guild):
            role = guild._roles.pop(int(data["role_id"]), None)
        if role is None:
            role = Object(data["role_id"], state=self.parent, guild=guild)
        yield role  # pyright: ignore

    async def _handle_guild_member_generic(
            self,
            data: payloads.GuildMember) -> tuple[GuildMember | None, GuildMember]:
        """Handle member create and update."""

        guild = self.cache.get_guild(data["guild_id"])
        member = GuildMember(state=self.parent, data=data)
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
        yield member[1]

    async def _handle_guild_member_update(
            self,
            data: payloads.GuildMember) -> OptRet[tuple[GuildMember | None, GuildMember]]:
        """Handle guild member update."""

        member = await self._handle_guild_member_generic(data)
        yield member

    async def _handle_guild_member_remove(
            self,
            data: payloads.GuildMemberRemove) -> Ret[tuple[BaseGuild, GuildMember | User]]:
        """Handle guild member being removed."""

        guild = self.cache.get_guild(data["guild_id"])
        member: GuildMember | User | None = None
        if isinstance(guild, Guild):
            member = guild._members.pop(int(data["user"]["id"]), None)
            if member:
                try:
                    member._user._guilds.remove(guild.id)
                except KeyError:
                    pass
                if not member._user._guilds:
                    self.cache.users.pop(member.id, None)
        if member is None:
            member = self.cache.get_user(data["user"]["id"])
            if member is None:
                member = User(state=self.parent, data=data["user"])  # don't cache
            else:
                member._sync(data["user"])
        yield guild, member,

    async def _handle_guild_member_chunk(self, data: gw.GuildMemberChunk) -> Ret[None]:
        """Handle response from chunk request."""

        guild = self.cache.get_guild(data["guild_id"])
        if not isinstance(guild, Guild):
            return
        nonce = None
        if "nonce" in data:
            nonce = data["nonce"]
        for m in data["members"]:
            created = guild._add_member(m)
            if nonce:
                self.shard.chunk_groups[nonce].append(created)
            await asyncio.sleep(0)
        if nonce:
            self.shard.chunk_counter[nonce] += 1
            if self.shard.chunk_counter[nonce] == data["chunk_count"]:
                del self.shard.chunk_counter[nonce]
                self.shard.chunk_event[nonce].set()
        yield None

    async def _handle_message_reaction_generic(
            self,
            data: gw.ReactionAddRemove) -> tuple[GuildMember | User | Object, Reaction]:
        """Handle reaction add or remove."""

        # Get message from cache
        message = self.cache.get_message(data["message_id"])

        # Create a new reaction object using that cached message (which may not
        # exist)
        created = Reaction(state=self.parent, data=data, message=message)  # pyright: ignore

        # Get the guild from cache if one exists
        guild: BaseGuild | Guild | None = None
        if "guild_id" in data:
            guild = self.cache.get_guild(data["guild_id"])

        # Update our cache with the created member object
        user: User | GuildMember | Object | None = None
        if "member" in data:
            assert isinstance(guild, Guild)
            user = guild._add_member(data["member"])

        # Probably didn't happen in a guild. That sucks
        if user is None:
            user = self.cache.get_user(data["user_id"])
            if user is None:
                user = Object(data["user_id"], state=self.parent)

        return user, created

    async def _handle_message_reaction_add(
            self,
            data: gw.ReactionAddRemove) -> Ret[tuple[GuildMember | User | Object, Reaction]]:
        """Handle reaction add."""

        created = await self._handle_message_reaction_generic(data)
        yield created[0], created[1],

    async def _handle_message_reaction_remove(
            self,
            data: gw.ReactionAddRemove) -> Ret[tuple[GuildMember | User | Object, Reaction]]:
        """Handle reaction remove."""

        created = await self._handle_message_reaction_generic(data)
        yield created[0], created[1],

    async def _handle_message_reaction_remove_all(
            self,
            data: gw.ReactionAddRemove) -> Ret[Message | Object]:
        """Handle reaction remove all."""

        message = self.cache.get_message(data["message_id"])
        if message is None:
            yield Object(data["message_id"], state=self.parent)
            return
        yield message

    async def _handle_message_reaction_remove_all_emoji(
            self,
            data: gw.ReactionAddRemove) -> Ret[Reaction]:
        """Handle reaction remove all for emoji."""

        created = await self._handle_message_reaction_generic(data)
        yield created[1]

    async def _handle_thread_create(
            self,
            data: payloads.Channel) -> Ret[Thread]:
        """Handle thread creation."""

        assert "guild_id" in data  # You can only have threads in guilds
        guild = self.cache.get_guild(data["guild_id"])
        created = channel_builder(state=self.parent, data=data, guild_id=guild.id)
        assert isinstance(created, Thread)
        if isinstance(guild, Guild):
            guild._add_thread(created)  # pyright: ignore
        yield created

    async def _handle_thread_update(
            self,
            data: payloads.Channel) -> Ret[tuple[Thread | None, Thread]]:
        """Handle thread update."""

        assert "guild_id" in data  # You can only have threads in guilds
        guild = self.cache.get_guild(data["guild_id"])
        created = channel_builder(state=self.parent, data=data, guild_id=guild.id)
        assert isinstance(created, Thread)
        current = None
        if isinstance(guild, Guild):
            current = guild._threads.get(created.id)
            guild._add_thread(created)  # pyright: ignore
        yield current, created

    async def _handle_thread_member_list_update(
            self,
            data: gw.ThreadMemberListUpdate) -> Ret[Thread | Channel]:
        """Handle a thread's member list being updated."""

        thread = self.cache.get_channel(data["id"])
        if thread is None:
            return
        if isinstance(thread, Thread):
            for member_payload in data.get("added_members", []):
                assert "member" in member_payload
                member = ThreadMember(
                    state=self.parent,
                    data=member_payload,
                    guild_id=data["guild_id"],
                )
                thread._add_member(member)
            for member_id in data.get("removed_member_ids", []):
                thread._remove_member(member_id)
            thread.member_count = data["member_count"]
        yield thread

    async def _handle_voice_state(
            self,
            data: payloads.VoiceState) -> Ret[tuple[VoiceState | None, VoiceState | None]]:
        """Handle voice state update."""

        if "guild_id" not in data:
            return
        created = VoiceState(state=self.parent, data=data)
        guild = self.cache.get_guild(data["guild_id"])
        user_id = int(data["user_id"])
        if guild is None or not isinstance(guild, Guild):
            yield None, created
            return
        current = guild._voice_states.get(user_id)
        if created.channel:
            guild._add_voice_state(created)
            yield current, created
        else:
            guild._voice_states.pop(user_id, None)
            yield current, None

    async def _handle_audit_log_entry(
            self,
            data: payloads.AuditLogEntry) -> Ret[AuditLogEntry]:
        """Handle audit log entry events."""

        yield AuditLogEntry(data=data, log=None)
