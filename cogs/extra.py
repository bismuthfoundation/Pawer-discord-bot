"""
Extra cogs
"""

# import requests
from discord.ext import commands
from modules.helpers import async_get


class Extra:
    """Useful cogs not Bismuth specific"""

    def __init__(self, bot):
        self.bot = bot

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
