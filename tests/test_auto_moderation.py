from __future__ import annotations

import operator

import pytest

import novus

from ._setup import ConfigGuild, cache, get_connection, get_data, max_choices, to_object

users, guilds = get_data()


@pytest.mark.parametrize(
    "guild",
    max_choices(filter(operator.attrgetter("admin"), guilds), k=3),
)
@pytest.mark.asyncio
async def test_get_automod(guild: ConfigGuild) -> None:
    state = get_connection()
    fake_guild = to_object(guild, state=state)
    await novus.Guild.fetch_auto_moderation_rules(fake_guild)


guild_automod_pairs: list[tuple[ConfigGuild, int]] = []
for g in guilds:
    for i in g.automod_rules:
        guild_automod_pairs.append((g, i))


@pytest.mark.parametrize(
    "guild_automod_pair",
    max_choices(guild_automod_pairs, k=3),
)
@pytest.mark.asyncio
async def test_get_rule(guild_automod_pair: tuple[ConfigGuild, int]) -> None:
    guild, rule_id = guild_automod_pair
    state = get_connection()
    await novus.AutoModerationRule.fetch(state, guild.id, rule_id)


@pytest.mark.parametrize("run", range(2))
@pytest.mark.asyncio
async def test_create_rule(run: int) -> None:
    guild = ConfigGuild.get_test()
    state = get_connection()
    fake_guild = to_object(guild, state=state)
    created = await novus.Guild.create_auto_moderation_rule(
        fake_guild,
        name="Test Case",
        event_type=novus.AutoModerationEventType.message_send,
        trigger_type=novus.AutoModerationTriggerType.keyword,
        trigger_metadata=novus.AutoModerationTriggerMetadata(
            keyword_filters=["testCaseCreatedAutomodRule"],
        ),
        actions=[
            novus.AutoModerationAction(
                type=novus.AutoModerationActionType.block_message,
            ),
        ],
    )
    cache.automod_rule_id = (created.id, guild.id,)


@pytest.mark.parametrize("run", range(2))
@pytest.mark.asyncio
async def test_edit_rule(run: int) -> None:
    rule_id: int
    guild_id: int
    rule_id, guild_id = cache.automod_rule_id[run]
    state = get_connection()
    fake_rule = novus.Object(rule_id, state=state, guild_id=guild_id)
    await novus.AutoModerationRule.edit(  # type: ignore
        fake_rule,  # type: ignore
        name="Edited Test Case",
    )


@pytest.mark.parametrize("run", range(2))
@pytest.mark.asyncio
async def test_delete_rule(run: int) -> None:
    rule_id: int
    guild_id: int
    rule_id, guild_id = cache.automod_rule_id[run]
    state = get_connection()
    fake_rule = novus.Object(rule_id, state=state, guild_id=guild_id)
    await novus.AutoModerationRule.delete(fake_rule)  # type: ignore
