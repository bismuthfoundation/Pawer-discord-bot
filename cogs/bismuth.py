"""
Bismuth related cog
"""

import json
import time

import discord
from discord.ext import commands
from modules.config import EMOJIS

# from modules.config import CONFIG
from modules.helpers import User, ts_to_string, async_get
from bismuthclient.bismuthutil import BismuthUtil

"""
Potential todo:
    play paper / rock / scissor
    play zircodice
    mining rentability calc
"""

DISCLAIMER = """By creating a Bismuth address on this service, you acknowledge that:
- This is meant to be used for tips, thanks you, quick experiments and other small amount usage.
- The matching wallet private key is stored on a secret online server, team operated.
- The team does not hold any responsability if your wallet or funds are lost.
Basically, you're using this service at your own risks.

Type `Pawer accept` to say you understand and proceed."""


class Bismuth:
    """Bismuth specific Cogs"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='bismuth', brief="Shows bismuth price", pass_context=True)
    async def bismuth(self, ctx):
        # TODO: cache
        url = 'https://bismuth.ciperyho.eu/api/markets'
        response = await async_get(url, is_json=True)
        cryptopia = response['markets']['Cryptopia']
        qtrade = response['markets']['QTrade']
        # await client.send_message(discord.Object(id='502494064420061184'), "Bitcoin price is: " + value)
        await self.bot.say("{} price is:\n▸ {:0.8f} BTC or {:0.2f} USD on Cryptopia\n▸ {:0.8f} BTC or {:0.2f} USD on QTrade"
                           .format(EMOJIS['Bismuth'], cryptopia['BTC']['lastPrice'], cryptopia['USD']['lastPrice'],
                                   qtrade['BTC']['lastPrice'],qtrade['USD']['lastPrice']))

    @commands.command(name='deposit', brief="Shows or creates a BIS deposit address", pass_context=True)
    async def deposit(self, ctx):
        user = User(ctx.message.author.id)
        user_info = user.info()
        print(ctx.message.author.id, user_info)
        if user_info:
            if user_info['accept']:
                msg = "{}, your {} address is `{}`".\
                    format(ctx.message.author.display_name, EMOJIS['Bismuth'], user_info['address'])
                em = discord.Embed(description=msg, colour=discord.Colour.green())
                await self.bot.say(embed=em)

                return

        em = discord.Embed(description=DISCLAIMER, colour=discord.Colour.dark_orange())
        em.set_author(name="Terms:")
        await self.bot.say(embed=em)

    @commands.command(name='info', brief="Shows bismuth chain info", pass_context=True)
    async def info(self, ctx):
        # TODO: cache?
        status = User.status()
        # print(status)
        # How to
        msg = "Current supply: {} {}\n".format(int(status['supply']), EMOJIS['Bismuth'])
        msg += "Block height  : {} \n".format(status['blocks'])
        msg += "Protocol      : {} \n".format(status['protocolversion'])
        msg += "Node version  : {} \n".format(status['walletversion'])
        msg += "Consensus     : {}  ({:0.2f}%)\n".format(status['consensus'], status['consensus_percent'])
        msg += "Difficulty    : {} \n".format(status['difficulty'])
        msg += "Connections   : {} \n".format(status['connections'])
        # msg += "Time of info  : {} \n".format(status['difficulty'])
        if 'extended' in status:
            msg += "Wallet version: {} \n".format(status['extended']['version'])
        em = discord.Embed(description=msg, colour=discord.Colour.green())
        em.set_author(name="Bismuth PoW status from {} on {} UTC".format(status['server'], ts_to_string(
            float(status['server_timestamp']))))
        await self.bot.say(embed=em)

    @commands.command(name='balance', brief="Displays your current BIS balance", pass_context=True)
    async def balance(self, ctx, *, type: str=''):
        # TODO: several types of balance (bis, usd, eur?) or by reactions rather than message ;)
        user = User(ctx.message.author.id)
        user_info = user.info()
        # print(ctx.message.author.id, user_info)
        if user_info and user_info['address']:
                # User exists and validated the terms, has an address
                balance = user.balance()
                msg = "{}, your balance is {} {}".\
                    format(ctx.message.author.display_name, balance, EMOJIS['Bismuth'])
                em = discord.Embed(description=msg, colour=discord.Colour.green())
                await self.bot.say(embed=em)
                return
        em = discord.Embed(description=DISCLAIMER, colour=discord.Colour.red())
        em.set_author(name="You have to create your address first:")
        await self.bot.say(embed=em)

    @commands.command(name='tip', brief="Tip a user, default 1 bis, min 0.1, max 50 BIS", pass_context=True)
    async def tip(self, ctx, who_to_tip: discord.Member, amount: str='1'):
        try:
            amount = float(amount)
            if amount > 50:
                amount = 50
            if amount < 0.1:
                amount = 0.1
            user = User(ctx.message.author.id)
            user_info = user.info()
            # print(ctx.message.author.id, user_info)
            if user_info and user_info['address']:
                    # User exists and validated the terms, has an address
                    # We could get a custom default tip value here from the info
                    # Make sure balance is enough
                    balance = float(user.balance())
                    msg = "{} tip {}, balance is {} ".format(ctx.message.author.display_name, amount, balance)
                    print(msg)
                    if balance < amount + 0.01:
                        print("balance too low")
                        await self.bot.add_reaction(ctx.message, '😟')
                        # await self.bot.add_reaction(ctx.message, '⚖️')
                        return
                    user_to_tip_info = User(who_to_tip.id).info()
                    print("to_tip", user_to_tip_info)
                    if not user_to_tip_info or not user_to_tip_info['address']:
                        print("user has no wallet")
                        await self.bot.add_reaction(ctx.message, '🤔')  # Thinking face purse
                        # await self.bot.add_reaction(ctx.message, '🤔👛')  # Thinking face purse
                        return
                    txid = user.send_bis_to(amount, user_to_tip_info['address'])
                    print("txid", txid)
                    if txid:
                        # answer by reaction not to pollute
                        await self.bot.add_reaction(ctx.message, '👍')  # Thumb up
                    else:
                        await self.bot.add_reaction(ctx.message, '👎')
                    return
            # Depending on channel, say or send PM
            em = discord.Embed(description=DISCLAIMER, colour=discord.Colour.red())
            em.set_author(name="You have to create your address first:")
            await self.bot.say(embed=em)
        except Exception as e:
            print(str(e))
            # Send a PM to the sender or answer if dedicated channel
            await self.bot.add_reaction(ctx.message, '👎')  # Thumb down

    @commands.command(name='withdraw', brief="Send BIS from your wallet to any BIS address, with an optional message", pass_context=True)
    async def withdraw(self, ctx, address:str, amount: str, message: str=''):
        try:
            amount = float(amount)
            user = User(ctx.message.author.id)
            user_info = user.info()
            # Check the address looks ok
            if not BismuthUtil.valid_address(address):
                print("address error")
                await self.bot.add_reaction(ctx.message, '😟')
                await self.bot.say("Address does not look ok. Command is `Pawer withdraw <address> <amount> [message]`")
                return

            if user_info and user_info['address']:
                # User exists and validated the terms, has an address
                # Make sure balance is enough
                balance = float(user.balance())
                msg = "{} withdraw {}, balance is {} ".format(ctx.message.author.display_name, amount, balance)
                fees = BismuthUtil.fee_for_tx(message)
                print(msg)
                if balance < amount + 0.01:
                    print("balance too low")
                    await self.bot.add_reaction(ctx.message, '😟')
                    await self.bot.say("Not enough balance to cover amount + fee ({} Fees)".format(fees))
                    return
                txid = user.send_bis_to(amount, address, data=message)
                print("txid", txid)
                if txid:
                    # answer by reaction not to pollute
                    await self.bot.add_reaction(ctx.message, '👍')  # Thumb up
                    await self.bot.say("Done, txid is {}.".format(txid))
                else:
                    await self.bot.add_reaction(ctx.message, '👎')  # Thumb down
                    await self.bot.say("Error")
                return
            # Depending on channel, say or send PM
            em = discord.Embed(description=DISCLAIMER, colour=discord.Colour.red())
            em.set_author(name="You have to create your address first:")
            await self.bot.say(embed=em)
        except Exception as e:
            print(str(e))
            # Send a PM to the sender or answer if dedicated channel
            await self.bot.add_reaction(ctx.message, '👎')  # Thumb down
            await self.bot.say("Error {}".format(e))

    @commands.command(name='accept', brief="Accept the Pawer terms, run deposit first", pass_context=True)
    async def accept(self, ctx):
        user = User(ctx.message.author.id)
        user_info = user.info()
        # if accepted, say when and gives address
        if user_info:
            if user_info['accept']:
                msg = "Your :bis: address is `{}`".format(user_info['address'])
                em = discord.Embed(description=msg, colour=discord.Colour.orange())
                em.set_author(name="{}, you already accepted the terms on {}".
                              format(ctx.message.author.display_name, ts_to_string(user_info['accept'])))
                await self.bot.say(embed=em)
                return
        # If not, creates wallet and stores accepted.
        address = user.create_wallet()
        info = {"accept": int(time.time()), "address": address}
        user.save(info)
        # TODO: safety, store an encrypted backup of the wallet elsewhere.
        msg = "Your {}: address is `{}`".format(EMOJIS['Bismuth'], info['address'])
        em = discord.Embed(description=msg, colour=discord.Colour.green())
        em.set_author(name="{}: Terms accepted".format(ctx.message.author.display_name))
        await self.bot.say(embed=em)


    @commands.command(name='terms', brief="Remind the current Pawer terms of use.", pass_context=True)
    async def terms(self, ctx):
        em = discord.Embed(description=DISCLAIMER, colour=discord.Colour.green())
        em.set_author(name="Current terms of use:")
        await self.bot.say(embed=em)

    @commands.command(name='terms', brief="Remind the current Pawer terms of use.", pass_context=True)
    async def terms(self, ctx):
        em = discord.Embed(description=DISCLAIMER, colour=discord.Colour.green())
        em.set_author(name="Current terms of use:")
        await self.bot.say(embed=em)

    @commands.command(name='graph', brief="Shows bismuth graphs: pools, diff, blocktime", pass_context=True)
    async def graph(self, ctx, type=''):
        urls = {'pools': ["Bismuth Pools estimated hashrate", 'https://hypernodes.bismuth.live/plots/hr.php'],
                'diff': ["Mainnet difficulty evolution", 'https://hypernodes.bismuth.live/plots/mainnet/diff.php'],
                'blocktime': ["Mainnnet blocktime evolution", 'https://hypernodes.bismuth.live/plots/mainnet/blocktime.php']}
        if type not in urls:
            msg = "\n".join(["`{}`: {}".format(a,b[0]) for a,b in urls.items()])
            em = discord.Embed(description=msg, colour=discord.Colour.red())
            em.set_author(name="Error: Please specify a graph type")
            await self.bot.say(embed=em)
        em = discord.Embed()
        em.set_image(url=urls[type][1])
        em.set_author(name=urls[type][0])
        await self.bot.say(embed=em)
