import enum
import typing

import discord


class CheckFailureAction(enum.Enum):
    """
    An enum describing actions that can be taken when a check fails.

    Attributes:
        FAIL: If the converter should fail when the check method returns :code:`False`.
        RETRY: If the converter should re-prompt the user for another onput when the
            check method returns :code:`False`.
    """

    FAIL = enum.auto()
    RETRY = enum.auto()


class Check(object):
    """
    An object to describe what to do when a user fails to give a valid answer to a converter.

    Examples:

        ::

            # This instance will take the input message and make sure its content is a digit between 7 and
            # 30 inclusive. If the user fails to provide this, the bot will output the string given as
            # `fail_message`, and wait for the user to retry again.
            voxelbotutils.menus.Check(
                check=lambda message: message.content.isdigit() and int(message.content) in range(7, 31),
                fail_message="You need to give a *number* between **7** and **31**.",
            )
    """

    failures = CheckFailureAction

    def __init__(
            self,
            check: typing.Callable[[discord.Message], bool] = None,
            on_failure: CheckFailureAction = CheckFailureAction.FAIL,
            fail_message: str = None):
        """
        Attributes
        ----------
        check : typing.Callable[[discord.Message], bool]
            A method that takes a message instance, returning whether or not
            this instance has converted properly. This cannot be a coroutine.
        fail_message : str, optional
            If the message doesn't pass the check, this is the
            message that string that gets output.

        Parameters
        ----------
        check : Optional[Callable[[discord.Message], bool]]
            A method that takes a message instance, returning whether or not
            this instance has converted properly. This cannot be a coroutine.
        fail_message : Optional[str]
            If the message doesn't pass the check, this is the
            message that string that gets output.
        """

        self.check: typing.Callable[[discord.Message], bool] = check
        self.fail_message: str = fail_message or "Please provide a valid input."


class ModalCheck(Check):
    """
    An object to describe what to do when a user fails to give a valid answer to a converter.

    Examples:

        ::

            # This instance will take the input message and make sure its content is a digit between 7 and
            # 30 inclusive. If the user fails to provide this, the bot will output the string given as
            # `fail_message`, and wait for the user to retry again.
            voxelbotutils.menus.ModalCheck(
                check=lambda interaction: interaction.components[0].components[0].value.isdigit() and int(interaction.components[0].components[0].value) in range(7, 31),
                on_failure=voxelbotutils.menus.Check.failures.RETRY,
                fail_message="You need to give a *number* between **7** and **31**.",
            )
    """

    failures = CheckFailureAction

    def __init__(
            self,
            check: typing.Callable[[discord.Interaction], bool] = None,
            on_failure: CheckFailureAction = CheckFailureAction.FAIL,
            fail_message: str = None):
        """
        Attributes
        ----------
        check : Callable[[discord.Interaction], bool]
            A method that takes a message instance, returning whether or not
            this instance has converted properly. This cannot be a coroutine.
        fail_message : str
            If the message doesn't pass the check, this is the message
            that string that gets output.

        Parameters
        ----------
        check : Optional[Callable[[discord.Interaction], bool]]
            A method that takes an interaction instance, returning whether or not
            this instance has converted properly. This cannot be a coroutine.
        fail_message : Optional[str]
            If the message doesn't pass the check, this is the
            message that string that gets output.
        """

        self.check: typing.Callable[[discord.Interaction], bool] = check
        self.fail_message: str = fail_message or "Please provide a valid input."
