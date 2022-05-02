import asyncio
from datetime import datetime as dt

from discord.ext import commands
import upgradechat


class IsNotUpgradeChatPurchaser(commands.CheckFailure):
    """The error raised when the user is missing an UpradeChat purchase."""

    def __init__(self, item_names: str):
        self.item_names = item_names
        super().__init__(
            f"You need to purchase `{self.item_names[0]}` to use this command - "
            f"see `{{ctx.clean_prefix}}info` for more information."
        )


class IsNotUpgradeChatSubscriber(commands.CheckFailure):
    """The error raised when the user is missing an UpradeChat subscription."""

    def __init__(self):
        super().__init__(
            "You need to be subscribed via Upgrade.Chat to run this command - "
            "see `{ctx.clean_prefix}info` for more information."
        )


def is_upgrade_chat_purchaser(*any_item_names):
    """
    A check to see whether a given user is an UpgradeChat purchaser for *any* of the given item names,
    adding an `upgrade_chat_items` attribute to the context object with the given purchases. For example,
    if you wanted a command to only be runnable if someone purchased the an item called `command_access` via
    UpgradeChat, your check would be `is_upgrade_chat_purchaser("command_access")`.

    Raises:
        IsNotUpgradeChatPurchaser: If the user hasn't purchased the given item.
        commands.CheckFailure: If the Upgrade.Chat API is unavailable.
    """

    async def predicate(ctx):

        # See if we're even requesting anything
        if not any_item_names:
            ctx.bot.logger.warning(f"No products input for is_upgrade_chat_purchaser for command {ctx.command.name}")
            return True  # This returns a bool because it needs to return something truthy

        # Grab all purchased roles by the user
        try:
            purchases = await asyncio.wait_for(
                ctx.bot.upgrade_chat.get_orders(discord_id=ctx.author.id, type=upgradechat.UpgradeChatItemType.SHOP),
                timeout=3,
            )
        except (asyncio.TimeoutError, upgradechat.UpgradeChatError):
            raise commands.CheckFailure("Upgrade.Chat is currently unable to process my request for purchasers - please try again later.")

        # See if they purchased anything that's correct
        output_items = []
        for purchase in purchases:
            if purchase.type.name != "SHOP":
                continue
            for order_item in purchase.order_items:
                product_name = order_item.product_name
                if product_name in any_item_names:
                    output_items.append(product_name)
        if output_items:
            ctx.upgrade_chat_items = output_items
            return True

        # They didn't purchase anything [valid]
        raise IsNotUpgradeChatPurchaser()

    return commands.check(predicate)


def is_upgrade_chat_subscriber(*any_item_names):
    """
    A check to see whether a given user is an UpgradeChat subscriber for *any* of the given item names,
    adding an `upgrade_chat_items` attribute to the context object with the given purchases. For example,
    if you wanted a command to only be runnable if someone is subscribed to an item called `command_access`
    via UpgradeChat, your check would be `is_upgrade_chat_subscriber("command_access")`.

    Raises:
        IsNotUpgradeChatSubscriber: If the user isn't subscribing to the given item.
        commands.CheckFailure: If the Upgrade.Chat API is unavailable.
    """

    async def predicate(ctx):

        # See if we're even requesting anything
        if not any_item_names:
            ctx.bot.logger.warning(f"No role tiers input for is_upgrade_chat_subscriber for command {ctx.command.name}")
            return True  # This returns a bool because it needs to return something truthy

        # Grab all purchased roles by the user
        try:
            purchases = await asyncio.wait_for(
                ctx.bot.upgrade_chat.get_orders(discord_id=ctx.author.id, type=upgradechat.UpgradeChatItemType.UPGRADE),
                timeout=3,
            )
        except (asyncio.TimeoutError, upgradechat.UpgradeChatError):
            raise commands.CheckFailure("Upgrade.Chat is currently unable to process my request for subscribers - please try again later.")

        # See if they purchased anything that's correct
        output_items = []
        for purchase in purchases:
            if purchase.type.name != "UPGRADE":
                continue
            if purchase.deleted is not None and purchase.deleted > dt.utcnow():
                continue
            for order_item in purchase.order_items:
                product_name = order_item.product_name
                if product_name in any_item_names:
                    output_items.append(product_name)
        if output_items:
            ctx.upgrade_chat_items = output_items
            return True

        # They didn't purchase anything [valid]
        raise IsNotUpgradeChatSubscriber()

    return commands.check(predicate)
