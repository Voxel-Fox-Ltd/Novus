import pytest
import novus

from ._setup import get_connection, get_data


known_user_ids, known_guild_ids = get_data()


@pytest.mark.parametrize("user_id", known_user_ids)
@pytest.mark.asyncio
async def test_get_any_user(user_id: int):
    """
    Get the current user from the API.
    """

    connection = get_connection()
    try:
        await connection.user.get_user(user_id)
    except novus.errors.HTTPException:
        assert False, "User with ID %s doesn't exist" % user_id
    else:
        assert True


@pytest.mark.asyncio
async def test_get_current_user():
    """
    Get the current user from the API.
    """

    connection = get_connection()
    await connection.user.get_current_user()


@pytest.mark.parametrize("user_id", [69, 420])
@pytest.mark.asyncio
async def test_fail_get_user(user_id: int):
    """
    404 on a user.
    """

    connection = get_connection()
    try:
        user = await connection.user.get_user(user_id)
    except novus.errors.NotFound:
        assert True
    else:
        assert False, "User with ID %s does exist" % user.id
