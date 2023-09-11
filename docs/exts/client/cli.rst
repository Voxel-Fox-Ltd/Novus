Command-Line Interface
======================

Novus implements a few menus via CLI.

``novus run``
-------------

Run a bot instance with config either passed in as CLI arguments, or from a
config file (either found in the current directory, or passed as a CLI arg).

``novus run-webserver``
-----------------------

Run a bot webserver instance (interactions only) with config either passed in
as CLI arguments, or from a config file (either found in the current directory,
or passed as a CLI arg).

``novus run-status``
--------------------

Create a websocket to Discord, connecting only to keep track of guild count and
to display a status on your bot user.

``novus config-dump``
---------------------

Output a config (with arguments optionally supplied via CLI). This can be piped
into a file (``novus config-dump --token test > config.yaml``).

``novus new-plugin``
--------------------

Output a new plugin (with arguments optionally supplied via CLI). This can be
piped into a file (``novus new-plugin Test > test.py``).
