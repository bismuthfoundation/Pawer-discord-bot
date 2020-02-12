"""
Extra cogs
"""

# import requests
import discord
from discord.ext import commands
from modules.helpers import async_get, User

class Extra:
    """Useful cogs not Bismuth specific"""

    def __init__(self, bot):
        self.bot = bot

    async def safe_send_message(self, recipient, message):
        try:
            await self.bot.send_message(recipient, message)
        except Exception as e:
            print(e)

    @commands.command(name='test', brief="test", pass_context=True)
    async def test(self, ctx):
        # print(ctx.message.content)
        await self.bot.say('test')

    @commands.command()
    async def ping(self):
        await self.bot.say('Pong')

    @commands.command(name='bitcoin', brief="Shows bitcoin price")
    async def bitcoin(self, pass_context=True):
        # TODO: cache
        url = 'https://api.coindesk.com/v1/bpi/currentprice/BTC.json'
        """
        response = requests.get(url)
        value = response.json()['bpi']['USD']['rate']
        """
        response = await async_get(url, is_json=True)
        value = response['bpi']['USD']['rate'].replace(',', '')
        # await client.send_message(discord.Object(id='502494064420061184'), "Bitcoin price is: " + value)
        await self.bot.say("Bitcoin price is {:0.2f} USD".format(float(value)))

    @commands.command(name='avah', brief="Show user avatar hash", pass_context=True)
    async def avah(self, ctx, who: discord.Member):
        # user = User(who)
        # print(User)
        message = "User avatar hash is {}".format(who.avatar)
        # TODO: list other users with this hash
        await self.bot.say(message)
        members = list(self.bot.get_all_members()) 
        for member in members:
            if member.avatar == who.avatar:
                await self.bot.say("Found for {}".format(member.mention))
