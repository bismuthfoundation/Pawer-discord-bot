"""
Extra cogs
"""

import discord
from discord.ext import commands
from modules.helpers import async_get
from json import loads as json_loads


class Extra(commands.Cog):
    """Useful cogs not Bismuth specific"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        """Pong"""
        await ctx.send('Pong')

    @commands.command()
    async def bitcoin(self, ctx):
        """Shows bitcoin price"""
        # TODO: cache
        url = 'https://api.coindesk.com/v1/bpi/currentprice/BTC.json'
        """
        response = requests.get(url)
        value = response.json()['bpi']['USD']['rate']
        """
        response = json_loads(await async_get(url))
        value = response['bpi']['USD']['rate'].replace(',', '')
        await ctx.send("Bitcoin price is {:0.2f} USD".format(float(value)))

    @commands.command()
    async def avah(self, ctx, who: discord.Member):
        """Show user avatar hash"""

        message = "User avatar hash is {}".format(who.avatar)
        # TODO: list other users with this hash
        await ctx.send(message)
        members = list(self.bot.get_all_members()) 
        for member in members:
            if member.avatar == who.avatar:
                await ctx.send("Found for {}".format(member.mention))
