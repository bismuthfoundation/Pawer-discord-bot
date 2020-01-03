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
from random import shuffle
# Current Draggon Egg price in BIS
EGG_PRICE = 3
DISCLAIMER = """By creating a Bismuth address on this service, you acknowledge that:
- This is meant to be used for tips, thanks you, quick experiments and other small amount usage.
- The matching wallet private key is stored on a secret online server, team operated.
- The team does not hold any responsability if your wallet or funds are lost.
Basically, you're using this service at your own risks.

Type `Pawer accept` to say you understand and proceed."""


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
        if not os.path.exists("data"):
            os.system("mkdir data")

        if not os.path.exists("data/dragginator.json"):
            open("data/dragginator.json", "w").write('{"last_day":""}')

    async def safe_send_message(self, recipient, message):
        try:
            await self.bot.send_message(recipient, message)
        except Exception as e:
            print(e)

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

    """ 
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
    """

    @dragg.command(name='eggrain', brief="Distribute a given amount of eggs between n users (cost 3 bis per user)",
                   pass_context=True)
    async def eggrain(self, ctx, how_many_users: str = '5'):
        try:
            how_many_users = int(how_many_users)

            if how_many_users > 100:
                how_many_users = 100
            if how_many_users < 1:
                how_many_users = 1

            user = User(ctx.message.author.id)
            user_info = user.info()
            if user_info and user_info['address']:
                balance = float(user.balance())
                msg = "{} rain {} eggs to {} users, balance is {} ".format(ctx.message.author.display_name,
                                                                           how_many_users, how_many_users, balance)
                print(msg)
                if balance < how_many_users * (EGG_PRICE + 0.011):
                    print("balance too low")
                    await self.bot.add_reaction(ctx.message, '😟')
                    return

                registered_members = []
                unregistered_members = []
                for member in self.bot.get_all_members():
                    if str(member.status) != "offline" and not member.bot and member.name != ctx.message.author.name:
                        # print(member.name, member.status, member.bot)
                        current_user = User(member.id)
                        member_info = current_user.info()
                        if member_info and member_info["address"]:
                            registered_members.append(member)
                        else:
                            unregistered_members.append(member)

                how_many_real_users = (min(how_many_users, len(registered_members)))
                shuffle(registered_members)
                shuffle(unregistered_members)

                message = "Yeah! You got a draggon egg from the rain of {} ({}) from the Bismuth discord!" \
                    .format(ctx.message.author, ctx.message.author.display_name)
                final_message = "{} sent a draggon egg to: ".format(ctx.message.author.mention)
                self.bot.tip_module.start_rain(user_info['address'], how_many_real_users, how_many_real_users, "eggrain")
                for current_member in registered_members[:how_many_real_users]:
                    user.send_bis_to(EGG_PRICE, "9ba0f8ca03439a8b4222b256a5f56f4f563f6d83755f525992fa5daf",
                                     operation="dragg:gift", data=User(current_member.id).info()['address'])
                    self.bot.tip_module.tip(user_info['address'], User(current_member.id).info()['address'], 1, "eggrain")
                    final_message += current_member.mention + " "
                    await self.safe_send_message(current_member, message)
                await self.bot.say(final_message)
                await self.bot.add_reaction(ctx.message, '👍')  # Thumb up

                for current_member in unregistered_members[:10]:
                    message = "Hi {}, {} launched a draggon eggs rain, but you do not have a Discord Bismuth wallet yet.\n" \
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
            await self.bot.add_reaction(ctx.message, '👎')  # Thumb down

    @dragg.command(name='see', brief="show the specified egg/draggon", pass_context=True)
    async def see(self, ctx, dna: str, egg_or_draggon: str="egg"):
        data = await async_get(
            "https://dragginator.com/api/pawer/see_api.php?dna={}&type={}".format(dna, egg_or_draggon), is_json=True)

        em = discord.Embed()
        if "url" in data:
            em.set_image(url=data["url"])
        em.set_author(name=data["title"])
        await self.bot.say(embed=em)

    @dragg.command(name='cup', brief="Give informations about the cup", pass_context=True)
    async def cup(self, ctx):

        user = User(ctx.message.author.id)
        user_info = user.info()
        data = await async_get(
            "https://dragginator.com/api/cup/address/?address={}?raw=1".format(user_info['address']), is_json=True)
        em = discord.Embed(description=data["message"], colour=discord.Colour.green())
        em.set_author(name=data["title"])
        await self.bot.say(embed=em)

    @dragg.command(name='leagues', brief="Give informations about the leagues", pass_context=True)
    async def leagues(self, ctx, *dna):
        user = User(ctx.message.author.id)
        user_info = user.info()
        if len(dna) and dna[0] == "register":

            result = user.send_bis_to(0, "9ba0f8ca03439a8b4222b256a5f56f4f563f6d83755f525992fa5daf", data=dna[1],
                                      operation="dragg:leagues", check_balance=True)

            if result["txid"]:
                em = discord.Embed(description="The Dna is now registered!\n Txid: {}".format(result["txid"]),
                                   colour=discord.Colour.green())
            elif result["error"] == "LOW_BALANCE":
                em = discord.Embed(
                    description="Sorry, but you don't have enough Bis to afford the fees", colour=discord.Colour.red())
            elif result["error"] == "NO_WALLET":
                em = discord.Embed(description="Sorry, but you have to create a wallet first: type `Pawer deposit`",
                                   colour=discord.Colour.red())
            else:
                em = discord.Embed(description="Something went wrong, Try again to see what append",
                                   colour=discord.Colour.red())

            em.set_author(name="")
            await self.bot.say(embed=em)
            return
        if len(dna):
            dna = dna[0]
        else:
            dna = ""
        data = await async_get(
            "https://dragginator.com/api/pawer/leagues_api.php?address={}&dna={}".format(user_info['address'], dna),
            is_json=True)
        em = discord.Embed(description=data["message"], colour=discord.Colour.green())
        em.set_author(name=data["title"])
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
            await self.bot.send_message(member, "Hey, It seems than you can claim a free egg today!\n"
                                               "Just type `pawer dragg claim`, and you'll get a free egg")

        data["last_day"] = today
        with open("data/dragginator.json", "w") as f:
            json.dump(data, f)

    # badges (empty or address)
