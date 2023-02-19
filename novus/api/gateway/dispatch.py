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
from typing import TYPE_CHECKING, Any, AsyncIterator, Callable, TypeAlias, TypeVar

from ...models import (
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
)
from ...models.channel import channel_builder
from ...utils import try_snowflake

if TYPE_CHECKING:
    from ... import Intents, payloads
    from ...models import api_mixins as amix
    from ...payloads import gateway as gw
    from .._http import HTTPConnection


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

    def __init__(self, parent: HTTPConnection) -> None:
        self.parent = parent
        self.cache = self.parent.cache
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
            # "Thread update": None,
            # "Thread delete": None,
            # "Thread list sync": None,
            # "Thread member update": None,
            "THREAD_MEMBERS_UPDATE": self._handle_thread_member_list_update,
            "GUILD_CREATE": self._handle_guild_create,
            "GUILD_UPDATE": self._handle_guild_update,
            "GUILD_DELETE": self._handle_guild_delete,
            # "Guild audit log entry create": None,
            "GUILD_BAN_ADD": self._handle_guild_ban,
            "GUILD_BAN_REMOVE": self._handle_guild_unban,
            "GUILD_EMOJIS_UPDATE": self._handle_guild_emojis_update,
            "GUILD_STICKERS_UPDATE": self._handle_guild_stickers_update,
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
            # "Voice state update": None,
            # "Voice server update": None,
            # "Webhooks update": None,
            "INTERACTION_CREATE": self._handle_interaction,
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
            data: gw.GuildEmojisUpdate) -> Ret[tuple[Guild | amix.GuildAPIMixin, list[Emoji]]]:
        """Handle guild emojis update. For whatever reason Discord gives us
        the entire guild emoji list for every update."""

        guild = self.cache.get_guild(data["guild_id"], or_object=True)
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
            data: gw.GuildStickersUpdate) -> Ret[tuple[Guild | amix.GuildAPIMixin, list[Sticker]]]:
        """Handle guild stickers update. For whatever reason Discord gives us
        the entire guild stickers list for every update."""

        guild = self.cache.get_guild(data["guild_id"], or_object=True)
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
            data: gw.TypingStart) -> OptRet[tuple[Channel, GuildMember | User | amix.UserAPIMixin]]:
        """Handle the typing event; return the guild, channel, and user IDs."""

        guild: Guild | amix.GuildAPIMixin | None = None
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
                )
            yield channel, member
            return

        # Unfortunately it tells us nothing about a user so we just have to
        # build something that acts like it if they don't exist in cache.
        user = self.cache.get_user(data["user_id"], or_object=True)
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
        current = self.cache.get_message(message.id, or_object=False)
        self.cache.add_messages(message)

        # Update channel with cached
        channel = self.cache.get_channel(message.channel.id)
        if channel is not None:
            message.channel = channel

        # Update guild with cached
        if message.guild is not None:
            guild = self.cache.get_guild(message.guild.id, or_object=True)
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

        channel = self.cache.get_channel(data["channel_id"], or_object=True)
        message = self.cache.messages.pop(int(data["id"]), None)
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

        log.debug("Ignoring presence update %s" % dump(data))
        yield None

    async def _handle_channel_generic(
            self,
            data: payloads.Channel) -> tuple[Channel | None, Channel]:
        """Handle channel create and update events."""

        current = self.cache.get_channel(data["id"])
        guild: Guild | amix.GuildAPIMixin | None = None
        guild_id: int | None = None
        if "guild_id" in data:
            guild = self.cache.get_guild(data["guild_id"], or_object=True)
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
        # object
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
            guild = self.cache.get_guild(data["guild_id"], or_object=True)
            channel.guild = guild
        yield channel

    async def _handle_guild_ban(
            self,
            data: dict[str, Any]) -> Ret[tuple[Guild | amix.GuildAPIMixin, User | GuildMember]]:
        """Handle guild ban event."""

        user = self.cache.get_user(data["user"]["id"], or_object=False)
        if user is None:
            user = User(state=self.parent, data=data["user"])
        guild = self.cache.get_guild(data["guild_id"], or_object=True)
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
            data: dict[str, Any]) -> Ret[tuple[Guild | amix.GuildAPIMixin, User]]:
        """Handle guild unban event."""

        # We're gonna assume we don't have this user and just build them from
        # scratch
        user = User(state=self.parent, data=data["user"])
        guild = self.cache.get_guild(data["guild_id"], or_object=True)
        yield guild, user,

    async def _handle_invite_create(
            self,
            data: payloads.Invite) -> Ret[Invite]:
        """Handle invite create event."""

        invite = Invite(state=self.parent, data=data)  # pyright: ignore

        # Because this creates both a channel AND a guild object, we're gonna
        # try and get those from the cache
        channel: Channel | None = None
        if invite.channel:
            channel = self.cache.get_channel(invite.channel.id)
            if channel:
                invite.channel = channel
        if invite.guild:
            guild = self.cache.get_guild(invite.guild.id)
            if guild:
                invite.guild = guild
            if channel:
                channel.guild = guild

        yield invite

    async def _handle_invite_delete(
            self,
            data: dict[str, str]) -> Ret[tuple[Guild | amix.GuildAPIMixin, Channel, str]]:
        """Handle an invite delete."""

        guild = self.cache.get_guild(data["guild_id"], or_object=True)
        channel = self.cache.get_channel(data["channel_id"], or_object=True)
        channel.guild = guild
        yield guild, channel, data["code"],

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
        yield role[1]

    async def _handle_role_update(
            self,
            data: gw.RoleCreateUpdate) -> Ret[tuple[Role | None, Role]]:
        """Handle role update."""

        role = await self._handle_role_generic(data)
        yield role

    async def _handle_role_delete(
            self,
            data: gw.RoleDelete) -> Ret[Role | amix.RoleAPIMixin]:
        """Handle role delete."""

        guild = self.cache.get_guild(data["guild_id"], or_object=True)
        role: Role | amix.RoleAPIMixin | None = None
        if isinstance(guild, Guild):
            role = guild._roles.pop(int(data["role_id"]), None)
        if role is None:
            role = Object(data["role_id"], state=self.parent).add_api(Role)
            role.guild = guild
        yield role

    async def _handle_guild_member_generic(
            self,
            data: payloads.GuildMember) -> tuple[GuildMember | None, GuildMember]:
        """Handle member create and update."""

        guild = self.cache.get_guild(data["guild_id"], or_object=True)
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
            data: dict[str, Any]) -> Ret[tuple[Guild | amix.GuildAPIMixin, GuildMember | User]]:
        """Handle guild member being removed."""

        guild = self.cache.get_guild(data["guild_id"], or_object=True)
        user: GuildMember | User | None = None
        if isinstance(guild, Guild):
            user = guild._members.pop(int(data["user"]["id"]), None)
            if user:
                try:
                    user._user._guilds.remove(guild.id)
                except KeyError:
                    pass
                if not user._user._guilds:
                    self.cache.users.pop(user.id, None)
        if user is None:
            user = User(state=self.parent, data=data["user"])  # don't cache
        yield guild, user,

    async def _handle_message_reaction_generic(
            self,
            data: gw.ReactionAddRemove) -> tuple[GuildMember | User | amix.UserAPIMixin, Reaction]:
        """Handle reaction add or remove."""

        created = Reaction(state=self.parent, data=data)
        message = self.cache.get_message(created.message.id, or_object=False)
        if message:
            created.message = message

        guild: Guild | None = None
        if "guild_id" in data:
            guild = self.cache.get_guild(data["guild_id"], or_object=False)

        user: User | GuildMember | amix.UserAPIMixin | None = None
        if created.message is not None and "member" in data:
            assert guild
            user = guild._add_member(data["member"])
        if user is None:
            user = self.cache.get_user(data["user_id"], or_object=True)

        return user, created

    async def _handle_message_reaction_add(
            self,
            data: gw.ReactionAddRemove) -> Ret[tuple[GuildMember | User | amix.UserAPIMixin, Reaction]]:
        """Handle reaction add."""

        created = await self._handle_message_reaction_generic(data)
        yield created[0], created[1],

    async def _handle_message_reaction_remove(
            self,
            data: gw.ReactionAddRemove) -> Ret[tuple[GuildMember | User | amix.UserAPIMixin, Reaction]]:
        """Handle reaction remove."""

        created = await self._handle_message_reaction_generic(data)
        yield created[0], created[1],

    async def _handle_message_reaction_remove_all(
            self,
            data: gw.ReactionAddRemove) -> Ret[Message | amix.MessageAPIMixin]:
        """Handle reaction remove all."""

        message = self.cache.get_message(data["message_id"], or_object=True)
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

        assert "guild_id" in data
        guild = self.cache.get_guild(data["guild_id"], or_object=True)
        created = channel_builder(state=self.parent, data=data, guild_id=guild.id)
        assert isinstance(created, Thread)
        if isinstance(guild, Guild):
            guild._add_thread(created)  # pyright: ignore
        yield created

    async def _handle_thread_member_list_update(
            self,
            data: gw.ThreadMemberListUpdate) -> Ret[Thread | Channel]:
        """Handle a thread's member list being updated."""

        thread = self.cache.get_channel(data["id"], or_object=True)
        guild = self.cache.get_guild(data["guild_id"], or_object=True)
        if isinstance(thread, Thread):
            for member_payload in data.get("added_members", []):
                member: GuildMember | None = None
                if isinstance(guild, Guild):
                    member_id = int(member_payload["member"]["user"]["id"])
                    member = guild.get_member(member_id)
                if member is None:
                    member = GuildMember(
                        state=self.parent,
                        data=member_payload["member"],
                        guild_id=guild.id,
                    )
                thread._add_member(member)
            for member_id in data.get("removed_member_ids", []):
                thread._remove_member(member_id)
            thread.member_count = data["member_count"]
        yield thread
