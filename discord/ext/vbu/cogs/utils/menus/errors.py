import asyncio


class ConverterFailure(Exception):
    """
    Thrown when a converter fails and we want to exit
    the option run entirely.
    """

    pass


class ConverterTimeout(asyncio.TimeoutError):
    """
    Thrown when a converter times out.
    """

    def __init__(self, message):
        super().__init__()
        self.message = message
