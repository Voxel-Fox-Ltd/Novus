from datetime import datetime, timezone
from typing import List


class TwitchStream:
    """
    A container class for parts of a Twitch stream.

    Attributes
    -----------
    id: :class:`str`
        The ID of the stream.
    user_id: :class:`str`
        The ID of the user who's streaming.
    user_login: :class:`str`
        The login name of the user who's streaming.
    user_name: :class:`str`
        The display name of the user who's streaming.
    game_id: :class:`str`
        The ID of the game that the user is playing.
    game_name: :class:`str`
        The name of the game that the user is playing.
    type: :class:`str`
        The stream status. Will only be "live".
    title: :class:`str`
        The title of the stream.
    viewer_count: :class:`int`
        The viewer count for the stream.
    started_at: :class:`datetime.datetime`
        An ISO 8601 timestamp for the stream's start time.
    language: :class:`str`
        The language code for the stream's language.
    thumbnail_url: :class:`str`
        A URL for the stream's thumbnail, with placeholder "{width}" and "{height}"
        format string placeholders.
    tag_ids: List[:class:`str`]
        The IDs of the tags assigned to the stream.
    is_mature: :class:`bool`
        Whether or not the stream is set to mature.
    """

    def __init__(self, *, data: dict):
        self.id: str = data['id']
        self.user_id: str = data['user_id']
        self.user_login: str = data['user_login']
        self.user_name: str = data['user_name']
        self.game_id: str = data['game_id']
        self.game_name: str = data['game_name']
        self.type: str = data['type']
        self.title: str = data['title']
        self.viewer_count: int = data['viewer_count']
        started_at = datetime.fromisoformat(data['started_at'][:-1])  # It has a Z on the end :(
        started_at.replace(tzinfo=timezone.utc)
        self.started_at: datetime = started_at
        self.language: str = data['language']
        self.thumbnail_url: str = data['thumbnail_url']
        self.tag_ids: List[str] = data['tag_ids']
        self.is_mature: bool = data['is_mature']
