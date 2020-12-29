"""
Bismuth related cog
"""

import json
import time
from os import path, walk
import os
import discord
from discord.ext import commands
from modules.config import EMOJIS
from discord.utils import get
# from modules.config import CONFIG
from modules.helpers import User, ts_to_string, async_get
from bismuthclient.bismuthutil import BismuthUtil
from random import shuffle
from modules.stats import Tips
import validators
import re
import asyncio
"""
Potential todo:
    play paper / rock / scissor
    mining rentability calc
"""

DISCLAIMER = """By creating a Bismuth address on this service, you acknowledge that:
- This is meant to be used for tips, thanks you, quick experiments and other small amount usage.
- The matching wallet private key is stored on a secret online server, team operated.
- The team does not hold any responsability if your wallet or funds are lost.
Basically, you're using this service at your own risks.

Type `Pawer accept` to say you understand and proceed."""

MARKETS = ["qtrade", "vinex", "graviex", "finexbox", "hubi"]  # Markets we want to list


async def get_users_from_addresses(addresses: list):
    """
    Given a list of addresses, returns a list of user ids
    No reverse index for now, takes times, don't abuse.
    """
    result = {}
    for folder, subs, files in walk("users"):
            for filename in files:
                if folder != 'users' and filename.endswith('.json'):
                    try:
                        wallet = path.join(folder, filename)
                        with open(wallet, 'r') as f:
                            info = json.load(f)
                            if info['address'] in addresses:
                                result[info['address']] = filename[:-5]
                    except:
                        pass
    return result


class Bismuth(commands.Cog):
    """Bismuth specific Cogs"""

    def __init__(self, bot):
        self.bot = bot
        self.bot.tip_module = Tips()

    @classmethod
    async def get_user_info(cls, ctx, user_id=None, send_message=True):
        user = User(user_id if user_id else ctx.author.id)
        user_info = user.info()
        #print(ctx.author.id, user_info)
        if user_info:
            if user_info['accept']:
                return user, user_info
        if send_message:
            em = discord.Embed(description=DISCLAIMER, colour=discord.Colour.dark_orange())
            em.set_author(name="Terms:")
            await ctx.send(embed=em)
        return user, None

    @staticmethod
    async def safe_send_message(recipient, message):
        try:
            if not recipient.dm_channel:
                await recipient.create_dm()

            await recipient.dm_channel.send(message)
        except Exception as e:
            print(e)

    @commands.command()
    async def bismuth(self, ctx):
        """Shows bismuth price"""
        # TODO: cache
        url = "https://api.coingecko.com/api/v3/coins/bismuth/tickers"
        api = await async_get(url, is_json=True)
        sorted_api = sorted(api["tickers"], key=lambda ticker: ticker["market"]["identifier"] + " " + ticker["target"])
        prices = []
        for market in sorted_api:
            if market["market"]["identifier"] in MARKETS:
                if market["target"] == "BTC":
                    prices.append("▸ {:0.8f} BTC or {:0.3f} USD on {}".format(market["last"], market["converted_last"]["usd"], market["market"]["name"]))
                if market["target"] == "ETH":
                    prices.append("▸ {:0.8f} ETH or {:0.3f} USD on {}".format(market["last"], market["converted_last"]["usd"], market["market"]["name"]))
                if market["target"] == "USDT":
                    prices.append("▸ {:0.8f} USDT or {:0.3f} USD on {}".format(market["last"], market["converted_last"]["usd"], market["market"]["name"]))
        prices = "\n".join(prices)
        # await bot.send_message(discord.Object(id='502494064420061184'), "Bitcoin price is: " + value)
        await ctx.send("{} price is:\n{}".format(EMOJIS['Bismuth'], prices))

    @commands.command()
    async def deposit(self, ctx):
        """Shows or creates a BIS deposit address"""
        user = User(ctx.author.id)
        user_info = user.info()
        print(ctx.author.id, user_info)
        if user_info:
            if user_info['accept']:
                msg = "{}, your {} address is `{}`".\
                    format(ctx.author.display_name, EMOJIS['Bismuth'], user_info['address'])
                em = discord.Embed(description=msg, colour=discord.Colour.green())
                await ctx.send(embed=em)
                return
        em = discord.Embed(description=DISCLAIMER, colour=discord.Colour.dark_orange())
        em.set_author(name="Terms:")
        await ctx.send(embed=em)

    @commands.command()
    async def info(self, ctx):
        """Shows bismuth chain info"""
        # TODO: cache?
        status = User.status()
        # print(status)
        # How to
        msg = "Current supply: {} {}\n".format(int(status['supply']), EMOJIS['Bismuth'])
        msg += "Block height  : {} \n".format(status['blocks'])
        msg += "Protocol      : {} \n".format(status['protocolversion'])
        msg += "Node version  : {} \n".format(status['walletversion'])
        msg += "Consensus     : {}  ({:0.2f}%)\n".format(status['consensus'], status['consensus_percent'])
        msg += "Difficulty    : {:0.2f} \n".format(status['difficulty'])
        msg += "Block reward  : {:0.5f} \n".format(status['last_block'][9])
        msg += "Connections   : {} \n".format(status['connections'])
        # msg += "Time of info  : {} \n".format(status['difficulty'])
        if 'extended' in status:
            msg += "Wallet version: {} \n".format(status['extended']['version'])
        em = discord.Embed(description=msg, colour=discord.Colour.green())
        em.set_author(name="Bismuth PoW status from {} on {} UTC".format(status['server'], ts_to_string(
            float(status['server_timestamp']))))
        await ctx.send(embed=em)

    @commands.command()
    async def balance(self, ctx):
        """Displays your current BIS balance"""
        try:
            # TODO: several types of balance (bis, usd, eur?) or by reactions rather than message ;)
            user = User(ctx.author.id)
            user_info = user.info()
            # print(ctx.author.id, user_info)
            if user_info and user_info['address']:
                    # User exists and validated the terms, has an address
                    balance = user.balance()
                    msg = "{}, your balance is {} {}".\
                        format(ctx.author.display_name, balance, EMOJIS['Bismuth'])
                    em = discord.Embed(description=msg, colour=discord.Colour.green())
                    await ctx.send(embed=em)
                    return
            em = discord.Embed(description=DISCLAIMER, colour=discord.Colour.red())
            em.set_author(name="You have to create your address first:")
            await ctx.send(embed=em)
        except Exception as e:
            print(str(e))
            # Send a PM to the sender or answer if dedicated channel
            await ctx.message.add_reaction('👎')  # Thumb down

    @commands.command()
    async def tip(self, ctx, who_to_tip: discord.Member, amount: str='1'):
        """Tip a user, default 1 bis, min 0.1, max 50 BIS"""
        try:
            amount = float(amount)
            if amount > 50:
                amount = 50
                await ctx.send("Maw tip amount too high, lowering to 50 {}".format(EMOJIS['Bismuth']))

            if amount < 0.1:
                amount = 0.1
            user = User(ctx.author.id)
            user_info = user.info()
            # print(ctx.author.id, user_info)
            if user_info and user_info['address']:
                # User exists and validated the terms, has an address
                # We could get a custom default tip value here from the info
                # Make sure balance is enough
                balance = float(user.balance())
                msg = "{} tip {}, balance is {} ".format(ctx.author.display_name, amount, balance)
                print(msg)
                if balance < amount + 0.01:
                    print("balance too low")
                    await ctx.message.add_reaction('😟')
                    # await ctx.message.add_reaction('⚖️')
                    return
                user_to_tip_info = User(who_to_tip.id).info()
                print("to_tip", user_to_tip_info)
                if not user_to_tip_info or not user_to_tip_info['address']:
                    print("user has no wallet")
                    await ctx.message.add_reaction('🤔')  # Thinking face purse
                    message = "Hi {}, {} wanted to tip you, but you do not have a Discord Bismuth wallet yet.\n"\
                              .format(who_to_tip.display_name, ctx.author.display_name)
                    message += "It's easy, you just have to type `Pawer deposit` here to read and accept the terms.\n"
                    message += "Then you'll have an address of yours and be able to receive tips and play with me.\n"
                    message += "Use `Pawer help` to get a full list of what I can do."
                    await self.safe_send_message(who_to_tip, message)
                    return
                send = user.send_bis_to(amount, user_to_tip_info['address'])
                self.bot.tip_module.tip(user_info['address'], user_to_tip_info['address'], amount)
                txid = send['txid']
                print("txid", txid)
                if txid:
                    # answer by reaction not to pollute
                    await ctx.message.add_reaction('👍')  # Thumb up
                    message = "Yeah! You've been tipped {:0.2f} {} by {} ({}) from the Bismuth discord!"\
                              .format(amount, EMOJIS['Bismuth'], ctx.author, ctx.author.display_name)
                    await self.safe_send_message(who_to_tip, message)

                else:
                    await ctx.message.add_reaction('👎')
                return
            # Depending on channel, say or send PM
            em = discord.Embed(description=DISCLAIMER, colour=discord.Colour.red())
            em.set_author(name="You have to create your address first:")
            await ctx.send(embed=em)
        except Exception as e:
            print(str(e))
            # Send a PM to the sender or answer if dedicated channel
            await ctx.message.add_reaction('👎')  # Thumb down

    @commands.command()
    async def rain(self, ctx, total_amount: str='10', how_many_users: str='10'):
        """Distribute a given amount between n users"""
        try:
            if "/" in total_amount:
                data = total_amount.split("/")
                total_amount = float(data[0])
                how_many_users = float(data[1])
            total_amount = float(total_amount)
            how_many_users = int(how_many_users)

            if total_amount < 0 or how_many_users < 0:
                return

            if how_many_users > 100:
                how_many_users = 100
            if how_many_users < 1:
                how_many_users = 1

            if total_amount > 1000:
                total_amount = 1000
            if total_amount < 0.1 * how_many_users:
                how_many_users = int(total_amount/0.1)
            individual_amount = total_amount/how_many_users
            user = User(ctx.author.id)

            user_info = user.info()
            if user_info and user_info['address']:
                balance = float(user.balance())
                msg = "{} rain {} bis to {} users, balance is {} ".format(ctx.author.display_name, total_amount,
                                                                          how_many_users, balance)
                print(msg)
                if balance < total_amount + 0.01 * how_many_users:
                    print("balance too low")
                    await ctx.message.add_reaction('😟')
                    return

                registered_members = []
                unregistered_members = []
                for member in self.bot.get_all_members():
                    if str(member.status) != "offline" and not member.bot and member.name != ctx.author.name:
                        #print(member.name, member.status, member.bot)
                        current_user = User(member.id)
                        member_info = current_user.info()
                        if member_info and member_info["address"]:
                            registered_members.append(member)
                        else:
                            unregistered_members.append(member)

                how_many_real_users = int(min(how_many_users, len(registered_members)))
                shuffle(registered_members)
                shuffle(unregistered_members)

                message = "Yeah! You got {:0.2f} {} from the rain of {} ({}) from the Bismuth discord!" \
                    .format(individual_amount, EMOJIS['Bismuth'], ctx.author, ctx.author.display_name)
                final_message = "{} sent {:0.2f} {} each to: ".format(ctx.author.mention, individual_amount, EMOJIS['Bismuth'])
                self.bot.tip_module.start_rain(user_info['address'], individual_amount*how_many_real_users, how_many_real_users, "rain")
                for current_member in registered_members[:how_many_real_users]:
                    to_address = User(current_member.id).info()['address']
                    user.send_bis_to(individual_amount, to_address)
                    self.bot.tip_module.tip(user_info['address'], to_address, individual_amount, "rain")
                    final_message += current_member.mention + " "
                    await self.safe_send_message(current_member, message)
                await ctx.send(final_message)
                await ctx.message.add_reaction('👍')  # Thumb up

                for current_member in unregistered_members[:10]:
                    message = "Hi {}, {} launched a rain, but you do not have a Discord Bismuth wallet yet.\n" \
                        .format(current_member.display_name, ctx.author.display_name)
                    message += "It's easy, you just have to type `Pawer deposit` here to read and accept the terms.\n"
                    message += "Then you'll have an address of yours and be able to receive tips and play with me.\n"
                    message += "Use `Pawer help` to get a full list of what I can do."
                    await self.safe_send_message(current_member, message)

                return

            # Depending on channel, say or send PM
            em = discord.Embed(description=DISCLAIMER, colour=discord.Colour.red())
            em.set_author(name="You have to create your address first:")
            await ctx.send(embed=em)
        except Exception as e:
            print(str(e))
            # Send a PM to the sender or answer if dedicated channel
            await ctx.message.add_reaction('👎')  # Thumb down

    @commands.command()
    async def withdraw(self, ctx, address:str, amount: str, *message):
        """Send BIS from your wallet to any BIS address, with an optional message"""
        try:
            amount = float(amount)
            openfield_data = ' '.join(filter(None, message))
            user = User(ctx.author.id)
            user_info = user.info()
            # Check the address looks ok
            if not BismuthUtil.valid_address(address):
                print("address error")
                await ctx.message.add_reaction('😟')
                await ctx.send("Address does not look ok. Command is `Pawer withdraw <address> <amount> [message]`")
                return

            if user_info and user_info['address']:
                # User exists and validated the terms, has an address
                # Make sure balance is enough
                balance = float(user.balance())
                msg = "{} withdraw {}, balance is {} ".format(ctx.author.display_name, amount, balance)
                fees = BismuthUtil.fee_for_tx(openfield_data)
                print(msg)
                if balance < amount + 0.01:
                    print("balance too low")
                    await ctx.message.add_reaction('😟')
                    await ctx.send("Not enough balance to cover amount + fee ({} Fees)".format(fees))
                    return
                send = user.send_bis_to(amount, address, data=openfield_data)
                txid = send['txid']
                print("txid", txid)
                if txid:
                    # answer by reaction not to pollute
                    await ctx.message.add_reaction('👍')  # Thumb up
                    await ctx.send("Done, txid is {}.".format(txid))
                else:
                    await ctx.message.add_reaction('👎')  # Thumb down
                    await ctx.send("Error {}".format(send['error']))
                return
            # Depending on channel, say or send PM
            em = discord.Embed(description=DISCLAIMER, colour=discord.Colour.red())
            em.set_author(name="You have to create your address first:")
            await ctx.send(embed=em)
        except Exception as e:
            print(str(e))
            # Send a PM to the sender or answer if dedicated channel
            await ctx.message.add_reaction('👎')  # Thumb down
            await ctx.send("Error {}".format(e))

    @commands.command()
    async def zirco(self, ctx, amount: str, bet: str):
        """Play ZircoDice from your pawer wallet, with any amount less than 100 along with your bet """
        try:
            amount = float(amount)
            zirco_service_address = '340c195f768be515488a6efedb958e135150b2ef3e53573a7017ac7d'
            user = User(ctx.author.id)
            user_info = user.info()

            # Check the bet field
            if bet.lower() not in ('odd', 'even'):
                print("OpenField data error")
                await ctx.message.add_reaction('😟')
                await ctx.send("Your bet does not look ok. Command is `Pawer zirco <amount> <odd/even>`")
                return

            # Check the bet amount
            if (amount - float(100)) > 0.01 :
                print("Bet amount too high")
                await ctx.message.add_reaction('😟')
                await ctx.send("You are betting too high. Recommended amount is less than 100`")
                return

            if user_info and user_info['address']:
                # User exists and validated the terms, has an address
                # Make sure balance is enough
                balance = float(user.balance())
                msg = "{} zirco {}, balance is {} ".format(ctx.author.display_name, amount, balance)
                fees = BismuthUtil.fee_for_tx(bet)
                print(msg)
                if balance < amount + 0.01004:
                    print("balance too low")
                    await ctx.message.add_reaction('😟')
                    await ctx.send("Not enough balance to cover amount + fee ({} Fees)".format(fees))
                    return
                send = user.send_bis_to(amount, zirco_service_address, data=bet)
                txid = send['txid']
                print("txid", txid)
                if txid:
                    # answer by reaction not to pollute
                    await ctx.message.add_reaction('👍')  # Thumb up
                    await ctx.send("Your bet has been placed. Txid is {}".format(txid))
                    await ctx.message.remove_reaction('⏳', self.bot.user)
                    await self.get_zirco_status(ctx.author, txid)
                else:
                    await ctx.message.add_reaction('👎')  # Thumb down
                    await ctx.send("Can't place your bet. Error {}".format(send['error']))
                return
        except Exception as e:
            print(str(e))
            # Send a PM to the sender or answer if dedicated channel
            await ctx.message.add_reaction('👎')  # Thumb down
            await ctx.send("Can't place your bet. Error {}".format(e))

    @classmethod
    @commands.command()
    async def operation(cls, ctx, operation: str, address:str, amount: str, *message):
        """Send a generic 'operation' transaction, with an optional message"""
        # TODO: too much code in common with withdraw, factorize somehow.
        try:
            amount = float(amount)
            openfield_data = ' '.join(filter(None, message))
            user = User(ctx.author.id)
            user_info = user.info()
            # Check the address looks ok
            if not BismuthUtil.valid_address(address):
                print("address error")
                await ctx.message.add_reaction('😟')
                await ctx.send("Address does not look ok. Command is `Pawer operation <operation> <address> <amount> [message]`")
                return

            if user_info and user_info['address']:
                # User exists and validated the terms, has an address
                # Make sure balance is enough
                balance = float(user.balance())
                msg = "{} withdraw {}, balance is {} ".format(ctx.author.display_name, amount, balance)
                fees = BismuthUtil.fee_for_tx(openfield_data)
                print(msg)
                if balance < amount + 0.01:
                    print("balance too low")
                    await ctx.message.add_reaction('😟')
                    await ctx.send("Not enough balance to cover amount + fee ({} Fees)".format(fees))
                    return
                send = user.send_bis_to(amount, address, data=openfield_data, operation=operation)
                txid = send['txid']
                print("txid", txid)
                if txid:
                    # answer by reaction not to pollute
                    await ctx.message.add_reaction('👍')  # Thumb up
                    await ctx.send("Done, txid is {}.".format(txid))
                else:
                    await ctx.message.add_reaction('👎')  # Thumb down
                    await ctx.send("Error {}".format(send['error']))
                return
            # Depending on channel, say or send PM
            em = discord.Embed(description=DISCLAIMER, colour=discord.Colour.red())
            em.set_author(name="You have to create your address first:")
            await ctx.send(embed=em)
        except Exception as e:
            print(str(e))
            # Send a PM to the sender or answer if dedicated channel
            await ctx.message.add_reaction('👎')  # Thumb down
            await ctx.send("Error {}".format(e))

    @commands.command()
    async def freebismuth(self, ctx, tweet_url: str):
        """Register your #Bismuth tweet and get free bismuth"""
        try:
            amount = float(0)  # amount has to be 0
            operation = 'twitter'
            user = User(ctx.author.id)
            user_info = user.info()
            address = user_info['address']

            #validate tweet url.
            # TODO: Validate tweet likes and retweets as per freebismuth spec
            if not validators.url(tweet_url):
                print("tweet url error")
                await ctx.message.add_reaction('😟')
                await ctx.send("Link to the tweet does not look ok. Command is `Pawer freebismuth <tweet_url>`")
                return

            if user_info and user_info['address']:
                # User exists and validated the terms, has an address
                # Make sure balance is enough
                balance = float(user.balance())
                tweet_id = re.search('/status/(\d+)', tweet_url).group(1)  # Extract tweet ID
                msg = "{} freebismuth, tweet ID is {} ".format(ctx.author.display_name, tweet_id)
                fees = BismuthUtil.fee_for_tx(tweet_id)
                print(msg)
                if balance < amount + fees:
                    print("balance too low")
                    await ctx.message.add_reaction('😟')
                    await ctx.send("Not enough balance to cover fee ({} Fees)".format(fees))
                    return
                send = user.send_bis_to(amount, address, data=tweet_id, operation=operation)
                txid = send['txid']
                print("txid", txid)
                if txid:
                    # answer by reaction not to pollute
                    await ctx.message.add_reaction('👍')  # Thumb up
                    await ctx.send("Your tweet has been registered. Txid is {}.".format(txid))
                else:
                    await ctx.message.add_reaction('👎')  # Thumb down
                    await ctx.send("Can't register your tweet. Error {}".format(send['error']))
                return
        except Exception as e:
            print(str(e))
            # Send a PM to the sender or answer if dedicated channel
            await ctx.message.add_reaction('👎')  # Thumb down
            await ctx.send("Can't register your tweet. Error {}".format(e))

    @commands.command()
    async def bisurl(self, ctx, bisurl: str, send: str='NO'):
        """Decode a transaction from a BIS URL. Append SEND to effectively send the tx."""
        # TODO: too much code in common with withdraw, factorize somehow.
        try:
            try:
                decode = BismuthUtil.read_url(bisurl)
            except Exception as e:
                await ctx.message.add_reaction('😢')  # Crying
                await ctx.send("Does not look like a proper BIS URL")
                return
            amount = float(decode['amount'])
            address = decode['recipient']
            operation = decode['operation']
            message = decode['openfield']
            fees = BismuthUtil.fee_for_tx(message)

            decoded = "▸ Recipient: {}\n".format(address)
            decoded += "▸ Amount: {:.2f} $BIS\n".format(amount)
            decoded += "▸ Operation: {}\n".format(operation)
            decoded += "▸ Message: {}\n".format(message)
            decoded += "▸ Fees: {} $BIS\n".format(fees)
            if send == 'SEND':
                title = "Decoded BIS URL:"
                em = discord.Embed(description=decoded, colour=discord.Colour.green())
                em.set_author(name=title)
                await ctx.send(embed=em)
            else:
                title = "Decoded BIS URL: (**not** sent)"
                decoded += " \nPaste this command again and append ` SEND` if you want to send that transaction.\n"
                em = discord.Embed(description=decoded, colour=discord.Colour.green())
                em.set_author(name=title)
                await ctx.send(embed=em)
                return

            user = User(ctx.author.id)
            user_info = user.info()
            # Check the address looks ok
            if not BismuthUtil.valid_address(decode['recipient']):
                print("address error")
                await ctx.message.add_reaction('😟')
                await ctx.send("Address does not look ok. Command is `Pawer operation <operation> <address> <amount> [message]`")
                return

            if user_info and user_info['address']:
                # User exists and validated the terms, has an address
                # Make sure balance is enough
                balance = float(user.balance())
                msg = "{} withdraw {}, balance is {} ".format(ctx.author.display_name, amount, balance)
                fees = BismuthUtil.fee_for_tx(message)
                print(msg)
                if balance < amount + 0.01:
                    print("balance too low")
                    await ctx.message.add_reaction('😟')
                    await ctx.send("Not enough balance to cover amount + fee ({} Fees)".format(fees))
                    return
                send = user.send_bis_to(amount, address, data=message, operation=operation)
                txid = send['txid']
                print("txid", txid)
                if txid:
                    # answer by reaction not to pollute
                    await ctx.message.add_reaction('👍')  # Thumb up
                    await ctx.send("Done, txid is {}.".format(txid))
                else:
                    await ctx.message.add_reaction('👎')  # Thumb down
                    await ctx.send("Error {}".format(send['error']))
                return
            # Depending on channel, say or send PM
            em = discord.Embed(description=DISCLAIMER, colour=discord.Colour.red())
            em.set_author(name="You have to create your address first:")
            await ctx.send(embed=em)
        except Exception as e:
            print(str(e))
            # Send a PM to the sender or answer if dedicated channel
            await ctx.message.add_reaction('👎')  # Thumb down
            await ctx.send("Error {}".format(e))

    @commands.command()
    async def sign(self, ctx, message: str):
        """Sign a message from your wallet, for off-chain use"""
        try:
            user = User(ctx.author.id)
            user_info = user.info()
            if user_info and user_info['address']:
                # User exists and validated the terms, has an address
                # Make sure balance is enough
                res = user.sign_message(message)
                sign = res['sign']
                # print("sign", sign)
                if sign:
                    # answer by reaction not to pollute
                    await ctx.message.add_reaction('👍')  # Thumb up
                    await ctx.send("Signature is `{}`.".format(sign))
                else:
                    await ctx.message.add_reaction('👎')  # Thumb down
                    await ctx.send("Error {}".format(res['error']))
                return
            # Depending on channel, say or send PM
            em = discord.Embed(description=DISCLAIMER, colour=discord.Colour.red())
            em.set_author(name="You have to create your address first:")
            await ctx.send(embed=em)
        except Exception as e:
            print(str(e))
            # Send a PM to the sender or answer if dedicated channel
            await ctx.message.add_reaction('👎')  # Thumb down
            await ctx.send("Error {}".format(e))

    @commands.command()
    async def accept(self, ctx):
        """Accept the Pawer terms, run deposit first"""
        user = User(ctx.author.id)
        user_info = user.info()
        # if accepted, say when and gives address
        if user_info:
            if user_info['accept']:
                msg = "Your :bis: address is `{}`".format(user_info['address'])
                em = discord.Embed(description=msg, colour=discord.Colour.orange())
                em.set_author(name="{}, you already accepted the terms on {}".
                              format(ctx.author.display_name, ts_to_string(user_info['accept'])))
                await ctx.send(embed=em)
                return
        # If not, creates wallet and stores accepted.
        address = user.create_wallet()
        info = {"accept": int(time.time()), "address": address}
        user.save(info)

        self.bot.tip_module.add_user(address, ctx.author.id, ctx.author.display_name)

        # TODO: safety, store an encrypted backup of the wallet elsewhere.
        msg = "Your {} address is `{}`".format(EMOJIS['Bismuth'], info['address'])
        em = discord.Embed(description=msg, colour=discord.Colour.green())
        em.set_author(name="{}: Terms accepted".format(ctx.author.display_name))
        await ctx.send(embed=em)

    @commands.command()
    async def terms(self, ctx):
        """Remind the current Pawer terms of use."""
        em = discord.Embed(description=DISCLAIMER, colour=discord.Colour.green())
        em.set_author(name="Current terms of use:")
        await ctx.send(embed=em)

    @commands.command()
    async def graph(self, ctx, type=''):
        """Shows bismuth graphs: pools, diff, blocktime, hypernodes"""
        rkey = time.time()
        urls = {'pools': ["Bismuth Pools estimated hashrate", 'https://hypernodes.bismuth.live/plots/hr.php?col=1&void={}'.format(rkey)],
                'diff': ["Mainnet difficulty evolution", 'https://hypernodes.bismuth.live/plots/mainnet/diff.php?void={}'.format(rkey)],
                'hypernodes': ["Number of 10k equivalent HN per round", 'https://hypernodes.bismuth.live/plots/posnet/weight.php?void={}'.format(rkey)],
                'blocktime': ["Mainnnet blocktime evolution", 'https://hypernodes.bismuth.live/plots/mainnet/blocktime.php?void={}'.format(rkey)]}
        if type not in urls:
            msg = "\n".join(["`{}`: {}".format(a,b[0]) for a, b in urls.items()])
            em = discord.Embed(description=msg, colour=discord.Colour.red())
            em.set_author(name="Error: Please specify a graph type")
            await ctx.send(embed=em)
        em = discord.Embed()
        em.set_image(url=urls[type][1])
        em.set_author(name=urls[type][0])
        await ctx.send(embed=em)

    @commands.command()
    async def board(self, ctx, action:str):
        """Shows stats of given action: tip/rain"""
        with open("data/tips.json") as f:
            data = json.load(f)
        if action not in data:
            await ctx.send("unknown action")
            return
        msg = "__Who gave the most:__\n\n"
        for user in data[action]["from"]:
            msg += "{} gave {:0.2f} Bis\n".format(get(self.bot.get_all_members(), id=str(user[2])).display_name, user[0])

        msg += "\n\n__Who received the most:__\n\n"
        for user in data[action]["to"]:
            msg += "{} received {:0.2f} Bis\n".format(get(self.bot.get_all_members(), id=str(user[2])).display_name, user[0])

        em = discord.Embed(description=msg, colour=discord.Colour.green())
        em.set_author(name="{} board".format(action))
        await ctx.send(embed=em)

    async def get_zirco_status(self, sender, txid):
        try:
            timeout_counter = 0
            while not self.bot.is_closed and timeout_counter < 10:
                result = await async_get("http://bismuth.live:1212/txid/{}".format(txid))
                if result != "not found":
                    bet_info = json.loads(result)
                    try:
                        if bet_info["victorious"] == 1:
                            await self.safe_send_message(sender, "Hurrah! You've won the bet worth {}{}.".format(bet_info["amount"], EMOJIS['Bismuth']))
                        else:
                            await self.safe_send_message(sender, "You've lost the bet worth {}{}. Hard luck!".format(bet_info["amount"], EMOJIS['Bismuth']))
                    except:
                        pass
                    return
                else:
                    timeout_counter += 1
                    await asyncio.sleep(60)
        except Exception as e:
            print(str(e))
