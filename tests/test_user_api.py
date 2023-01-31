import random
from typing import NoReturn

import pytest

import novus

from ._setup import get_connection, get_data

known_human_ids, known_bot_ids, known_guild_ids = get_data()


@pytest.mark.asyncio
async def test_get_current_user() -> None:
    state = get_connection()
    await novus.User.fetch_me(state)


@pytest.mark.parametrize("user_id", random.choices(known_human_ids + known_bot_ids, k=3))
@pytest.mark.asyncio
async def test_get_any_user(user_id: int) -> None:
    state = get_connection()
    try:
        await novus.User.fetch(state, user_id)
    except novus.HTTPException:
        assert False, "User with ID %s doesn't exist" % user_id
    else:
        assert True


@pytest.mark.parametrize("user_id", [69, 420, 14])
@pytest.mark.asyncio
async def test_fail_get_user(user_id: int) -> None:
    state = get_connection()
    try:
        user = await novus.User.fetch(state, user_id)
    except novus.NotFound:
        assert True
    else:
        assert False, "User with ID %s does exist" % user.id


@pytest.mark.skip("No \"nice\" implementation")
@pytest.mark.asyncio
async def test_modify_current_user() -> NoReturn:
    raise NotImplementedError()


@pytest.mark.asyncio
async def test_get_current_user_guilds() -> None:
    state = get_connection()
    await novus.User.fetch_my_guilds(state)


@pytest.mark.skip("Only available with Oauth")
@pytest.mark.parametrize("guild_id", random.choices(known_guild_ids, k=3))
@pytest.mark.asyncio
async def test_get_current_user_guild_member(guild_id: int) -> NoReturn:
    raise NotImplementedError()


@pytest.mark.skip("No reasonable way to test")
@pytest.mark.asyncio
async def test_leave_guild() -> NoReturn:
    raise NotImplementedError()


@pytest.mark.parametrize("user_id", random.choices(known_human_ids, k=3))
@pytest.mark.asyncio
async def test_create_dm(user_id: int) -> None:
    state = get_connection()
    fake_user = novus.Object(user_id, state=state)
    await novus.User.create_dm_channel(fake_user)
