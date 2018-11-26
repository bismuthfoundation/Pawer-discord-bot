"""
Bismuth related cog
"""

""

import requests
from modules.config import CONFIG
from discord.ext import commands
from modules.helpers import is_channel




class Bismuth:
    """Bismuth specific Cogs"""

    def __init__(self, bot):
        self.bot = bot

    @is_channel(CONFIG['bot_channel'])
    @commands.command(name='bismuth', brief="Shows bismuth price", pass_context=True)
    async def bismuth(self, ctx):
        # TODO: cache
        url = 'https://bismuth.ciperyho.eu/api/markets'
        response = requests.get(url)
        cryptopia = response.json()['markets']['Cryptopia']
        qtrade = response.json()['markets']['QTrade']
        # await client.send_message(discord.Object(id='502494064420061184'), "Bitcoin price is: " + value)
        await self.bot.say(":bis: price is {:0.8f} BTC or {:0.2f} USD on Cryptopia".format(cryptopia['BTC']['lastPrice'],
                                                                                         cryptopia['USD']['lastPrice']))
        await self.bot.say(":bis: price is {:0.8f} BTC or {:0.2f} USD on QTrade".format(qtrade['BTC']['lastPrice'],
                                                                                      qtrade['USD']['lastPrice']))
