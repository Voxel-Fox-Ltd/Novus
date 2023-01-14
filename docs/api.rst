.. currentmodule:: novus

API Reference
==============

Enums
------

.. class:: Locale

    .. list-table::
        :header-rows: 1

        * - Attribute
        * - ``indonesian``
        * - ``danish``
        * - ``german``
        * - ``uk_english``
        * - ``us_english``
        * - ``spanish``
        * - ``french``
        * - ``croatian``
        * - ``italian``
        * - ``lithuanian``
        * - ``hungarian``
        * - ``dutch``
        * - ``norwegian``
        * - ``polish``
        * - ``brazilian_portuguese``
        * - ``romanian``
        * - ``finnish``
        * - ``swedish``
        * - ``vietnamese``
        * - ``turkish``
        * - ``czech``
        * - ``greek``
        * - ``bulgarian``
        * - ``russian``
        * - ``ukrainian``
        * - ``hindi``
        * - ``thai``
        * - ``china_chinese``
        * - ``japanese``
        * - ``taiwan_chinese``
        * - ``korean``

Guild
~~~~~~

.. class:: enums.guild.NSFWLevel

    .. list-table::
        :header-rows: 1

        * - Attribute
        * - ``default``
        * - ``explicit``
        * - ``safe``
        * - ``age_restricted``

.. class:: enums.guild.PremiumTier

    .. list-table::
        :header-rows: 1

        * - Attribute
        * - ``none``
        * - ``tier_1``
        * - ``tier_2``
        * - ``tier_3``

.. class:: enums.guild.MFALevel

    .. list-table::
        :header-rows: 1

        * - Attribute
        * - ``none``
        * - ``elevated``

.. class:: enums.guild.ContentFilterLevel

    .. list-table::
        :header-rows: 1

        * - Attribute
        * - ``disabled``
        * - ``members_without_roles``
        * - ``all_members``

.. class:: enums.guild.VerificationLevel

    A representation of a guild's verification level.

    .. list-table::
        :header-rows: 1

        * - Attribute
          - Description
        * - ``none``
          - Unrestricted.
        * - ``low``
          - Must have a verified email on account.
        * - ``medium``
          - Must be registered on Discord for longer than 5 minutes.
        * - ``high``
          - Must be a member of the guild for longer than 10 minutes.
        * - ``very_high``
          - Must have a verified phone number.

.. class:: enums.guild.NotificationLevel

    .. list-table::
        :header-rows: 1

        * - Attribute
        * - ``all_messages``
        * - ``only_mentions``

Flags
------

.. class:: Permissions

    A permission set from Discord's API.

    .. list-table::
        :header-rows: 1

        * - Attribute
        * - ``create_instant_invite``
        * - ``kick_members``
        * - ``ban_members``
        * - ``administrator``
        * - ``manage_channels``
        * - ``manage_guild``
        * - ``add_reactions``
        * - ``view_audit_log``
        * - ``priority_speaker``
        * - ``stream``
        * - ``view_channel``
        * - ``send_messages``
        * - ``send_tts_messages``
        * - ``manage_messages``
        * - ``embed_links``
        * - ``attach_files``
        * - ``read_message_history``
        * - ``mention_everyone``
        * - ``use_external_emojis``
        * - ``view_guild_insights``
        * - ``connect``
        * - ``speak``
        * - ``mute_members``
        * - ``deafen_members``
        * - ``move_members``
        * - ``use_vad``
        * - ``change_nickname``
        * - ``manage_nicknames``
        * - ``manage_roles``
        * - ``manage_webhooks``
        * - ``manage_emojis_and_stickers``
        * - ``use_application_commands``
        * - ``request_to_speak``
        * - ``manage_events``
        * - ``manage_threads``
        * - ``create_public_threads``
        * - ``create_private_threads``
        * - ``use_external_stickers``
        * - ``send_messages_in_threads``
        * - ``use_embedded_activites``
        * - ``moderate_members``

Application
~~~~~~~~~~~~

.. class:: flags.application.ApplicationFlags

    The public flags for an application.

    .. list-table::
        :header-rows: 1

        * - Attribute
          - Description

        * - ``application_command_badge``
          - Indicates if an app has registered global application commands.
        * - ``embedded``
          - Indicates if an app is embedded within the Discord client
            (currently unavailable publicly).
        * - ``gateway_guild_members``
          - Intent required for bots in 100 or more servers to receive
            member-related events like ``guild_member_add``.
        * - ``gateway_guild_members_limited``
          - Intent required for bots in under 100 servers to receive
            member-related events like ``guild_member_add``.
        * - ``gateway_message_content``
          - Intent required for bots in 100 or more servers to receive message
            content.
        * - ``gateway_message_content_limited``
          - Intent required for bots in under 100 servers to receive message
            content.
        * - ``gateway_presence``
          - Intent required for bots in 100 or more servers to receive
            ``presence_update`` events.
        * - ``gateway_presence_limited``
          - Intent required for bots in under 100 servers to receive
            ``presence_update`` events.
        * - ``verification_pending_guild_limit``
          - Indicates unusual growth of an app that prevents verification.

Guild
~~~~~~

.. class:: flags.guild.SystemChannelFlags

    Flags for a system channel within a guild.

    .. list-table::
        :header-rows: 1

        * - Attribute
        * - ``suppress_join_notifications``
        * - ``suppress_premium_subscriptions``
        * - ``suppress_guild_reminder_notifications``
        * - ``suppress_join_notification_replies``

Utils
--------

Models
-------

.. autoclass:: Guild
    :members:

.. autoclass:: Sticker
    :members:

.. autoclass:: Emoji
    :members:

.. autoclass:: Role
    :members:

.. autoclass:: Asset
    :members:

.. autoclass:: WelcomeScreen
    :members:
