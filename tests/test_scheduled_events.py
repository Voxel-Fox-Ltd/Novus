from __future__ import annotations

import operator
from datetime import datetime as dt
from datetime import timedelta

import pytest

import novus

from ._setup import ConfigGuild, cache, get_connection, get_data, max_choices, to_object

users, guilds = get_data()


@pytest.mark.parametrize(
    "guild",
    max_choices(filter(operator.attrgetter("present"), guilds), k=3),
)
@pytest.mark.asyncio
async def test_get_guild_events(guild: ConfigGuild) -> None:
    state = get_connection()
    fake_guild = novus.Object(guild.id, state=state)
    await novus.Guild.fetch_scheduled_events(fake_guild)


guild_event_pairs: list[tuple[ConfigGuild, int]] = []
for g in guilds:
    for i in g.scheduled_events:
        guild_event_pairs.append((g, i))


@pytest.mark.parametrize(
    "guild_event_pairs",
    max_choices(guild_event_pairs, k=3),
)
@pytest.mark.asyncio
async def test_get_event(guild_event_pairs: tuple[ConfigGuild, int]) -> None:
    guild, event_id = guild_event_pairs
    state = get_connection()
    await novus.ScheduledEvent.fetch(state, guild.id, event_id)


@pytest.mark.parametrize(
    "guild_event_pairs",
    max_choices(guild_event_pairs, k=3),
)
@pytest.mark.asyncio
async def test_get_event_users(guild_event_pairs: tuple[ConfigGuild, int]) -> None:
    guild, event_id = guild_event_pairs
    state = get_connection()
    fake_event = novus.Object(event_id, state=state, guild_id=guild.id)
    await novus.ScheduledEvent.fetch_users(fake_event)  # type: ignore


@pytest.mark.parametrize("run", range(2))
@pytest.mark.asyncio
async def test_create_event(run: int) -> None:
    guild = ConfigGuild.get_test()
    state = get_connection()
    fake_guild = to_object(guild, state=state)
    created = await novus.Guild.create_scheduled_event(
        fake_guild,
        name="Test Event",
        start_time=dt.utcnow() + timedelta(days=run),
        end_time=dt.utcnow() + timedelta(days=run + 1),  # required for external
        entity_type=novus.EventEntityType.external,
        privacy_level=novus.EventPrivacyLevel.guild_only,
        location="https://voxelfox.co.uk",
    )
    cache.scheduled_event_id = (created.id, guild.id,)


@pytest.mark.parametrize("run", range(2))
@pytest.mark.asyncio
async def test_edit_event(run: int) -> None:
    event_id: int
    guild_id: int
    event_id, guild_id = cache.scheduled_event_id[run]
    state = get_connection()
    fake_event = novus.Object(event_id, state=state, guild_id=guild_id)
    await novus.ScheduledEvent.edit(  # type: ignore
        fake_event,  # type: ignore
        name="Edited Test Event",
    )


@pytest.mark.parametrize("run", range(2))
@pytest.mark.asyncio
async def test_delete_event(run: int) -> None:
    event_id: int
    guild_id: int
    event_id, guild_id = cache.scheduled_event_id[run]
    state = get_connection()
    fake_event = novus.Object(event_id, state=state, guild_id=guild_id)
    await novus.ScheduledEvent.delete(fake_event)  # type: ignore
