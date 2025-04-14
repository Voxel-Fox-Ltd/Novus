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
from copy import copy
from typing import TYPE_CHECKING, Any, Awaitable, Callable, cast

from ...models import (  # Emoji,; Object,; Sticker,; ThreadMember,
    AuditLogEntry,
    BaseGuild,
    Channel,
    Guild,
    GuildMember,
    Interaction,
    Invite,
    Message,
    Reaction,
    Role,
    User,
    VoiceState,
)
from ...utils import try_id, try_snowflake

if TYPE_CHECKING:
    from ... import payloads
    from ...flags import Intents
    from ...payloads import gateway as gw
    from .._http import APICache, HTTPConnection
    from .gateway import GatewayShard


__all__ = (
    'GatewayDispatch',
)


log = logging.getLogger("novus.gateway.dispatch")
dump = json.dumps


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
                Awaitable[None],
            ]
        ]
        self.EVENT_HANDLER = {
            "APPLICATION_COMMAND_PERMISSIONS_UPDATE": self.ignore("APPLICATION_COMMAND_PERMISSIONS_UPDATE"),
            # "Auto moderation rule create": None,
            # "Auto moderation rule update": None,
            # "Auto moderation rule delete": None,
            # "Auto moderation action execution": None,
            "CHANNEL_CREATE": self._handle_channel_create,
            "CHANNEL_UPDATE": self._handle_channel_update,
            "CHANNEL_DELETE": self._handle_channel_delete,
            # "CHANNEL_PINS_UPDATE": self._handle_channel_pins_update,
            # "THREAD_CREATE": self._handle_thread_create,
            # "THREAD_UPDATE": self._handle_thread_update,
            # "Thread delete": None,
            # "Thread list sync": None,
            # "Thread member update": None,
            # "THREAD_MEMBERS_UPDATE": self._handle_thread_member_list_update,
            "GUILD_CREATE": self._handle_guild_create,
            "GUILD_UPDATE": self._handle_guild_update,
            "GUILD_DELETE": self._handle_guild_delete,
            "GUILD_AUDIT_LOG_ENTRY_CREATE": self._handle_audit_log_entry,
            "GUILD_BAN_ADD": self._handle_guild_ban,
            "GUILD_BAN_REMOVE": self._handle_guild_unban,
            "GUILD_EMOJIS_UPDATE": self._handle_guild_emojis_update,
            "GUILD_STICKERS_UPDATE": self._handle_guild_stickers_update,
            "GUILD_INTEGRATIONS_UPDATE": self.ignore("GUILD_INTEGRATIONS_UPDATE"),
            "GUILD_JOIN_REQUEST_UPDATE": self.ignore("GUILD_JOIN_REQUEST_UPDATE"),
            "GUILD_JOIN_REQUEST_DELETE": self.ignore("GUILD_JOIN_REQUEST_DELETE"),
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
            # "INTEGRATION_CREATE": self.ignore("INTEGRATION_CREATE"),
            # "INTEGRATION_UPDATE": self.ignore("INTEGRATION_UPDATE"),
            # "INTEGRATION_DELETE": self.ignore("INTEGRATION_DELETE"),
            "INTERACTION_CREATE": self._handle_interaction,
            "INVITE_CREATE": self._handle_invite_create,
            "INVITE_DELETE": self._handle_invite_delete,
            "MESSAGE_CREATE": self._handle_message_create,
            "MESSAGE_UPDATE": self._handle_message_edit,
            "MESSAGE_DELETE": self._handle_message_delete,
            # "Message delete bulk": None,
            "MESSAGE_REACTION_ADD": self._handle_message_reaction_add,
            "MESSAGE_REACTION_REMOVE": self._handle_message_reaction_remove,
            # "MESSAGE_REACTION_REMOVE_ALL": self._handle_message_reaction_remove_all,
            # "MESSAGE_REACTION_REMOVE_EMOJI": self._handle_message_reaction_remove_all_emoji,
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
    def cache(self) -> APICache:
        return self.parent.cache

    @property
    def intents(self) -> Intents:
        return self.parent.gateway.intents

    @property
    def dispatch(self) -> Any:
        return self.parent.dispatch

    async def handle_dispatch(self, event_name: str, data: dict) -> None:
        """
        Handle a Dispatch message from Discord.
        """

        if event_name == "READY":
            self.cache.user = User(state=self.parent, data=data['user'])
            self.cache.application_id = try_snowflake(data['application']['id'])
            self.shard.resume_url = data['resume_gateway_url']
            self.shard.session_id = data['session_id']
            for g in data["guilds"]:
                asyncio.create_task(self.handle_dispatch("GUILD_CREATE", g))
            self.dispatch("READY")
            return None
        elif event_name == "RESUMED":
            return None

        coro: Callable[[Any], Awaitable[None]] | None
        if self.parent.gateway.guild_ids_only:
            if event_name == "GUILD_CREATE":
                # Cast to avoid coro from being typed too specifically
                # This is a compromise to avoid 50 different @overload's for every single
                # dispatch handler's individual data type
                coro = cast(Callable[[Any], Awaitable[None]], self._handle_guild_create_id_only)
            elif event_name == "GUILD_DELETE":
                coro = self.EVENT_HANDLER["GUILD_DELETE"]
            else:
                return
        else:
            coro = self.EVENT_HANDLER.get(event_name)
        if coro is None:
            log.warning(
                "Failed to parse event %s %s"
                % (event_name, dump(data))
            )
        else:
            await coro(data)

    @staticmethod
    def ignore(event_name: str) -> Callable[..., Any]:
        async def wrapper(data: Any) -> None:
            return
        return wrapper

    async def _handle_interaction(
            self,
            data: payloads.Interaction) -> None:
        self.dispatch(
            "INTERACTION_CREATE",
            Interaction(state=self.parent, data=data),
        )

    async def _handle_guild_create(
            self,
            data: payloads.GatewayGuild) -> None:
        if data.get("unavailable"):
            return  # Don't do anything for unavailable guilds
        guild = Guild(state=self.parent, data=data)
        self.cache.add_guilds(guild)
        await guild._sync(data=data)
        self.dispatch("GUILD_CREATE", guild)

    async def _handle_guild_create_id_only(
            self,
            data: payloads.GatewayGuild) -> None:
        """
        The non-cache version of guild create that we just have
        so as to keep a guild count internally.
        """

        self.cache.guild_ids.add(int(data["id"]))

    async def _handle_guild_update(
            self,
            data: payloads.GatewayGuild) -> None:
        # The guild update over the gateway includes stickers,
        # roles, and emojis, as well as the guild attributes

        # Get current object
        cached = self.cache.guilds.get(int(data["id"]), None)

        # Update cached object with updated cached items (since they
        # get their own events, they won't be included as part of the
        # guild update, so this is safe to do)
        if cached is not None:

            # Store new copy in cache
            before = copy(cached)  # create a copy of current for dispatch
            after = cached._update(data)  # update with new attrs
            await after._sync(data)

        # We didn't have a version cached already so we're gonna store
        # this one anew but not dispatch the usual update method
        else:
            before = None
            after = Guild(state=self.parent, data=data)
            await after._sync(data=data)
            self.cache.add_guilds(after)
            self.dispatch("RAW_GUILD_UPDATE", after)

        if before is None and self.intents.guilds:
            log.warning(
                "Failed to get cached guild %s, ignoring guild update"
                % after.id
            )
            return
        self.dispatch("GUILD_UPDATE", before, after)

    async def _handle_guild_delete(self, data: dict[str, str]) -> None:
        # Get from cache if we can
        self.dispatch("RAW_GUILD_DELETE", int(data["id"]))
        try:
            self.cache.guild_ids.remove(int(data["id"]))
        except KeyError:
            pass
        current = self.cache.guilds.pop(int(data["id"]), None)
        if current is None:
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
        for id in list(current._channels.keys()):
            try_delete(self.cache.channels, id)
            del current._channels[id]

        # And dispatch
        self.dispatch("GUILD_DELETE", current)

    async def _handle_guild_emojis_update(
            self,
            data: gw.GuildEmojisUpdate) -> None:
        guild = self.cache.get_guild(data["guild_id"])
        if isinstance(guild, Guild):
            await guild._sync(data)

    async def _handle_guild_stickers_update(
            self,
            data: gw.GuildStickersUpdate) -> None:
        guild = self.cache.get_guild(data["guild_id"])
        if isinstance(guild, Guild):
            await guild._sync(data)

    async def _handle_typing(
            self,
            data: gw.TypingStart) -> None:
        """Handle the typing event; return the guild, channel, and user IDs."""

        self.dispatch("RAW_TYPING", int(data["channel_id"]), int(data["user_id"]))

        # This will only dispatch an event if the typing is triggered inside of
        # a guild. Just for my own ease.

        channel = self.cache.get_channel(data["channel_id"])
        if channel is None:
            return
        channel.guild_id = try_id(data.get("guild_id"))

        # This event isn't good for a lot, but it DOES give us a new
        # member payload if the typing was started in a guild
        if "member" in data:
            assert isinstance(channel.guild, Guild)
            member = channel.guild._add_member(data["member"])  # adds to cache
            self.dispatch("TYPING", channel, member)
            return

        # Unfortunately it tells us nothing about a user (ie a non-guild
        # member) so we just have to build something that acts like it if they
        # don't exist in cache.
        user = self.cache.get_user(data["user_id"])
        if user is None:
            return
        self.dispatch("TYPING", channel, user)

    async def _handle_message_generic(
            self,
            data: payloads.Message) -> tuple[Message | None, Message] | None:
        """Handle message create and message edit."""

        # If there's no author, it's a webhook message
        if "author" not in data:
            return None

        # Get a message from cache (in case it's an edit or delete)
        cached = self.cache.get_message(data["id"])
        if cached is not None:
            current = copy(cached)
            message = cached._update(data)  # because a message already existed we don't need to add it to cache

            # If we got here, then a new author will not be created by the message,
            # so we're going to update the cache with our new data, as well as
            # write back some of our cached items into the object
            if isinstance(message.author, GuildMember):
                assert "member" in data
                assert "guild_id" in data
                message.author._update(data["member"])
                message.author._user._update(data["author"])
                guild = self.cache.get_guild(data["guild_id"])
                message.guild = guild
                message.author.guild = guild
            else:
                message.author._update(data["author"])

        # Create a new message
        # Doing this will try and read from cache, but afterwards will create
        # new objects (of things like User, GuildMember, and Channel).
        # If new objects are made, then we want to write these back to the
        # cache (apart from Channel, which isn't a full object).
        else:
            current = None
            message = Message(state=self.parent, data=data)
            self.cache.add_messages(message)  # message to cache

        return current, message

    async def _handle_message_create(
            self,
            data: payloads.Message) -> None:
        """Handle message create event."""

        message = await self._handle_message_generic(data)
        if message is None:
            return
        self.dispatch("MESSAGE_CREATE", message[1])

    async def _handle_message_edit(
            self,
            data: payloads.Message) -> None:
        """Handle message edit event."""

        message = await self._handle_message_generic(data)
        if message is None:
            return
        self.dispatch("RAW_MESSAGE_UPDATE", message[1])
        if message[0] is None:
            return
        self.dispatch("MESSAGE_UPDATE", *message)

    async def _handle_message_delete(
            self,
            data: payloads.Message) -> None:
        """Handle message delete; returns channel and either cached message or
        the message ID."""

        self.dispatch("RAW_MESSAGE_DELETE", int(data["channel_id"]), int(data["id"]))

        # Get cached message
        message = self.cache.messages.pop(int(data["id"]), None)
        if message is None:
            return
        self.dispatch("MESSAGE_DELETE", message)

    async def _handle_presence_update(
            self,
            data: payloads.Presence) -> None:
        """Handle updating presences for users."""

        user = self.cache.get_user(data["user"]["id"])
        if user is None:
            return  # Can't do anything with the presence user object really
        before = copy(user)
        user._update_presence(data)
        self.dispatch("PRESENCE_UPDATE", before, user)

    async def _handle_channel_generic(
            self,
            data: payloads.Channel) -> tuple[Channel | None, Channel]:
        """Handle channel create and update events."""

        cached = self.cache.get_channel(data["id"])
        if cached:
            current = copy(cached)
            channel = cached._update(data)
        else:
            current = None
            channel = Channel(state=self.parent, data=data)
            guild = channel.guild
            if isinstance(guild, Guild):
                guild._add_channel(channel)
            self.cache.add_channels(channel)
        return current, channel

    async def _handle_channel_create(
            self,
            data: payloads.Channel) -> None:
        """Handle channel create event."""

        channel = await self._handle_channel_generic(data)
        self.dispatch("CHANNEL_CREATE", channel[1])

    async def _handle_channel_update(
            self,
            data: payloads.Channel) -> None:
        """Handle channel update event."""

        channel = await self._handle_channel_generic(data)
        self.dispatch("RAW_CHANNEL_UPDATE", channel[1])
        if not channel[0]:
            return
        self.dispatch("CHANNEL_UPDATE", *channel)

    async def _handle_channel_delete(
            self,
            data: payloads.Channel) -> None:
        """Handle channel delete event."""

        # For whatever reason, Discord's CHANNEL_DELETE payload gives
        # us the entire channel.
        # I'm not entirely sure why they do this, but we can use this
        # to avoid making a `raw_channel_delete` dispatch and instead
        # just dispatch a new channel instance each time it's generated.
        # This does mean our library end-user doesn't know if a channel
        # was cached or not, but I'm not certain that's something they
        # particularly need to know.
        channel_id = int(data["id"])
        channel = self.cache.channels.pop(channel_id, None)
        if channel:
            self.dispatch("CHANNEL_DELETE", channel)
            return
        channel = Channel(state=self.parent, data=data)
        self.dispatch("CHANNEL_DELETE", channel)

    async def _handle_guild_ban(
            self,
            data: dict[str, Any]) -> None:
        """Handle guild ban event."""

        # Get cached guild member
        guild: Guild | BaseGuild = self.cache.get_guild(data["guild_id"])
        member: GuildMember | None = None
        if isinstance(guild, Guild):
            member = guild._members.pop(int(data["user"]["id"]), None)

        # Get user if we couldn't get a guild member
        if member is None:
            user: User | None = self.cache.get_user(data["user"]["id"])
            if user is None:
                user = User(state=self.parent, data=data["user"])
        else:
            user = member._user

        # Remove guild ID from the user's guild list
        try:
            user._guilds.remove(guild.id)
        except KeyError:
            pass

        self.dispatch("GUILD_BAN_ADD", guild, user)

    async def _handle_guild_unban(
            self,
            data: dict[str, Any]) -> None:
        """Handle guild unban event."""

        # We're gonna assume we don't have this user and just build them from
        # scratch.
        # We won't cache them from this, but if they're already cached, we'll
        # use this new payload to update them.
        user = self.cache.get_user(data["user"]["id"])
        if user is None:
            user = User(state=self.parent, data=data["user"])
        else:
            user = user._update(data["user"])
        guild = self.cache.get_guild(data["guild_id"])
        self.dispatch("GUILD_BAN_REMOVE", guild, user)

    async def _handle_invite_create(
            self,
            data: payloads.Invite) -> None:
        """Handle invite create event."""

        # The invite object pulls both the guild and the channel objects from
        # cache in its constructor -
        # the guild is actually a more full object than one found in BaseGuild,
        # so we're just going to leave it as is and let it do what it wants.

        self.dispatch("INVITE_CREATE", Invite(state=self.parent, data=data))

    async def _handle_invite_delete(
            self,
            data: dict[str, str]) -> None:
        """Handle an invite delete."""

        channel = self.cache.get_channel(data["channel_id"])
        if channel is None:
            return
        self.dispatch("INVITE_DELETE", channel, data["code"])

    async def _handle_role_generic(
            self,
            data: gw.RoleCreateUpdate) -> tuple[Role | None, Role] | None:
        """Handle a role being created."""

        guild = self.cache.get_guild(data["guild_id"])
        if not isinstance(guild, Guild):
            return None
        cached = guild.get_role(data["role"]["id"])
        if cached:
            current = copy(cached)
            role = cached._update(data["role"])
        else:
            current = None
            role = Role(state=self.parent, data=data["role"], guild=guild)
            guild._add_role(role)
        return current, role

    async def _handle_role_create(
            self,
            data: gw.RoleCreateUpdate) -> None:
        """Handle role create."""

        role = await self._handle_role_generic(data)
        if role is None:
            return
        self.dispatch("ROLE_CREATE", role)

    async def _handle_role_update(
            self,
            data: gw.RoleCreateUpdate) -> None:
        """Handle role update."""

        role = await self._handle_role_generic(data)
        if role is None:
            return
        self.dispatch("RAW_ROLE_UPDATE", role[1])
        if role[0] is None:
            return
        self.dispatch("ROLE_UPDATE", *role)

    async def _handle_role_delete(
            self,
            data: gw.RoleDelete) -> None:
        """Handle role delete."""

        self.dispatch("RAW_ROLE_DELETE", int(data["guild_id"]), int(data["role_id"]))
        guild = self.cache.get_guild(data["guild_id"])
        if not isinstance(guild, Guild):
            return
        role = guild._roles.pop(int(data["role_id"]), None)
        if role is None:
            return
        self.dispatch("ROLE_DELETE", role)

    async def _handle_guild_member_generic(
            self,
            data: payloads.GuildMember) -> tuple[GuildMember | None, GuildMember]:
        """Handle member create and update."""

        guild = self.cache.get_guild(data["guild_id"])
        if not isinstance(guild, Guild):
            current = None
            member = GuildMember(state=self.parent, data=data)
        else:
            cached = guild.get_member(data["user"]["id"])
            if cached:
                current = copy(cached)
                member = cached._update(data)
            else:
                current = None
                member = GuildMember(state=self.parent, data=data)
                guild._add_member(member)
        return current, member

    async def _handle_guild_member_add(
            self,
            data: payloads.GuildMember) -> None:
        """Handle guild member create."""

        member = await self._handle_guild_member_generic(data)
        self.dispatch("GUILD_MEMBER_ADD", member[1])

    async def _handle_guild_member_update(
            self,
            data: payloads.GuildMember) -> None:
        """Handle guild member update."""

        member = await self._handle_guild_member_generic(data)
        self.dispatch("RAW_GUILD_MEMBER_UPDATE", member[1])
        if member[0] is None:
            return
        self.dispatch("GUILD_MEMBER_UPDATE", *member)

    async def _handle_guild_member_remove(
            self,
            data: payloads.GuildMemberRemove) -> None:
        """Handle guild member being removed."""

        self.dispatch("RAW_GUILD_MEMBER_REMOVE", int(data["guild_id"]), int(data["user"]["id"]))

        guild = self.cache.get_guild(data["guild_id"])
        member: GuildMember | None = None
        user: User | None = None
        if isinstance(guild, Guild):
            member = guild._members.pop(int(data["user"]["id"]), None)
            if member:
                self.dispatch("GUILD_MEMBER_REMOVE", guild, member)
                try:
                    member._user._guilds.remove(guild.id)
                except KeyError:
                    pass
                if not member._user._guilds:
                    self.cache.users.pop(member.id, None)
                return
        if member is None:
            user = self.cache.get_user(data["user"]["id"])
            if user is None:
                user = User(state=self.parent, data=data["user"])
                # We are making the deliberate choice here to not add this user
                # to the cache.
            else:
                user._update(data["user"])
                # This user is already in the cache, but is not a guild member.
                # We're just going to leave them there.

        self.dispatch("GUILD_MEMBER_REMOVE", guild, member or user)

    async def _handle_guild_member_chunk(self, data: gw.GuildMemberChunk) -> None:
        """Handle response from chunk request."""

        # This is a bit of an odd one in that it's a websocket request
        # made by the user, rather than just coming straight from the
        # gateway.
        # We're going to add to the guild members cache, but not to the
        # user cache. An odd choice when taken in a vacuum, but this
        # is a state that will not necessarily update itself.
        # Ideally we wouldn't add to the guild member cache either, but
        # due to how I've implemented this, the nonce is not required,
        # so these members need to go _somewhere_.
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

    async def _handle_message_reaction_generic(
            self,
            data: gw.ReactionAddRemove) -> tuple[GuildMember | User | int, Reaction]:
        """Handle reaction add or remove."""

        # Now this is an annoying one.
        # Reaction add gives us an emoji payload and a full guild member
        # (or user ID).
        # Reaction remove gives us an emoji payload.
        # Neither give us a message, just a message/channel/guild? id.
        # In addition, there's REACTION_REMOVE and REACTION_REMOVE_EMOJI.
        # I don't know what the difference is.

        # Get message from cache
        created = Reaction(state=self.parent, data=data)

        # Get the guild from cache if one exists
        guild: BaseGuild | Guild | None = None
        if "guild_id" in data:
            guild = self.cache.get_guild(data["guild_id"])

        # Update our cache with the created member object
        user: User | GuildMember | None = None
        if "member" in data:
            assert isinstance(guild, Guild)
            user = guild._add_member(data["member"])
        else:
            user = self.cache.get_user(data["user_id"])

        if user is None:
            return int(data["user_id"]), created
        return user, created

    async def _handle_message_reaction_add(
            self,
            data: gw.ReactionAddRemove) -> None:
        """Handle reaction add."""

        created = await self._handle_message_reaction_generic(data)
        self.dispatch("REACTION_ADD", *created)

    async def _handle_message_reaction_remove(
            self,
            data: gw.ReactionAddRemove) -> None:
        """Handle reaction remove."""

        created = await self._handle_message_reaction_generic(data)
        self.dispatch("REACTION_REMOVE", *created)

    # async def _handle_message_reaction_remove_all(
    #         self,
    #         data: gw.ReactionAddRemove) -> None:
    #     """Handle reaction remove all."""

    #     message = self.cache.get_message(data["message_id"])
    #     if message is None:
    #         yield Object(data["message_id"], state=self.parent)
    #         return
    #     yield message

    # async def _handle_message_reaction_remove_all_emoji(
    #         self,
    #         data: gw.ReactionAddRemove) -> Ret[Reaction]:
    #     """Handle reaction remove all for emoji."""

    #     created = await self._handle_message_reaction_generic(data)
    #     yield created[1]

    # async def _handle_thread_create(
    #         self,
    #         data: payloads.Channel) -> Ret[Thread]:
    #     """Handle thread creation."""

    #     assert "guild_id" in data  # You can only have threads in guilds
    #     guild = self.cache.get_guild(data["guild_id"])
    #     created = channel_builder(state=self.parent, data=data, guild_id=guild.id)
    #     assert isinstance(created, Thread)
    #     if isinstance(guild, Guild):
    #         guild._add_thread(created)  # pyright: ignore
    #     yield created

    # async def _handle_thread_update(
    #         self,
    #         data: payloads.Channel) -> Ret[tuple[Thread | None, Thread]]:
    #     """Handle thread update."""

    #     assert "guild_id" in data  # You can only have threads in guilds
    #     guild = self.cache.get_guild(data["guild_id"])
    #     created = channel_builder(state=self.parent, data=data, guild_id=guild.id)
    #     assert isinstance(created, Thread)
    #     current = None
    #     if isinstance(guild, Guild):
    #         current = guild._threads.get(created.id)
    #         guild._add_thread(created)  # pyright: ignore
    #     yield current, created

    # async def _handle_thread_member_list_update(
    #         self,
    #         data: gw.ThreadMemberListUpdate) -> Ret[Thread | Channel]:
    #     """Handle a thread's member list being updated."""

    #     thread = self.cache.get_channel(data["id"])
    #     if thread is None:
    #         return
    #     if isinstance(thread, Thread):
    #         for member_payload in data.get("added_members", []):
    #             assert "member" in member_payload
    #             member = ThreadMember(
    #                 state=self.parent,
    #                 data=member_payload,
    #                 guild_id=data["guild_id"],
    #             )
    #             thread._add_member(member)
    #         for member_id in data.get("removed_member_ids", []):
    #             thread._remove_member(member_id)
    #         thread.member_count = data["member_count"]
    #     yield thread

    async def _handle_voice_state(
            self,
            data: payloads.VoiceState) -> None:
        """Handle voice state update."""

        if "guild_id" not in data:
            return
        guild = self.cache.get_guild(data["guild_id"])
        user_id = int(data["user_id"])
        if guild is None or not isinstance(guild, Guild):
            return
        current = guild._voice_states.get(user_id)
        if current:
            created = current
            current = copy(current)
            created._update(data)
        else:
            created = VoiceState(state=self.parent, data=data)
        if created.channel:
            guild._add_voice_state(created)
            self.dispatch("VOICE_STATE_UPDATE", current, created)
        else:
            guild._voice_states.pop(user_id, None)
            self.dispatch("VOICE_STATE_UPDATE", current, None)

    async def _handle_audit_log_entry(
            self,
            data: payloads.AuditLogEntry) -> None:
        """Handle audit log entry events."""

        self.dispatch("AUDIT_LOG_ENTRY", AuditLogEntry(data=data, log=None))
