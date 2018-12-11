"""
Dragginator related cog

@Iyomisc
"""

import discord
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

    @dragg.command(name='buy', brief="Buy an egg with Bis - Current price is {} $BIS".format(EGG_PRICE), pass_context=True)
    async def buy(self, ctx):
        """Buy an egg with Bis"""
        user = User(ctx.message.author.id)
        user_info = user.info()
        result = user.send_bis_to(EGG_PRICE, "9ba0f8ca03439a8b4222b256a5f56f4f563f6d83755f525992fa5daf", check_balance=True)
        if result["txid"]:
            em = discord.Embed(description="Your egg is generating...\n Txid: {}".format(result["txid"]),
                               colour=discord.Colour.green())
        elif result["error"] == "LOW_BALANCE":
            em = discord.Embed(description="Sorry, but you don't have enough Bis to buy an egg ;( Current price is {} $BIS.".format(EGG_PRICE),
                               colour=discord.Colour.red())
        elif result["error"] == "NO_WALLET":
            em = discord.Embed(description="Sorry, but you have to create a wallet first: type `Pawer deposit`", colour=discord.Colour.red())
        else:
            em = discord.Embed(description="Something went wrong, Try again to see what append",
                               colour=discord.Colour.red())

        em.set_author(name="Get an egg with Bis")
        await self.bot.say(embed=em)

    async def background_task(self):
        # TODO
        return

        result = await get_users_from_addresses(['b938135d497bcb40f88622378b5701df0709838443fae66665dc1ac4'])
        print(result)

        member = _get_from_servers(self.bot, 'get_member_named', 'SySy#5290')

        await self.bot.send_message(member, 'boop')



    # badges (empty or address)


