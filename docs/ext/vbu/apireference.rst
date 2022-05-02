API Reference
================================

Event Reference
---------------------------------------

.. function:: twitch_stream(data)

   :param data: The Twitch stream that went live.
   :type data: :class:`voxelbotutils.TwitchStream`

   Pinged when a Twitch stream goes live. This only occurs if valid Twitch
   authentication is set inside of the config.

Utils
---------------------------------------

Bot
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.MinimalBot
   :exclude-members: close, invoke, login, start, __init__
   :no-inherited-members:

.. autoclass:: voxelbotutils.Bot
   :exclude-members: close, invoke, login, start
   :no-inherited-members:

Cog
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.Cog
   :no-special-members:

Context
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.Context
   :no-special-members:

AbstractMentionable
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.AbstractMentionable

DatabaseWrapper
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.DatabaseWrapper
   :no-special-members:

DatabaseTransaction
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.DatabaseTransaction
   :no-special-members:

RedisConnection
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.RedisConnection
   :no-special-members:

StatsdConnection
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.StatsdConnection
   :no-special-members:

Embed
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.Embed
   :exclude-members: use_random_color

Paginator
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.Paginator

TimeValue
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.TimeValue

TwitchStream
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.TwitchStream

component_check
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: voxelbotutils.component_check

format
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: voxelbotutils.format

translation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: voxelbotutils.translation

Checks
-------------------------------------------------

checks.is_config_set
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: voxelbotutils.checks.is_config_set

checks.meta_command
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: voxelbotutils.checks.meta_command

checks.bot_is_ready
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: voxelbotutils.checks.bot_is_ready

checks.is_bot_support
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: voxelbotutils.checks.is_bot_support

checks.is_voter
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: voxelbotutils.checks.is_voter

checks.is_upgrade_chat_subscriber
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: voxelbotutils.checks.is_upgrade_chat_subscriber

checks.is_upgrade_chat_purchaser
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: voxelbotutils.checks.is_upgrade_chat_purchaser

Converters
----------------------------------------------------

converters.UserID
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.converters.UserID
   :no-special-members:
   :no-members:

converters.ChannelID
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.converters.ChannelID
   :no-special-members:
   :no-members:

converters.BooleanConverter
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.converters.BooleanConverter
   :no-special-members:
   :no-members:

converters.ColourConverter
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.converters.ColourConverter
   :no-special-members:
   :no-members:

converters.FilteredUser
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.converters.FilteredUser
   :no-special-members:
   :no-members:

converters.FilteredMember
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.converters.FilteredMember
   :no-special-members:
   :no-members:

Menus
------------------------------------------------------------

Menus also have :ref:`their own page<menus howto>` for a basic integration guide.

menus.DataLocation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.menus.DataLocation

menus.MenuCallbacks
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.menus.MenuCallbacks

menus.Check
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.menus.Check

menus.ModalCheck
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.menus.ModalCheck

menus.CheckFailureAction
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.menus.CheckFailureAction

menus.Converter
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.menus.Converter

menus.Option
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.menus.Option

menus.Menu
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.menus.Menu

menus.MenuIterable
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.menus.MenuIterable


Errors
-----------------------------------------------

errors.ConfigNotSet
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoexception:: voxelbotutils.errors.ConfigNotSet

errors.InvokedMetaCommand
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoexception:: voxelbotutils.errors.InvokedMetaCommand

errors.BotNotReady
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoexception:: voxelbotutils.errors.BotNotReady

errors.IsNotVoter
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoexception:: voxelbotutils.errors.IsNotVoter

errors.NotBotSupport
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoexception:: voxelbotutils.errors.NotBotSupport
    :no-special-members:

errors.MissingRequiredArgumentString
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoexception:: voxelbotutils.errors.MissingRequiredArgumentString
    :no-special-members:

errors.InvalidTimeDuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoexception:: voxelbotutils.errors.InvalidTimeDuration
    :no-special-members:

errors.IsNotUpgradeChatPurchaser
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoexception:: voxelbotutils.errors.IsNotUpgradeChatPurchaser
   :no-special-members:

errors.IsNotUpgradeChatSubscriber
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoexception:: voxelbotutils.errors.IsNotUpgradeChatSubscriber
   :no-special-members:

Websites
---------------------------------------------------

web.OauthGuild
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.web.OauthGuild
   :no-special-members:

web.OauthUser
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.web.OauthUser
   :no-special-members:

web.OauthMember
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: voxelbotutils.web.OauthMember
   :no-special-members:

web.add_discord_arguments
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: voxelbotutils.web.add_discord_arguments

web.get_avatar_url
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: voxelbotutils.web.get_avatar_url

web.requires_login
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: voxelbotutils.web.requires_login

   .. seealso:: :func:`voxelbotutils.web.is_logged_in`

web.is_logged_in
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: voxelbotutils.web.is_logged_in

   .. seealso:: :func:`voxelbotutils.web.requires_login`

web.get_discord_login_url
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: voxelbotutils.web.get_discord_login_url

web.process_discord_login
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: voxelbotutils.web.process_discord_login

web.get_user_info_from_session
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: voxelbotutils.web.get_user_info_from_session

web.get_access_token_from_session
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: voxelbotutils.web.get_access_token_from_session

web.get_user_guilds_from_session
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: voxelbotutils.web.get_user_guilds_from_session

web.add_user_to_guild_from_session
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: voxelbotutils.web.add_user_to_guild_from_session
