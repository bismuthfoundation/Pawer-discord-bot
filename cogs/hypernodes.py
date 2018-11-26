"""
Bismuth Hypernodes cogs
"""

""

import requests
from discord.ext import commands


class Hypernodes:
    """Bismuth HN specific Cogs"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='hypernodes', brief="Generic Hypernodes info", pass_context=True)
    async def hypernodes(self, ctx):
        # TODO: cache
        # Need more complete api - ongoing thanks to @gh2
        url = 'https://hypernodes.bismuth.live/status.json'
        response = requests.get(url).json()
        active = 0
        inactive = 0
        for hn, height in response.items():
            if height > 0:
                active +=1
            else:
                inactive += 1
        await self.bot.say(":bis: Hypernodes: {} active, {} inactives".format(active, inactive))

    @commands.group(name='hypernode', brief="Hypernode commands", pass_context=True)
    async def hypernode(self, ctx):
        if ctx.invoked_subcommand is None:
            await self.bot.say('TODO No, {0.subcommand_passed} is not cool'.format(ctx))

    @hypernode.command(name='watch', brief="WIP - Add an HN to the watch list and warn via PM when down", pass_context=True)
    async def watch(self, ctx, *, hypernode: str):
        """TODO"""
        """print(ctx.__dict__)  # 
        for arg in ctx.args:
            print(arg, arg.__dict__)
        """
        await self.bot.say("TODO watch - {}".format(hypernode))
