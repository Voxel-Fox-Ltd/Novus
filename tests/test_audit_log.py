from __future__ import annotations

import operator
from typing import TYPE_CHECKING

import pytest

import novus

from ._setup import get_connection, get_data, max_choices, to_object

if TYPE_CHECKING:
    from ._setup import ConfigGuild


users, guilds = get_data()


@pytest.mark.parametrize(
    "guild",
    max_choices(filter(operator.attrgetter("admin"), guilds), k=3),
)
@pytest.mark.asyncio
async def test_get_audit_log(guild: ConfigGuild) -> None:
    state = get_connection()
    fake_guild = to_object(guild, state=state)
    await novus.Guild.fetch_audit_logs(fake_guild)
