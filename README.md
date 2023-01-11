# Novus

Novus is a newly-built Discord Python library, designed with you in mind.

This is a work in progress, and is not yet ready for use. Most of this document
will just be development notes, updates, and changelog.

## Environment Variables

Novus uses a few environment variables to configure itself. These support
`.env` files via use of `python-dotenv`. These variables change how the library
works at a base level, such as changing routes.

- `NOVUS_API_URL`: The base URL for the API. Defaults to `https://discord.com/api/v10`
- `NOVUS_CDN_URL`: The base URL for the CDN. Defaults to `https://cdn.discordapp.com`
- `NOVUS_GATEWAY_URL`: The base URL for the gateway. Defaults to `wss://gateway.discord.gg/?v=10&encoding=json`

