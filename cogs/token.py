"""
Token related cog
"""
from typing import Union

from discord.ext import commands
import discord

from modules.helpers import async_get
from cogs.bismuth import Bismuth
from bismuthclient.bismuthutil import BismuthUtil


class Token(commands.Cog):
    """Token specific Cogs"""

    def __init__(self):
        pass

    @staticmethod
    async def get_balances(address):
        url = "https://bismuth.today/api/balances/{}".format(address)
        return await async_get(url, is_json=True)

    @staticmethod
    async def get_transactions(address):
        url = "https://bismuth.today/api/transactions/{}".format(address)
        return await async_get(url, is_json=True)

    @staticmethod
    async def safe_send_message(recipient, message):
        try:
            if not recipient.dm_channel:
                await recipient.create_dm()

            await recipient.dm_channel.send(message)
        except Exception as e:
            print(e)

    @commands.group()
    async def token(self, ctx):
        """Token commands"""
        if ctx.invoked_subcommand is None:
            await ctx.send('token needs a subcommand: balance, send, transactions')

    @token.command()
    async def balance(self, ctx, token: str=""):
        """Displays your current balance for every token you own"""
        try:
            user, user_info = await Bismuth.get_user_info(ctx)
            if user_info is None:
                return

            balances = await self.get_balances(user_info["address"])

            if token:
                message = "You don't own any {}".format(token)
                for balance in balances:
                    if balance[0] == token:
                        message = "You own {} {}".format(balance[1], balance[0])
            else:
                message = "You don't own any token"

                if balances:
                    message = "You own:"
                    for balance in balances:
                        message += "\n▸ {} {}".format(balance[1], balance[0])

            await ctx.send(message)

        except Exception as e:
            print(str(e))
            await ctx.message.add_reaction('👎')  # Thumb down

    @token.command()
    async def transactions(self, ctx, token: str = "", amount: int=10):
        """Displays latest transactions"""
        try:
            user, user_info = await Bismuth.get_user_info(ctx)
            if user_info is None:
                return
            amount = min(amount, 20)

            transactions = await self.get_transactions(user_info["address"])

            message = "{} latest {} token transactions:".format(amount, token)
            n = 0
            for transaction in transactions:
                if n >= amount:
                    break
                if not token or transaction[0] == token:
                    n += 1
                    message += "\n▸ {}{} {} {} {}".format("+" if user_info["address"] == transaction[4] else "-", transaction[5], transaction[0], "from" if user_info["address"] == transaction[4] else "to", transaction[3] if user_info["address"] == transaction[4] else transaction[4])

            await ctx.send(message)

        except Exception as e:
            print(str(e))
            await ctx.message.add_reaction('👎')  # Thumb down

    @token.command()
    async def send(self, ctx, recipient: Union[discord.User, str], token: str, amount: int, *message):
        """Sends tokens to the given recipient, recipient can be a @discord_user or a bismuth address"""
        try:
            user, user_info = await Bismuth.get_user_info(ctx)
            if user_info is None:
                return

            if amount <= 0:
                await ctx.send("Amount should be above 0")
                return

            address = recipient
            print(recipient, type(recipient))
            if type(recipient) == discord.user.User:
                recipient_user, recipient_user_info = await Bismuth.get_user_info(ctx, user_id=recipient.id, send_message=False)
                print(recipient_user, recipient_user_info)
                if recipient_user_info is None:
                    await ctx.message.add_reaction('😟')
                    await ctx.send("Recipient user doesn't have a pawer address")
                    return
                address = recipient_user_info["address"]

            if not BismuthUtil.valid_address(address):
                print("address error")
                await ctx.message.add_reaction('😟')
                await ctx.send("Recipient address does not look ok.")
                return

            balances = await self.get_balances(user_info["address"])
            for balance in balances:
                if balance[0] == token:
                    if balance[1] < amount:
                        ctx.send("You only have {} {}".format(balance[1], balance[0]))
                        return

                    await Bismuth.operation(ctx, "token:transfer", address, "0", "{}:{}{}".format(token, amount, ":{}".format(" ".join(message)) if message else ""))
                    break
            else:
                ctx.send("You don't own any {}".format(token))

        except Exception as e:
            print(str(e))
            await ctx.message.add_reaction('👎')  # Thumb down

