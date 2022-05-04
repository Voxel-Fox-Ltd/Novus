import discord


class MyClient(discord.Client):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        return

    async def on_ready(self) -> None:
        """Ready event handler"""
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')
        self.dispatch('custom_event', 'Ready')
        return

    async def on_message(self, message: discord.Message) -> None:
        """Message event handler"""
        self.dispatch('custom_event', f'Message Received: {message.content}')
        return

    async def on_custom_event(self, text: str) -> None:
        """Custom event handler to print given text"""
        print(f'{self.user} ({self.user.id}): {text}')
        return


client = MyClient()
client.run('TOKEN')
