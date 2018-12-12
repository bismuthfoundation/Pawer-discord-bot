"""
Dragginator related cog

@Iyomisc
"""
import datetime
import discord
import os
import json
from discord.ext import commands
from modules.helpers import User, async_get
from cogs.bismuth import get_users_from_addresses

# Current Draggon Egg price in BIS
EGG_PRICE = 2


def _get_from_servers(bot, getter, argument):
    result = None
    for server in bot.servers:
        result = getattr(server, getter)(argument)
        if result:
            return result
    return result


class Dragginator:
    """Dragginator Cogs"""

    def __init__(self, bot):
        self.bot = bot
        self.background_count = 15
        if not os.path.exists("data/dragginator.json"):
            open("data/dragginator.json", "w").write('{"last_day":""}')

    @commands.group(name='dragg', brief="Dragginator commands", pass_context=True)
    async def dragg(self, ctx):
        if ctx.invoked_subcommand is None:
            await self.bot.say('Commands for Dragginator'.format(ctx))

    @dragg.command(name='list', brief="List your eggs", pass_context=True)
    async def list(self, ctx):
        """List eggs for current user"""
        user = User(ctx.message.author.id)
        user_info = user.info()
        address = user_info['address']
        # await self.bot.say("Eggs of {}".format(address))
        eggs = await async_get("https://dragginator.com/api/info.php?address={}&type=list".format(address),
                               is_json=True)
        msg = ""
        for egg in eggs:
            msg += "- {}\n".format(egg["dna"])
        em = discord.Embed(description=msg, colour=discord.Colour.green())
        em.set_author(name="Eggs of {}".format(address))
        await self.bot.say(embed=em)

    @dragg.command(name='eggdrop', brief="Register to the current eggdrop (only if you don't have any egg)",
                   pass_context=True)
    async def eggdrop(self, ctx):
        """Auto register for the eggdrop"""
        user = User(ctx.message.author.id)
        user_info = user.info()

        data = await async_get(
            "https://dragginator.com/api/info.php?address={}&type=eggdrop".format(user_info['address']), is_json=True)
        if data[0] == "registered":
            msg = "You are already registered to the eggdrop"
        elif data[0]:
            msg = "The word is {}\n".format(data[1])
            if float(user.balance()) >= 0.01:
                result = user.send_bis_to(0, "9ba0f8ca03439a8b4222b256a5f56f4f563f6d83755f525992fa5daf", data=data[1])
                msg += "txid: {}".format(result['txid'])
            else:
                msg += "Not enough Bis to afford the fees ;("
        else:
            msg = "Sorry, but you already own {} eggs".format(str(data[1]))
        em = discord.Embed(description=msg, colour=discord.Colour.green())
        em.set_author(name="Eggdrop")
        await self.bot.say(embed=em)

    @dragg.command(name='buy', brief="Buy an egg with Bis - Current price is {} $BIS".format(EGG_PRICE),
                   pass_context=True)
    async def buy(self, ctx):
        """Buy an egg with Bis"""
        user = User(ctx.message.author.id)
        user_info = user.info()
        result = user.send_bis_to(EGG_PRICE, "9ba0f8ca03439a8b4222b256a5f56f4f563f6d83755f525992fa5daf",
                                  check_balance=True)
        if result["txid"]:
            em = discord.Embed(description="Your egg is generating...\n Txid: {}".format(result["txid"]),
                               colour=discord.Colour.green())
        elif result["error"] == "LOW_BALANCE":
            em = discord.Embed(
                description="Sorry, but you don't have enough Bis to buy an egg ;( Current price is {} $BIS.".format(
                    EGG_PRICE),
                colour=discord.Colour.red())
        elif result["error"] == "NO_WALLET":
            em = discord.Embed(description="Sorry, but you have to create a wallet first: type `Pawer deposit`",
                               colour=discord.Colour.red())
        else:
            em = discord.Embed(description="Something went wrong, Try again to see what append",
                               colour=discord.Colour.red())

        em.set_author(name="Get an egg with Bis")
        await self.bot.say(embed=em)

    @dragg.command(name='claim', brief="Claim a free egg for the advent calendar, only if you already have an egg",
                   pass_context=True)
    async def claim(self, ctx):
        user = User(ctx.message.author.id)
        user_info = user.info()

        data = await async_get(
            "https://dragginator.com/api/info.php?type=calendar&address={}".format(user_info['address']), is_json=True)

        colour = discord.Colour.red()

        if int(data[1]) == 0:
            msg = "Sorry, but you don't own any egg"
        elif int(data[2]) > 0:
            msg = "Sorry, but you already claimed an egg today"

        elif user_info['address'][:2] in data[0]:
            msg = "Your address matches with one of today seeds\n"
            if float(user.balance()) >= 0.01:
                txid = user.send_bis_to(0, "9ba0f8ca03439a8b4222b256a5f56f4f563f6d83755f525992fa5daf",
                                        operation="dragg:claim")["txid"]
                msg += "txid: {}".format(txid)
                colour = discord.Colour.green()
            else:
                msg += "Not enough Bis to afford the fees ;("

        else:
            msg = "Sorry, but your address doesn't match with any of today's seeds"
        em = discord.Embed(description=msg, colour=colour)
        em.set_author(name="Advent calendar")
        await self.bot.say(embed=em)

    async def background_task(self):
        # Only run every 15 min
        self.background_count += 1
        if self.background_count < 14:
            return
        self.background_count = 0

        today = datetime.datetime.now()
        if int(today.strftime("%H")) < 3:
            return

        with open("data/dragginator.json") as f:
            data = json.load(f)
        today = today.strftime("%Y-%m-%d")
        if today == data["last_day"]:
            return

        winners = await async_get("https://dragginator.com/api/info.php?type=calendar&address=list", is_json=True)
        result = await get_users_from_addresses(winners)
        for address, discord_id in result.items():
            member = _get_from_servers(self.bot, 'get_member', discord_id)
            await self.bot.send_message(member,"Hey, It seems than you can claim a free egg today!\n"
                                               "Just type `pawer dragg claim`, and you'll get a free egg")

        data["last_day"] = today
        with open("data/dragginator.json", "w") as f:
            json.dump(data, f)

    # badges (empty or address)


