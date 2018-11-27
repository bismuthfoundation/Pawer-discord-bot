"""
Bismuth Hypernodes cogs
"""

""

# import requests
import discord
from discord.ext import commands
from distutils.version import LooseVersion
from modules.helpers import async_get


class Hypernodes:
    """Bismuth HN specific Cogs"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='hypernodes', brief="Generic Hypernodes info",
                      pass_context=True)
    async def hypernodes(self, ctx):
        # TODO: quick cache?
        url = 'https://hypernodes.bismuth.live/status_ex.json'
        response = await async_get(url, is_json=True)
        status = {'active': 0, 'inactive': 0, 'active_collateral': 0,
                  'inactive_collateral': 0, 'total': 0, 'collateral': 0,
                  'latest_version': '0.0', 'latest_height': 0}
        for hn in response:
            # pos, ip, port, weight, registrar, reward, height, version, active
            #  0    1    2     3       4         5       6        7        8
            if hn[8] == 'Active':
                status['active'] += 1
                status['active_collateral'] += hn[3] * 10000
            else:
                status['inactive'] += 1
                status['inactive_collateral'] += hn[3] * 10000
            version = '0' if hn[7]=='?' else hn[7]
            if LooseVersion(version) >= LooseVersion(status['latest_version']):
                status['latest_version'] = hn[7]
            height = 0 if not hn[6] else int(hn[6])
            if height >= status['latest_height']:
                status['latest_height'] = height
        status['total'] = status['active'] + status['inactive']
        status['collateral'] = status['active_collateral'] + status['inactive_collateral']

        url = "https://hypernodes.bismuth.live/est_rewards.json"
        response = await async_get(url, is_json=True)
        per_week_10k = float(response['10k']['week'])
        per_year_30k = float(response['30k']['year'])

        msg = ("▸ Hypernodes version is {}".format(status['latest_version']),
               "▸ PoS chain height is {}".format(status['latest_height']),
               "▸ {} Active Hypernodes, {} :bis: total active collateral"
               .format(status['active'], status['active_collateral']),
               "▸ Estimated weekly reward for 10K Collateral is {} :bis:".format(per_week_10k),
               "▸ Estimated yearly ROI {:0.1f}%".format(per_year_30k * 100 / 30000)
               )
        msg = "\n".join(msg)
        em = discord.Embed(description=msg, colour=discord.Colour.green())
        em.set_author(name="{} registered Hypernodes with {} total BIS collateral".
                      format(status['total'], format(status['collateral'])))
        await self.bot.say(embed=em)

    @commands.group(name='hypernode', brief="Hypernode commands", pass_context=True)
    async def hypernode(self, ctx):
        if ctx.invoked_subcommand is None:
            await self.bot.say('TODO No, {0.subcommand_passed} is not cool'.format(ctx))

    @hypernode.command(name='watch', brief="WIP - Add an HN to the watch list and warn via PM when down",
                       pass_context=True)
    async def watch(self, ctx, *, hypernode: str):
        """TODO"""
        """print(ctx.__dict__)  # 
        for arg in ctx.args:
            print(arg, arg.__dict__)
        """
        await self.bot.say("TODO watch - {}".format(hypernode))
