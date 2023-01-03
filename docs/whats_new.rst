.. currentmodule:: discord

.. |commands| replace:: [:ref:`ext.commands <discord_ext_commands>`]
.. |tasks| replace:: [:ref:`ext.tasks <discord_ext_tasks>`]

.. _whats_new:

Changelog
============

This page keeps a detailed human friendly rendering of what's new and changed
in specific versions.

.. _vp0_2_4:

v0.2.4
--------

New Features
~~~~~~~~~~~~~~~~~~~~~~

* Add a ``message`` attribute to the interaction subclasses for typing.
* Add new attributes to some of the raw classes:
    * :attr:`discord.RawReactionActionEvent.cached_message`
    * :attr:`discord.RawReactionClearEvent.cached_message`
    * :attr:`discord.RawReactionClearEmoji.cached_message`
* [commands] Add :attr:`commands.ApplicationCommandMeta.guild_ids`.
* [vbu] Add ``cookie_encryption_key`` to bot config.
* [vbu] Add parameters to :func:`vbu.checks.bot_is_ready`.
* [vbu] Add :func:`vbu.Bot.log_command` function.
* [vbu] Add :func:`vbu.checks.interaction_filter` function.

Removed Features
~~~~~~~~~~~~~~~~~~~~~~

* [vbu] Remove ``Bot.get_invite_link``.
* [vbu] Remove ``oauth`` from the config.

.. _vp0_2_1:

v0.2.1
--------

New Features
~~~~~~~~~~~~~~~~~~~~~~

* [vbu] Add :func:`i18n` wrapper.

.. _vp0_2_0:

v0.2.0
--------

This version includes breaking changes around things that are cached/retrieved
from cache in regards to slash commands, interactions, and HTTP only clients.

This version also includes :attr:`Intents.message_content` explicitly.

New Features
~~~~~~~~~~~~~~~~~~~~~~

* Add :func:`Guild.create_forum_channel`.
* Add :func:`AllowedMentions.only`.
* Add :attr:`Interaction.app_permissions`.
* Add :attr:`Member.role_ids`.
* Add :attr:`Intents.message_content`.
* Add support for ``gateway_resume_url``.
* [vbu] Add :func:`vbu.component_id_check`.
* [vbu] Add :attr:`vbu.Bot.is_interactions_only`.

Changed Features
~~~~~~~~~~~~~~~~~~~~~~

* :attr:`Interaction.guild` can now be an instance of :class:`Object`.
    * :attr:`Member.guild` will return an empty list if the guild is a :class:`Object`.
    Use :attr:`Member.role_ids` instead.
* [commands] :func:`commands.bot_has_permissions` will now use :attr:`Interaction.app_permissions`
if available.
* [vbu] Owners will only get DMs for uncaught errors if the shard count is lower than 50.
* [vbu] :func:`vbu.Bot.startup` will now be run when the interactions webserver is started.
* [vbu] ``default_prefix`` can now be missing entirely from the config.


Removed Features
~~~~~~~~~~~~~~~~~~~~~~

* [vbu] Removed ``vbu.command``,  ``vbu.Command``, ``vbu.group``, and ``vbu.Group``.
* [vbu] Remove ``vbu.Redis.lock_manager`` and ``aioredlock`` requirement.

.. _vp0_1_4:

v0.1.4
--------

New Features
~~~~~~~~~~~~~~~~~~~~~~

* [vbu] Add ``shard`` command to owner only cog.
* [vbu] Add :attr:`ext.vbu.Bot.cluster`.
* [vbu] Add cluster and shard IDs to the statsd logger.

Changed Features
~~~~~~~~~~~~~~~~~~~

* [vbu] ``ev`` command runs invoked via the ``redis`` command will no longer try and add a reaction.
* [vbu] The statsd logger for guild count now runs per cluster for more accurate guild count measurement.

Bugs Fixed
~~~~~~~~~~~~~~~~~~~~~~

* Fixed not supporting ``None`` command prefixes.
* Fix ``InteractionResolved.channels`` not parsing properly.
* Fix channel kwarg not being optional for ``discord.GuildChannel``.
* [vbu] Fix package data in the setup files.

.. _vp0_1_3:

v0.1.3
--------

New Features
~~~~~~~~~~~~~~~~~~~~~~

* Add :class:`Locale`.

Bugs Fixed
~~~~~~~~~~~~~~~~~~~~~~

* Fixed an error in select menus merged in from the testing branch.

.. _vp0_0_8:

.. _vp0_1_0:
.. _vp0_1_1:
.. _vp0_1_2:

v0.1.2
--------

The *only* change for this release (and .0 and .1) is that VoxelBotUtils is now native to this package. You can install with ``pip install novus[vbu]``.

.. _vp0_0_8:

v0.0.8
--------

New Features
~~~~~~~~~~~~~~~~~~

* Add ``check_scopes`` parameter to :func:`ext.commands.is_slash_command()`.
* Add support for :class:`ForumChannel`.
* Add support for :class:`ui.UserSelectMenu`, :class:`ui.RoleSelectMenu`, :class:`ui.MentionableSelectMenu`, and :class:`ui.ChannelSelectMenu`.
* Add support for text in voice (voice channels are now sendable).
* Add support for NSFW VCs.

Bugs Fixed
~~~~~~~~~~~~~~~~~~~~

* Fix default permissions in application command meta.
* Fix error in context commands that didn't allow for unions.

.. _vp0_0_7:

v0.0.7
--------

New Features
~~~~~~~~~~~~~~~~~~

* Add support for attachment slash options.
    * Add :attr:`ApplicationCommandOptionType.attachment`.
    * Add :attr:`InteractionResolved.attachments`.
    * Add :attr:`Attachment.ephemeral`.

Changed Features
~~~~~~~~~~~~~~~~~~~

* Many options from slash commands are now gathered from the resolved data.
* Change reprs for components.

Bugs Fixed
~~~~~~~~~~~~~~~~~~~~

* Fix `Bot.get_slash_context()` for subcommands without options.
* Fix member converter.
* Fix permissions checks for interactions.
* Add localisations to the json output for application command options.

.. _vp0_0_6:

v0.0.6
--------

New Features
~~~~~~~~~~~~~~~~~~

* Add ``guild_locale``, ``user_locale``, and ``locale`` to :class:`Interaction` and the two context objects.
* Add :attr:`ApplicationCommand.default_member_permissions` and :attr:`ApplicationCommand.dm_permissions`.
* Add new methods for dealing with application commands.
    * :func:`Client.fetch_global_application_commands`
    * :func:`Client.fetch_global_application_command`
    * :func:`Client.create_global_application_command`
    * :func:`Client.edit_global_application_command`
    * :func:`Client.delete_global_application_command`
    * :func:`Client.bulk_create_global_application_commands`
    * :func:`Guild.fetch_application_commands`
    * :func:`Guild.fetch_application_command`
    * :func:`Guild.create_application_command`
    * :func:`Guild.edit_application_command`
    * :func:`Guild.delete_application_command`
    * :func:`Guild.bulk_create_application_commands`
* Add :func:`InteractedComponent.get_component`
* Add support for guild scheduled events.
    * Add :class:`GuildScheduledEvent`.
    * Add :func:`Guild.create_scheduled_event`.
    * Add :func:`Guild.fetch_scheduled_event`.
    * Add :func:`Guild.fetch_scheduled_events`.
* Add :func:`commands.Command.application_command_meta`.
    * This contains meta info for the command that should be converted to slash commands.
* Add support for :class:`ui.Modal`s and :class:`ui.InputText` components.
* Add :attr:`ApplicationCommandOption.max_value` and :attr:`ApplicationCommandOption.min_value`.

Changed Features
~~~~~~~~~~~~~~~~~~~

* Change all args in :class:`ApplicationCommandOptionChoice`, :class:`ApplicationCommandOption`, and :class:`ApplicationCommand`'s inits to be kwargs instead of positional args.

Bugs Fixed
~~~~~~~~~~~~~~~~~~~~

* Fix ``moderate_members`` not being included in ``Permissions.all``.
* Fix positional arguments not being passed properly to commands when invoked via slash command.

Removed Features
~~~~~~~~~~~~~~~~~~~~

* Removed ``Command.add_slash_command`` attr and kwarg. This has been replcaed by :attr:`commands.Command.application_command_meta`.

.. _vp0_0_5:

v0.0.5
--------

New Features
~~~~~~~~~~~~~~~~~~

* Added support for :class:`modals <ui.Modal>`.
* Add :attr:`Interaction.components`.
* Add :class:`ApplicationCommandInteractionDataOption`.
* Add :class:`ui.InteractableComponent`.
* Add support for role icons.
    * Add :attr:`Role.icon`.
    * Add :attr:`Role.unicode_emoji`.
    * Add ``icon`` to :func:`Role.edit`.
* Add support for member timeouts.
    * Add :func:`Member.disable_communication_until`.
    * Add :func:`Member.disable_communication_for`.
    * Add :func:`Member.enable_communication`.
    * Add ``communication_disabled_until`` to :func:`Member.edit`.

Changed Features
~~~~~~~~~~~~~~~~~~~

* :ref:`Autocomplete is now documented <on_autocomplete_interaction>`.
* Changed the types of :attr:`Interaction.values` and :attr:`Interaction.options`.
* Change error for :class:`ui.Button` invalid type to :class:`InvalidArgument`.

Bugs Fixed
~~~~~~~~~~~~~~~~~~

* Fixed typing of :func:`Member.move_to`.
* Add proper exports for ``discord.ui``.

.. _vp0_0_4:

v0.0.4
--------

New Features
~~~~~~~~~~~~~~~~~~

* Add :attr:`ApplicationCommandOption.channel_types`.
* Add ``files`` parameter to :func:`InteractionResponse.send`.
* Add support for autocomplete.
    * Add :attr:`ApplicationCommandOption.autocomplete`.
    * Add :attr:`Interaction.options`.
    * Add :func:`on_autocomplete_interaction` and :func:`commands.Bot.on_autocomplete` events.
* Add ``ignore_spaces`` kwarg to ``Bot.get_command``.
* Add :func:`MessageComponents.add_number_buttons`.
* Add :func:`Button.confirm` and :func:`Button.cancel`.
* Add ``options`` kwarg to `ApplicationCommand`.
* Add :attr:`Interaction.command_name`.
* Add :attr:`ApplicationCommandOption.channel_types`.
* Add ``@is_slash_command`` check.

Changed Features
~~~~~~~~~~~~~~~~~~~

* Change default response type to nothing.

Bugs Fixed
~~~~~~~~~~~~~~~~~~

* Fix adding slash commands which we say not to add.
* Fix component deferring.
* Fix popping non-existent keys.
* Re-add options to ApplicationCommandOption export.
* Fix reccursion error in interactionresolved.

.. _vp0_0_3:

v0.0.3
--------

Bugs Fixed
~~~~~~~~~~~~~~~~~~

* Fix indentation on getting application command arg type.
* Fix application command ``required`` property not being set properly.
* Add import for application commands to ``discord`` top-level package.
* Filter context menu commands out of the default help menu implementation.

Changed Features
~~~~~~~~~~~~~~~~~~

* Removed Danny's ``on_socket_event_type`` to be replaced with :func:`on_socket_event`.
* The ``newcog`` cmd argument will now use VoxelBotUtils if it's installed.
* A list of :class:`commands.Command` objects are now allowed to be passed into :func:`ext.commands.Bot.register_application_commands`.

New Features
~~~~~~~~~~~~~~~~~~

* Add :class:`InteractionResolved` class, as a new attribute in :class:`Interaction`.
* Added :func:`commands.context_command` decorator.
* Added :func:`utils.naive_dt`.
* Add :func:`Embed.remove_image` and :func:`Embed.remove_thumbnail`.
* Add :class:`WelcomeScreen`.
* Add :func:`ext.commands.get_interaction_route_table`.

.. _vp0_0_2:

v0.0.2
--------

New Features
~~~~~~~~~~~~~~~~~~

* Add :func:`defer decorator<commands.defer>` for application commands.
* Add :func:`InteractionResonse.defer_update`.
* Add ``allowed_mentions`` to :func:`InteractionReponse.edit_message`.
* Add ``response_type`` kwarg to :func:`utils.oauth_url`.

Bugs Fixed
~~~~~~~~~~~~~~~~~~

* Fix action rows not being parsed correctly.
* Fixed ``ephemeral`` kwarg in :func:`commands.SlashContext.send` and :func:`commands.SlashContext.defer`.
* Fix slash commands not working with cooldowns.


.. _vp0_0_1:

v0.0.1
--------

The new and changed features described in this section refer to changes from Rapptz's original Discord.py repo. You can see :ref:`a whole list of changes <migrating_2_0>` here, but this section will go over the main ones.

Breaking Changes
~~~~~~~~~~~~~~~~~~

* ``TextChannel.get_partial_message`` is now pos-only
* ``permissions_for`` is now pos-only
* ``GroupChannel.owner`` is now Optional
* ``edit`` methods now only accept None if it actually means something (e.g. clearing it)
* Separate ``on_member_update`` and ``on_presence_update``
    * The new event ``on_presence_update`` is now called when status/activity is changed.
    * ``on_member_update`` will now no longer have status/activity changes.
* ``afk`` parameter in ``Client.change_presence`` is removed
* The undocumented private ``on_socket_response`` event got removed.
    * Consider using the newer documented ``on_socket_event_type`` event instead.
* Using ``on_socket_raw_receive`` and ``on_socket_raw_send`` are now opt-in via enable_debug_events toggle.
* ``on_socket_raw_receive`` is now only dispatched after decompressing the payload.
* All ``get_`` lookup functions now use positional-only parameters for the id parameter.
* ``User.avatar`` now returns ``None`` if the user did not upload an avatar.
    * Use ``User.display_avatar`` to get the avatar and fallback to the default avatar to go back to the old behaviour.

New Features
~~~~~~~~~~~~~~~~

* Message components are now sendable using the :ref:`bot UI kit <discord_ui_kit>`.
* Slash commands are now processed as message commands if sent through the gateway.
* :func:`Client.register_application_commands` will register all of your bot's loaded commands as application commands.
* Threads as a whole (thanks to Danny).
* Type hinting for a vast majority of the library (thanks to Danny).

.. _vp_rapptz:

Original
--------

Everything at this point and before is forked directly from `Rapptz's Discord.py library <https://github.com/Rapptz/discord.py>`_. The changelogs from before that point (and thus before the existance of this library) have been removed.


