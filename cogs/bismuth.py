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


class Bismuth:
    """Bismuth specific Cogs"""

    def __init__(self, bot):
        self.bot = bot
        self.bot.tip_module = Tips()

    async def safe_send_message(self, recipient, message):
        try:
            await self.bot.send_message(recipient, message)
        except Exception as e:
            print(e)

    async def bismuth_deprecated(self, ctx):
        # TODO: cache
        url = 'https://bismuth.ciperyho.eu/api/markets'
        response = await async_get(url, is_json=True)
        cryptopia = response['markets']['Cryptopia']
        qtrade = response['markets']['QTrade']
        # await client.send_message(discord.Object(id='502494064420061184'), "Bitcoin price is: " + value)
        await self.bot.say("{} price is:\n▸ {:0.8f} BTC or {:0.2f} USD on Cryptopia\n▸ {:0.8f} BTC or {:0.2f} USD on QTrade"
                           .format(EMOJIS['Bismuth'], cryptopia['BTC']['lastPrice'], cryptopia['USD']['lastPrice'],
                                   qtrade['BTC']['lastPrice'], qtrade['USD']['lastPrice']))

    @commands.command(name='bismuth', brief="Shows bismuth price", pass_context=True)
    async def bismuth(self, ctx):
        MARKETS = ["qtrade", "vinex", "graviex"]  # Markets we want to list
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
        # await client.send_message(discord.Object(id='502494064420061184'), "Bitcoin price is: " + value)
        await self.bot.say("{} price is:\n{}".format(EMOJIS['Bismuth'], prices))

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
        try:
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
        except Exception as e:
            print(str(e))
            # Send a PM to the sender or answer if dedicated channel
            await self.bot.add_reaction(ctx.message, '👎')  # Thumb down

    @commands.command(name='tip', brief="Tip a user, default 1 bis, min 0.1, max 50 BIS", pass_context=True)
    async def tip(self, ctx, who_to_tip: discord.Member, amount: str='1'):
        try:
            amount = float(amount)
            if amount > 50:
                amount = 50
                await self.bot.say("Maw tip amount too high, lowering to 50 {}".format(EMOJIS['Bismuth']))

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
                    message = "Hi {}, {} wanted to tip you, but you do not have a Discord Bismuth wallet yet.\n"\
                              .format(who_to_tip.display_name, ctx.message.author.display_name)
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
                    await self.bot.add_reaction(ctx.message, '👍')  # Thumb up
                    message = "Yeah! You've been tipped {:0.2f} {} by {} ({}) from the Bismuth discord!"\
                              .format(amount, EMOJIS['Bismuth'], ctx.message.author, ctx.message.author.display_name)
                    await self.safe_send_message(who_to_tip, message)

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

    @commands.command(name='rain', brief="Distribute a given amount between n users", pass_context=True)
    async def rain(self, ctx, total_amount: str='10', how_many_users: str='10'):
        try:
            if "/" in total_amount:
                data = total_amount.split("/")
                total_amount = float(data[0])
                how_many_users = float(data[1])
            total_amount = float(total_amount)
            how_many_users = int(how_many_users)

            if how_many_users > 100:
                how_many_users = 100
            if how_many_users < 1:
                how_many_users = 1

            if total_amount > 1000:
                total_amount = 1000
            if total_amount < 0.1 * how_many_users:
                how_many_users = int(total_amount/0.1)
            individual_amount = total_amount/how_many_users
            user = User(ctx.message.author.id)

            user_info = user.info()
            if user_info and user_info['address']:
                balance = float(user.balance())
                msg = "{} rain {} bis to {} users, balance is {} ".format(ctx.message.author.display_name, total_amount,
                                                                          how_many_users, balance)
                print(msg)
                if balance < total_amount + 0.01 * how_many_users:
                    print("balance too low")
                    await self.bot.add_reaction(ctx.message, '😟')
                    return

                registered_members = []
                unregistered_members = []
                for member in self.bot.get_all_members():
                    if str(member.status) != "offline" and not member.bot and member.name != ctx.message.author.name:
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
                    .format(individual_amount, EMOJIS['Bismuth'], ctx.message.author, ctx.message.author.display_name)
                final_message = "{} sent {:0.2f} {} each to: ".format(ctx.message.author.mention, individual_amount, EMOJIS['Bismuth'])
                self.bot.tip_module.start_rain(user_info['address'], individual_amount*how_many_real_users, how_many_real_users, "rain")
                for current_member in registered_members[:how_many_real_users]:
                    to_address = User(current_member.id).info()['address']
                    user.send_bis_to(individual_amount, to_address)
                    self.bot.tip_module.tip(user_info['address'], to_address, individual_amount, "rain")
                    final_message += current_member.mention + " "
                    await self.safe_send_message(current_member, message)
                await self.bot.say(final_message)
                await self.bot.add_reaction(ctx.message, '👍')  # Thumb up

                for current_member in unregistered_members[:10]:
                    message = "Hi {}, {} launched a rain, but you do not have a Discord Bismuth wallet yet.\n" \
                        .format(current_member.display_name, ctx.message.author.display_name)
                    message += "It's easy, you just have to type `Pawer deposit` here to read and accept the terms.\n"
                    message += "Then you'll have an address of yours and be able to receive tips and play with me.\n"
                    message += "Use `Pawer help` to get a full list of what I can do."
                    await self.safe_send_message(current_member, message)

                return

            # Depending on channel, say or send PM
            em = discord.Embed(description=DISCLAIMER, colour=discord.Colour.red())
            em.set_author(name="You have to create your address first:")
            await self.bot.say(embed=em)
        except Exception as e:
            print(str(e))
            # Send a PM to the sender or answer if dedicated channel
            await self.bot.add_reaction(ctx.message, '👎')  # Thumb down@commands.command(name='rain', brief="Distribute a given amount between n users", pass_context=True)

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
                send = user.send_bis_to(amount, address, data=message)
                txid = send['txid']
                print("txid", txid)
                if txid:
                    # answer by reaction not to pollute
                    await self.bot.add_reaction(ctx.message, '👍')  # Thumb up
                    await self.bot.say("Done, txid is {}.".format(txid))
                else:
                    await self.bot.add_reaction(ctx.message, '👎')  # Thumb down
                    await self.bot.say("Error {}".format(send['error']))
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

    @commands.command(name='operation', brief="Send a generic 'operation' transaction, with an optional message", pass_context=True)
    async def operation(self, ctx, operation: str, address:str, amount: str,  message: str=''):
        # TODO: too much code in common with withdraw, factorize somehow.
        try:
            amount = float(amount)
            user = User(ctx.message.author.id)
            user_info = user.info()
            # Check the address looks ok
            if not BismuthUtil.valid_address(address):
                print("address error")
                await self.bot.add_reaction(ctx.message, '😟')
                await self.bot.say("Address does not look ok. Command is `Pawer operation <operation> <address> <amount> [message]`")
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
                send = user.send_bis_to(amount, address, data=message, operation=operation)
                txid = send['txid']
                print("txid", txid)
                if txid:
                    # answer by reaction not to pollute
                    await self.bot.add_reaction(ctx.message, '👍')  # Thumb up
                    await self.bot.say("Done, txid is {}.".format(txid))
                else:
                    await self.bot.add_reaction(ctx.message, '👎')  # Thumb down
                    await self.bot.say("Error {}".format(send['error']))
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

    @commands.command(name='bisurl', brief="Decode a transaction from a BIS URL. Append SEND to effectively send the tx.", pass_context=True)
    async def bisurl(self, ctx, bisurl: str, send: str='NO'):
        # TODO: too much code in common with withdraw, factorize somehow.
        try:
            try:
                decode = BismuthUtil.read_url(bisurl)
            except Exception as e:
                await self.bot.add_reaction(ctx.message, '😢')  # Crying
                await self.bot.say("Does not look like a proper BIS URL")
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
                await self.bot.say(embed=em)
            else:
                title = "Decoded BIS URL: (**not** sent)"
                decoded += " \nPaste this command again and append ` SEND` if you want to send that transaction.\n"
                em = discord.Embed(description=decoded, colour=discord.Colour.green())
                em.set_author(name=title)
                await self.bot.say(embed=em)
                return

            user = User(ctx.message.author.id)
            user_info = user.info()
            # Check the address looks ok
            if not BismuthUtil.valid_address(decode['recipient']):
                print("address error")
                await self.bot.add_reaction(ctx.message, '😟')
                await self.bot.say("Address does not look ok. Command is `Pawer operation <operation> <address> <amount> [message]`")
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
                send = user.send_bis_to(amount, address, data=message, operation=operation)
                txid = send['txid']
                print("txid", txid)
                if txid:
                    # answer by reaction not to pollute
                    await self.bot.add_reaction(ctx.message, '👍')  # Thumb up
                    await self.bot.say("Done, txid is {}.".format(txid))
                else:
                    await self.bot.add_reaction(ctx.message, '👎')  # Thumb down
                    await self.bot.say("Error {}".format(send['error']))
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

    @commands.command(name='sign', brief="Sign a message from your wallet, for off-chain use", pass_context=True)
    async def sign(self, ctx, message: str):
        try:
            user = User(ctx.message.author.id)
            user_info = user.info()
            if user_info and user_info['address']:
                # User exists and validated the terms, has an address
                # Make sure balance is enough
                res = user.sign_message(message)
                sign = res['sign']
                # print("sign", sign)
                if sign:
                    # answer by reaction not to pollute
                    await self.bot.add_reaction(ctx.message, '👍')  # Thumb up
                    await self.bot.say("Signature is `{}`.".format(sign))
                else:
                    await self.bot.add_reaction(ctx.message, '👎')  # Thumb down
                    await self.bot.say("Error {}".format(res['error']))
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

        self.bot.tip_module.add_user(address, ctx.message.author.id, ctx.message.author.display_name)

        # TODO: safety, store an encrypted backup of the wallet elsewhere.
        msg = "Your {} address is `{}`".format(EMOJIS['Bismuth'], info['address'])
        em = discord.Embed(description=msg, colour=discord.Colour.green())
        em.set_author(name="{}: Terms accepted".format(ctx.message.author.display_name))
        await self.bot.say(embed=em)

    @commands.command(name='terms', brief="Remind the current Pawer terms of use.", pass_context=True)
    async def terms(self, ctx):
        em = discord.Embed(description=DISCLAIMER, colour=discord.Colour.green())
        em.set_author(name="Current terms of use:")
        await self.bot.say(embed=em)

    @commands.command(name='graph', brief="Shows bismuth graphs: pools, diff, blocktime, hypernodes", pass_context=True)
    async def graph(self, ctx, type=''):
        urls = {'pools': ["Bismuth Pools estimated hashrate", 'https://hypernodes.bismuth.live/plots/hr.php'],
                'diff': ["Mainnet difficulty evolution", 'https://hypernodes.bismuth.live/plots/mainnet/diff.php'],
                'hypernodes': ["Number of 10k equivalent HN per round", 'https://hypernodes.bismuth.live/plots/posnet/weight.php'],
                'blocktime': ["Mainnnet blocktime evolution", 'https://hypernodes.bismuth.live/plots/mainnet/blocktime.php']}
        if type not in urls:
            msg = "\n".join(["`{}`: {}".format(a,b[0]) for a, b in urls.items()])
            em = discord.Embed(description=msg, colour=discord.Colour.red())
            em.set_author(name="Error: Please specify a graph type")
            await self.bot.say(embed=em)
        em = discord.Embed()
        em.set_image(url=urls[type][1])
        em.set_author(name=urls[type][0])
        await self.bot.say(embed=em)

    @commands.command(name='board', brief="Shows stats of given action: tip/rain", pass_context=True)
    async def board(self, ctx, action:str):

        with open("data/tips.json") as f:
            data = json.load(f)
        if action not in data:
            await self.bot.say("unknown action")
            return
        msg = "__Who gave the most:__\n\n"
        for user in data[action]["from"]:
            msg += "{} gave {:0.2f} Bis\n".format(get(self.bot.get_all_members(), id=str(user[2])).display_name, user[0])

        msg += "\n\n__Who received the most:__\n\n"
        for user in data[action]["to"]:
            msg += "{} received {:0.2f} Bis\n".format(get(self.bot.get_all_members(), id=str(user[2])).display_name, user[0])

        em = discord.Embed(description=msg, colour=discord.Colour.green())
        em.set_author(name="{} board".format(action))
        await self.bot.say(embed=em)
