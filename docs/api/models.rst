.. currentmodule:: novus

Models
--------------

Discord Models
~~~~~~~~~~~~~~

Models that are received from Discord. None of these should be created
yourself, but should all be given to you by library or API methods.

.. autoclass:: Activity
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: Application
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: Asset
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: Attachment
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: AuditLog
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: AuditLogContainer
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: AuditLogEntry
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: AutoModerationAction
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: AutoModerationRule
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: AutoModerationTriggerMetadata
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: BaseGuild
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: Channel
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: Emoji
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: ForumTag
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: Guild
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: GuildBan
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: GuildMember
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: GuildPreview
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: Invite
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: Message
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: PartialEmoji
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: PartialGuild
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: Reaction
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: Role
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: ScheduledEvent
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: StageInstance
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: Sticker
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: Team
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: TeamMember
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: ThreadMember
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: User
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: VoiceState
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: Webhook
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: WebhookMessage
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: WelcomeScreen
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: WelcomeScreenChannel
    :members:
    :inherited-members:
    :no-special-members:

User-Creatable Models
~~~~~~~~~~~~~~~~~~~~~

Models that itneract with Discord. These may be user-created, but some can still
be returned by the API on certain methods.

.. autoclass:: AllowedMentions
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: Embed
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: File
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: Object
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: PermissionOverwrite
    :members:
    :inherited-members:
    :no-special-members:

Components
~~~~~~~~~~

Models that relate to message components.

.. autoclass:: ActionRow
    :members:
    :special-members: __setitem__, __getitem__, __iter__
    :inherited-members:
    :no-special-members:
.. autoclass:: Button
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: StringSelectMenu
    :members:
    :special-members: __setitem__, __getitem__, __iter__
    :inherited-members:
    :no-special-members:
.. autoclass:: ChannelSelectMenu
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: RoleSelectMenu
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: UserSelectMenu
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: MentionableSelectMenu
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: SelectOption
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: TextInput
    :members:
    :inherited-members:
    :no-special-members:

Application Commands
~~~~~~~~~~~~~~~~~~~~

Models that relate to application commands.

.. autoclass:: PartialApplicationCommand
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: ApplicationCommand
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: ApplicationCommandChoice
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: ApplicationCommandOption
    :members:
    :inherited-members:
    :no-special-members:

Interactions
~~~~~~~~~~~~

Models that relate to interactions.

.. autoclass:: Interaction
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: GuildInteraction
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: MessageInteraction
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: ContextComandData
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: ApplicationCommandData
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: MessageComponentData
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: ModalSubmitData
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: InteractionData
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: InteractionOption
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: InteractionResolved
    :members:
    :inherited-members:
    :no-special-members:
.. .. autoclass:: InteractionWebhook
