.. currentmodule:: novus

Flags
------

.. class:: Intents

    .. py:attribute:: guilds
    .. py:attribute:: guild_members
    .. py:attribute:: guild_moderation
    .. py:attribute:: guild_emojis_and_stickers
    .. py:attribute:: guild_integrations
    .. py:attribute:: guild_webhooks
    .. py:attribute:: guild_invites
    .. py:attribute:: guild_voice_states
    .. py:attribute:: guild_presences
    .. py:attribute:: guild_messages
    .. py:attribute:: guild_message_reactions
    .. py:attribute:: guild_message_typing
    .. py:attribute:: direct_messages
    .. py:attribute:: direct_message_reactions
    .. py:attribute:: direct_message_typing
    .. py:attribute:: message_content
    .. py:attribute:: guild_scheduled_events
    .. py:attribute:: auto_moderation_configuration
    .. py:attribute:: auto_moderation_execution

.. class:: ApplicationFlags

    The public flags for an application.

    .. py:attribute:: application_command_badge

        Indicates if an app has registered global application commands.

    .. py:attribute:: embedded

        Indicates if an app is embedded within the Discord client
        (currently unavailable publicly).

    .. py:attribute:: gateway_guild_members

        Intent required for bots in 100 or more servers to receive
        member-related events like ``GUILD_MEMBER_ADD``.

    .. py:attribute:: gateway_guild_members_limited

        Intent required for bots in under 100 servers to receive
        member-related events like ``GUILD_MEMBER_ADD``.

    .. py:attribute:: gateway_message_content

        Intent required for bots in 100 or more servers to receive message
        content.

    .. py:attribute:: gateway_message_content_limited

        Intent required for bots in under 100 servers to receive message
        content.

    .. py:attribute:: gateway_presence

        Intent required for bots in 100 or more servers to receive
        ``PRESENCE_UPDATE`` events.

    .. py:attribute:: gateway_presence_limited

        Intent required for bots in under 100 servers to receive
        ``PRESENCE_UPDATE`` events.

    .. py:attribute:: verification_pending_guild_limit

        Indicates unusual growth of an app that prevents verification.

.. class:: MessageFlags

    .. py:attribute:: suppress_join_notifications
    .. py:attribute:: suppress_premium_subscriptions
    .. py:attribute:: suppress_guild_reminder_notifications
    .. py:attribute:: suppress_join_notification_replies

.. class:: SystemChannelFlags

    Flags for a system channel within a guild.

    .. py:attribute:: suppress_join_notifications
    .. py:attribute:: suppress_premium_subscriptions
    .. py:attribute:: suppress_guild_reminder_notifications
    .. py:attribute:: suppress_join_notification_replies

.. class:: Permissions

    A permission set from Discord's API.

    .. py:attribute:: create_instant_invite
    .. py:attribute:: kick_members
    .. py:attribute:: ban_members
    .. py:attribute:: administrator
    .. py:attribute:: manage_channels
    .. py:attribute:: manage_guild
    .. py:attribute:: add_reactions
    .. py:attribute:: view_audit_log
    .. py:attribute:: priority_speaker
    .. py:attribute:: stream
    .. py:attribute:: view_channel
    .. py:attribute:: send_messages
    .. py:attribute:: send_tts_messages
    .. py:attribute:: manage_messages
    .. py:attribute:: embed_links
    .. py:attribute:: attach_files
    .. py:attribute:: read_message_history
    .. py:attribute:: mention_everyone
    .. py:attribute:: use_external_emojis
    .. py:attribute:: view_guild_insights
    .. py:attribute:: connect
    .. py:attribute:: speak
    .. py:attribute:: mute_members
    .. py:attribute:: deafen_members
    .. py:attribute:: move_members
    .. py:attribute:: use_vad
    .. py:attribute:: change_nickname
    .. py:attribute:: manage_nicknames
    .. py:attribute:: manage_roles
    .. py:attribute:: manage_webhooks
    .. py:attribute:: manage_emojis_and_stickers
    .. py:attribute:: use_application_commands
    .. py:attribute:: request_to_speak
    .. py:attribute:: manage_events
    .. py:attribute:: manage_threads
    .. py:attribute:: create_public_threads
    .. py:attribute:: create_private_threads
    .. py:attribute:: use_external_stickers
    .. py:attribute:: send_messages_in_threads
    .. py:attribute:: use_embedded_activites
    .. py:attribute:: moderate_members

.. class:: UserFlags

    .. py:attribute:: staff
    .. py:attribute:: partner
    .. py:attribute:: hypesquad
    .. py:attribute:: bug_hunter_level_1
    .. py:attribute:: hypesquad_house_bravery
    .. py:attribute:: hypesquad_house_brilliance
    .. py:attribute:: hypesquad_house_balance
    .. py:attribute:: premium_early_supporter
    .. py:attribute:: team_pseudo_user
    .. py:attribute:: bug_hunter_level_2
    .. py:attribute:: verified_bot
    .. py:attribute:: verified_developer
    .. py:attribute:: certified_moderator
    .. py:attribute:: bot_http_interactions
    .. py:attribute:: active_developer

.. class:: AuditLogEntryType

    .. py:attribute:: guild_update
    .. py:attribute:: channel_create
    .. py:attribute:: channel_update
    .. py:attribute:: channel_delete
    .. py:attribute:: channel_overwrite_create
    .. py:attribute:: channel_overwrite_update
    .. py:attribute:: channel_overwrite_delete
    .. py:attribute:: member_kick
    .. py:attribute:: member_prune
    .. py:attribute:: member_ban_add
    .. py:attribute:: member_ban_remove
    .. py:attribute:: member_update
    .. py:attribute:: member_role_update
    .. py:attribute:: member_move
    .. py:attribute:: member_disconnect
    .. py:attribute:: bot_add
    .. py:attribute:: role_create
    .. py:attribute:: role_update
    .. py:attribute:: role_delete
    .. py:attribute:: invite_create
    .. py:attribute:: invite_update
    .. py:attribute:: invite_delete
    .. py:attribute:: webhook_create
    .. py:attribute:: webhook_update
    .. py:attribute:: webhook_delete
    .. py:attribute:: emoji_create
    .. py:attribute:: emoji_update
    .. py:attribute:: emoji_delete
    .. py:attribute:: message_delete
    .. py:attribute:: message_bulk_delete
    .. py:attribute:: message_pin
    .. py:attribute:: message_unpin
    .. py:attribute:: integration_create
    .. py:attribute:: integration_update
    .. py:attribute:: integration_delete
    .. py:attribute:: stage_instance_create
    .. py:attribute:: stage_instance_update
    .. py:attribute:: stage_instance_delete
    .. py:attribute:: sticker_create
    .. py:attribute:: sticker_update
    .. py:attribute:: sticker_delete
    .. py:attribute:: guild_scheduled_event_create
    .. py:attribute:: guild_scheduled_event_update
    .. py:attribute:: guild_scheduled_event_delete
    .. py:attribute:: thread_create
    .. py:attribute:: thread_update
    .. py:attribute:: thread_delete
    .. py:attribute:: application_command_permission_update
    .. py:attribute:: auto_moderation_rule_create
    .. py:attribute:: auto_moderation_rule_update
    .. py:attribute:: auto_moderation_rule_delete
    .. py:attribute:: auto_moderation_block_message
    .. py:attribute:: auto_moderation_flag_to_channel
    .. py:attribute:: auto_moderation_user_communication_disabled
