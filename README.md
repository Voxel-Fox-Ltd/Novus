# Novus

Novus is an asyncio Discord Python library, designed with scale in mind.

This is a work in progress, and is not yet ready for use.

## Cache

As a general rule, when instances are created they will try to read from the state cache in order to fill their own attributes, but they will not write back into the cache. The exception is upgrading cached instances - some classes like `Message` receive a full member and user object when they are created. These will write back into the cache after they read from the cache instance.

All cache-adding operations should be handled by the dispatch class.

## Overview

```py
TOKEN: str
GUILD_ID: int
USER_ID: int

# In Novus, a client is a secondary citizen, whereas the HTTP
# connection is who we love - you can just put down your token
# and pass that around as necessary
state = novus.HTTPConnection(TOKEN)

# As such, models now have classmethods using their state in order
# to get instances
guild = await novus.Guild.fetch(state, GUILD_ID)

# Things that logically inherit (such as Guild -> GuildMember)
# do also have helper methods
user1 = await guild.fetch_member(USER_ID)
user2 = await novus.GuildMember.fetch(state, GUILD_ID, USER_ID)
assert user1 == user2
```

## Environment Variables

Novus uses a few environment variables to configure itself. These support
`.env` files via use of `python-dotenv`. These variables change how the library
works at a base level, such as changing routes.

- `NOVUS_API_URL`: The base URL for the API. Defaults to `https://discord.com/api/v10`
- `NOVUS_CDN_URL`: The base URL for the CDN. Defaults to `https://cdn.discordapp.com`
- `NOVUS_GATEWAY_URL`: The base URL for the gateway. Defaults to `wss://gateway.discord.gg/?v=10&encoding=json`
