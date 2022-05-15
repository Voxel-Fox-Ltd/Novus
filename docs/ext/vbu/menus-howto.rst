Menus Howto
##########################################

Menus are a pain to implement yourself in a lot of cases, so VoxelBotUtils does its best to handle those for you in an intuitive way.

Basic Example
------------------------------------------

Here's a heavily commented menu with a single option in it:

.. code-block:: python

    # Store our menu instance in a variable
    settings_menu = vbu.menus.Menu(

        # Our menu contains an option
        vbu.menus.Option(

            # This is what is displayed in the presented embed
            # Can be a function taking ctx, or a string
            display=lambda ctx: f"Favourite role (currently {ctx.bot.guild_settings[ctx.guild.id]['favourite_role']})",

            # This is what is shown on the button
            component_display="Favourite role",

            # This is a list of things that the user should be asked for
            converters=[

                # Make a converter instance
                vbu.menus.Converter(

                    # This is the message that's sent to the user
                    prompt="What role is your favourite?",

                    # The converter that we're using to convert the user's input
                    converter=discord.Role,

                    # The message to be sent if the converter times out
                    timeout_message="Timed out asking for old role removal.",
                ),
            ],

            # These are [async] functions that are called when the converters pass
            callback=vbu.menus.Menu.callbacks.set_table_column(vbu.menus.DataLocation.GUILD, "guild_settings", "remove_old_roles"),
            cache_callback=vbu.menus.Menu.callbacks.set_cache_from_key(vbu.menus.DataLocation.GUILD, "remove_old_roles"),
        ),
    )

Iterable Example
----------------------------------------------

Here's a basic initial menu that takes an iterable:

settings_menu = vbu.menus.MenuIterable(

    # The SQL to be run to get a list of arguments
    select_sql="""SELECT * FROM role_list WHERE guild_id=$1 AND key='BlacklistedVCRoles'""",

    # The arguments that should be passed as the select SQL arguments
    select_sql_args=lambda ctx: (ctx.guild.id,),

    # The SQL to be run to add the item to the database
    insert_sql="""INSERT INTO role_list (guild_id, role_id, key) VALUES ($1, $2, 'BlacklistedVCRoles')""",

    # The arguments that should be passed as the insert SQL arguments - data is the list of converted args
    insert_sql_args=lambda ctx, data: (ctx.guild.id, data[0].id,),

    # The SQL to be run to remove the item from the database
    delete_sql="""DELETE FROM role_list WHERE guild_id=$1 AND role_id=$2 AND key='BlacklistedVCRoles'""",

    # The arguments that should be passed as the delete SQL arguments - row is used here as the delete button
    # is generated when the menu is generated
    delete_sql_args=lambda ctx, row: (ctx.guild.id, row['role_id'],),

    # Converters for the menu, same as the other example
    converters=[
        vbu.menus.Converter(
            prompt="What role would you like to blacklist users getting VC points with?",
            converter=discord.Role,
        ),
    ],

    # The text to be shown in the menu
    row_text_display=lambda ctx, row: ctx.get_mentionable_role(row['role_id']).mention,

    # The text to be shown on the options' button
    row_component_display=lambda ctx, row: ctx.get_mentionable_role(row['role_id']).name,

    # The callback method to add a new item to the cache
    cache_callback=vbu.menus.Menu.callbacks.set_iterable_list_cache(vbu.menus.DataLocation.GUILD, "blacklisted_vc_roles"),

    # The callback method to remove an item from the cache
    cache_delete_callback=vbu.menus.Menu.callbacks.delete_iterable_list_cache(vbu.menus.DataLocation.GUILD, "blacklisted_vc_roles"),

    # The arguments that should be passed to the cache delete method
    cache_delete_args=lambda row: (row['role_id'],)
),
