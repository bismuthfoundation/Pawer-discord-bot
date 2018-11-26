"""
Extra cogs
"""

import requests
from discord.ext import commands

from modules.config import CONFIG
from modules.helpers import is_channel


class Extra:
    """Useful cogs not Bismuth specific"""

    def __init__(self, bot):
        self.bot = bot

    @is_channel(CONFIG['bot_channel'])
    @commands.command(name='test', brief="test", pass_context=True)
    async def test(self, ctx):
        # print(ctx.message.content)
        await self.bot.say('test')

    @commands.command()
    @is_channel(CONFIG['bot_channel'])
    async def ping(self):
        await self.bot.say('Pong')

    @is_channel(CONFIG['bot_channel'])
    @commands.command(name='bitcoin', brief="Shows bitcoin price")
    async def bitcoin(self, pass_context=True):
        # TODO: cache
        url = 'https://api.coindesk.com/v1/bpi/currentprice/BTC.json'
        response = requests.get(url)
        value = response.json()['bpi']['USD']['rate']
        # await client.send_message(discord.Object(id='502494064420061184'), "Bitcoin price is: " + value)
        await self.bot.say("Bitcoin price is {:0.2f} USD".format(value))
