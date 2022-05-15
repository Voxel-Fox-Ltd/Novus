.. raw:: html

    <style>
        dt, dd {
            margin-bottom: 0 !important;
        }
   </style>

Getting Started
===========================================

Command Line
---------------------------------------

There's a few available things from the commandline (CMD) that you can do with VoxelBotUtils. You can run the module either as :code:`python3 -m voxelbotutils`, or it's registered as a plain :code:`voxelbotutils` to your PATH on install that you can run instead.

.. _cmd_create_config:

* :code:`$ voxelbotutils create-config`

   * :code:`bot` - this creates a set of bot config files
   * :code:`website` - this creates a set of website config files
   * :code:`all` - this creates a set of all available config files

.. _cmd_run_bot:

* :code:`$ voxelbotutils run-bot`

   * :code:`[bot_directory]` - the directory that the bot files are located in; defaults to `.`
   * :code:`[config_file]` - the path to the config file to use; defaults to `config/config.toml`
   * :code:`--min [amount]` - the minimum shard ID for this instance
   * :code:`--max [amount]` - the maximum shard ID for this instance
   * :code:`--shardcount [amount]` - the number of shards that the bot should identify as (not the number of shards for this instance)
   * :code:`--loglevel [level]` - the :code:`logging.Logger` loglevel that you want to start the bot with

.. _cmd_run_interactions:

* :code:`$ voxelbotutils run-interactions`

   * :code:`[bot_directory]` - the directory that the bot files are located in; defaults to `.`
   * :code:`[config_file]` - the path to the config file to use; defaults to `config/config.toml`
   * :code:`--host` - the host that you want to run the webserver with.
   * :code:`--port` - the port that you want to run the webserver on.
   * :code:`--path` - the path that the route should be added as; defaults to `/interactions`
   * :code:`--connect` - if you want to connect your bot to the gateway as well as running the interactions webserver; shards will be automatically calculated and intents will be set to none.
   * :code:`--loglevel [level]` - the :code:`logging.Logger` loglevel that you want to start the bot with

.. _cmd_commands:

* :code:`$ voxelbotutils commands`

   * :code:`[action]` - the action you want to take for your commands - this can be :code:`add` or :code:`remove`
   * :code:`[bot_directory]` - the directory that the bot files are located in; defaults to `.`
   * :code:`[config_file]` - the path to the config file to use; defaults to `config/config.toml`
   * :code:`--guild [guild_id]` - if you want to perform the action for a specific guild, you can specify its ID here

Getting Started With Bots
---------------------------------------

To get started you'll first want to make a config file. Fortunately, making one is pretty easy, and can be done via CMD.

.. code-block:: bash

   $ voxelbotutils create-config bot

Doing this will make a few files and folders:

* :code:`cogs/ping_command.py` - a simple base class that you can copy/paste to build new classes
* :code:`config/config.toml` - this is your bot's configuration file
* :code:`config/config.example.toml` - this is a git-safe version of your configuration file; you can commit this as you please
* :code:`config/database.pgsql` - this file should contain your database schema; it'll be pushed to your bot's database at every startup
* :code:`.gitignore` - a default Gitignore file to ignore your configuration file

Running the Bot
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Running the bot is also available via the package at a CMD level.

.. code-block:: bash

   $ voxelbotutils run-bot

The information in the bot's :code:`config/config.toml` file will be used to run it, as well as automatically loading any files found in the :code:`cogs/` folder, should they not start with an underscore (eg the file :code:`cogs/test.py` would be loaded, but :code:`cogs/_test.py` would not).

If your database is enabled when you start your bot, the information found in the :code:`config/database.pgsql` will be automatically run, so make sure to write your tables as :code:`CREATE TABLE IF NOT EXISTS` and put your enum creations in an if statement -

.. code-block:: sql

   DO $$ BEGIN
      CREATE TYPE my_type AS ENUM ('Example 1', 'Example 2');
   EXCEPTION
      WHEN duplicate_object THEN null;
   END $$;

Migrating
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you're reading this, you *probably* already have a bot that you want to get using with VoxelBotUtils. Fortunately, migrating is pretty easy. Most base Discord.py classes work by default without alteration, and as such you can just run your existing bot with a VBU config file, and that can be that.

If you really want to get things going, you can change all of your :code:`@commands.command()` lines to :code:`@voxelbotutils.command()<voxelbotutils.Command>`, and any :code:`class MyCog(commands.Cog)` to :code:`class MyCog(voxelbotutils.Cog)<voxelbotutils.Cog>`, and everything else should pretty much handle itself.

Alternatively, some people want to make as few code changes as possible, using only the VoxelBotUtils utilities. That's available too! If you change your bot instance in your current Discord.py code to use :class:`voxelbotutils.MinimalBot` then everything else is drag and drop as usual. This change is necessary to make use of the changes to Discord.py's :class:`discord.abc.Messageable` (which include buttons and ephemeral messages). If there are certain extensions that you wish to load yourself from VoxelBotUtils, you can do that with :code:`bot.load_extension("voxelbotutils.cogs.[NAME]")`.

Getting Started With Websites
-------------------------------------

To get started, you'll need to make a configuration file that VBU can use. The library is nice enough to do this for you if you run the module via the commandline:

.. code-block:: bash

   $ voxelbotutils create-config website

Doing this will make a few files and folders:

* :code:`website/frontend.py` - a simple set of frontend routes
* :code:`website/backend.py` - a simple set of backend routes
* :code:`website/static/` - a folder for all of your static files
* :code:`website/templates/` - a folder for your Jinja2 templates
* :code:`config/website.toml` - this is your bot's configuration file
* :code:`config/website.example.toml` - this is a git-safe version of your configuration file; you can commit this as you please
* :code:`config/database.pgsql` - this file should contain your database schema
* :code:`.gitignore` - a default Gitignore file to ignore your configuration file

Running the Website
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can write your website routes in the :code:`frontend.py` and :code:`backend.py` files (as well as any other files you specify in :attr:`your config<WebsiteConfig.routes>`) and run your website from CMD.

.. code-block:: bash

   $ voxelbotutils run-website
