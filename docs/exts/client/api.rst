.. currentmodule:: novus.ext.client

API Reference
=============

Bots
----

.. autoclass:: Client
    :members:
.. autoclass:: Config

Plugins
-------

.. autoclass:: Plugin
    :members:
    :no-members: dispatch

Commands
--------

.. autofunction:: command
.. autoclass:: Command
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: CommandDescription
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: CommandGroup
    :members:
    :inherited-members:
    :no-special-members:

Events
------

Most events can be handled by using an :class:`~novus.ext.client.EventBuilder` decorator within a plugin.

.. autoclass:: EventBuilder
    :members:

Loops
-----

.. autofunction:: loop
.. autoclass:: Loop
    :members:
    :inherited-members:
    :no-special-members:
.. autoclass:: LoopBehavior

Errors
------

.. autoclass:: CommandError
