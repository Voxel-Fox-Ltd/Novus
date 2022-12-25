from typing import TypedDict


__all__ = (
    "LogCommandFunc",
)


class LogCommandFunc(TypedDict, total=False):
    command_name: str
    command_type: str
    guild_id: int
    channel_id: int
    user_id: int
    shard_id: int
    cluster: int
    user_locale: str
    guild_locale: str
