import typing

import discord


class OauthGuild(object):
    """
    A guild object from an oauth integration.

    Attributes:
        id (int): The ID of the guild.
        name (str): The name of the guild.
        icon (discord.Asset): The guild's icon.
        owner_id (int): The ID of the owner for the guild.
            This will either be the ID of the authenticated user or `0`.
        features (typing.List[str]): A list of features that the guild has.sa
    """

    def __init__(self, bot, guild_data, user):
        self.id: int = int(guild_data.get("id"))
        self.name: str = guild_data.get("name")
        self._icon: typing.Optional[str] = guild_data.get("icon")
        self.owner_id: int = user.id if guild_data.get("owner") else 0
        self.features: typing.List[str] = guild_data.get("features")
        self._bot: discord.Client = bot

    @property
    def icon(self) -> typing.Optional[discord.Asset]:
        """Optional[:class:`Asset`]: Returns the guild's icon asset, if available."""
        if self._icon is None:
            return None
        return discord.Asset._from_guild_icon(None, self.id, self._icon)

    async def fetch_guild(self, bot=None) -> typing.Optional[discord.Guild]:
        """
        Fetch the original :class:`discord.Guild` object from the API using the authentication from the
        bot given.

        Args:
            bot: The bot object that you want to use to fetch the guild.

        Returns:
            typing.Optional[discord.Guild]: The guild instance.
        """

        bot = bot or self._bot
        try:
            return await bot.fetch_guild(self.id)
        except discord.HTTPException:
            return None


class OauthUser(object):
    """
    A user object from an oauth integration.

    Attributes:
        id (int): The ID of the user.
        username (str): The user's username.
        avatar (discord.Asset): The user's avatar asset.
        discriminator (str): The user's discrimiator.
        public_flags (discord.PublicUserFlags): The user's public flags.
        locale (str): The locale of the user.
        mfa_enabled (bool): Whether or not the user has MFA enabled.
    """

    def __init__(self, user_data):
        self.id: int = int(user_data['id'])
        self.username: str = user_data.get("username")
        self._avatar: str = user_data.get("avatar")
        self.discriminator: str = user_data.get("discriminator")
        self.public_flags: discord.PublicUserFlags = discord.PublicUserFlags._from_value(user_data.get("public_flags", 0))
        self.locale: str = user_data.get("locale")
        self.mfa_enabled: bool = user_data.get("mfa_enabled", False)

    @property
    def avatar(self) -> typing.Optional[discord.Asset]:
        """Optional[:class:`Asset`]: Returns the guild's icon asset, if available."""
        if self._avatar is None:
            return None
        return discord.Asset._from_avatar(None, self.id, self._avatar)


class OauthMember(OauthUser):
    """
    A user object from an oauth integration.

    Attributes:
        id (int): The ID of the user.
        username (str): The user's username.
        avatar (str): The user's avatar hash.
        avatar_url (discord.Asset): The user's avatar.
        discriminator (str): The user's discrimiator.
        public_flags (discord.PublicUserFlags): The user's public flags.
        locale (str): The locale of the user.
        mfa_enabled (bool): Whether or not the user has MFA enabled.
        guild (OauthGuild): The guild object that this member is a part of.
        guild_permissions (discord.Permissions): The permissions that this member has on the guild.
    """

    def __init__(self, bot, guild_data, user_data):
        super().__init__(user_data)
        self.guild: OauthGuild = OauthGuild(bot, guild_data, self)
        self.guild_permissions: discord.Permissions = discord.Permissions(guild_data['permissions'])
