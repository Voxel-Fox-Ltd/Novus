from discord.ext import commands


class ConfigNotSet(commands.DisabledCommand):
    """
    This is a subclass of :class:`discord.ext.commands.DisabledCommand` raised exclusively by the
    :func:`is_config_set<voxelbotutils.checks.is_config_set>` check. For normal users, this should just say
    that the command is disabled.
    """


def is_config_set(*config_keys):
    """
    Checks that your config has been set given the keys for the item. Items are run as `__getitem__`s
    for the following item. So for a config where you want to check that `config["api_keys"]["example"]`
    has been set, you would write your check as `is_config_set("api_keys", "example")`.

    Raises:
        ConfigNotSet: If the config item hasn't been set for the bot.
    """

    def predicate(ctx: commands.Context):
        working_config = ctx.bot.config
        try:
            for key in config_keys:
                working_config = working_config[key]
        except (KeyError, TypeError):
            raise ConfigNotSet()
        if not working_config:
            ctx.bot.logger.warning(f"No config is set for {'.'.join(config_keys)}")
            raise ConfigNotSet()
        return True
    return commands.check(predicate)
