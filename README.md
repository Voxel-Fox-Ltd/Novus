# Novus

Novus is an asyncio Discord Python library, designed with scale in mind.

This is a work in progress, and is not yet ready for use.

## Overview

```py
TOKEN: str
GUILD_ID: int
USER_ID: int

# In Novus, a client is a secondary citizen, whereas the HTTP
# connection is who we love - you can just put down your token
# and pass that around the classes like me at a party
state = novus.api.HTTPConnection(TOKEN)

# As such, models now have classmethods using their state in order
# to get instances
guild = await novus.models.Guild.fetch(state, GUILD_ID)

# Things that logically inherit (such as Guild -> GuildMember)
# do also have helper methods
user1 = await guild.fetch_member(USER_ID)
user2 = await novus.models.GuildMember.fetch(state, GUILD_ID, USER_ID)
assert user1 == user2
```

## Tests

In an attempt to build a testing suite, I'm writing some test cases to go into the `tests/` directory so as to test each of the API methods. These use `pytest` with `pytest-asyncio`.

## Environment Variables

Novus uses a few environment variables to configure itself. These support
`.env` files via use of `python-dotenv`. These variables change how the library
works at a base level, such as changing routes.

- `NOVUS_API_URL`: The base URL for the API. Defaults to `https://discord.com/api/v10`
- `NOVUS_CDN_URL`: The base URL for the CDN. Defaults to `https://cdn.discordapp.com`
- `NOVUS_GATEWAY_URL`: The base URL for the gateway. Defaults to `wss://gateway.discord.gg/?v=10&encoding=json`

