"""
Bismuth Hypernodes cogs
"""

""

# import requests
import discord
import json
from discord.ext import commands
from distutils.version import LooseVersion
from modules.helpers import User, async_get
from modules.config import EMOJIS
from os import path

HN_STATUS_CACHE = 'users/status_ex.json'

class Hypernodes:
    """Bismuth HN specific Cogs"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='hypernodes', brief="Generic Hypernodes info",
                      pass_context=True)
    async def hypernodes(self, ctx):
        response = await self.hn_status
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
               "▸ {} Active Hypernodes, {} {} total active collateral"
               .format(status['active'], status['active_collateral'], '$BIS'),
               "▸ Estimated weekly reward for 10K Collateral is {} {}".format(per_week_10k, '$BIS'),
               "▸ Estimated yearly ROI {:0.1f}%".format(per_year_30k * 100 / 30000)
               )
        msg = "\n".join(msg)
        em = discord.Embed(description=msg, colour=discord.Colour.green())
        em.set_author(name="{} registered Hypernodes with {} total BIS collateral".
                      format(status['total'], status['collateral']))
        await self.bot.say(embed=em)

    @property
    async def hn_status(self):
        """Returns cached or live hn status"""
        if path.isfile(HN_STATUS_CACHE) and path.getmtime(HN_STATUS_CACHE):
            with open(HN_STATUS_CACHE, 'r') as f:
                return json.load(f)
        url = 'https://hypernodes.bismuth.live/status_ex.json'
        response = await async_get(url, is_json=True)
        with open(HN_STATUS_CACHE, 'w') as f:
            json.dump(response, f)
        return response

    @commands.group(name='hypernode', brief="Hypernode commands", pass_context=True)
    async def hypernode(self, ctx):
        if ctx.invoked_subcommand is None:
            await self.bot.say('TODO No, {0.subcommand_passed} is not cool'.format(ctx))

    async def hn_watch_list(self, user_info, for_print=False):
        hn_list = user_info.get('hn_watch', [])
        hn_status = self.hn_status
        hn_height = [(status[1], status[6]) for status in hn_status if status[1] in hn_list]
        # Also add to global reverse index - lock?
        if for_print:
            return '\n'.join(["{} height {}".format(s[0], s[1]) for s in hn_height])
        return hn_height

    @hypernode.command(name='watch', brief="WIP - Add an HN to the watch list and warn via PM when down",
                       pass_context=True)
    async def watch(self, ctx, *, hypernode: str=''):
        """Adds a hn to watch, print the current list"""
        user = User(ctx.message.author.id)
        user_info = user.info()
        msg = ''
        if hypernode:
            # add the hhn to the list
            if hypernode not in user_info.get('hn_watch', []):
                watch =  user_info.get('hn_watch', [])
                watch.append(hypernode)
                # TODO: add to reverse index
                user_info['hn_watch'] = watch
                msg = "Added {}\n".format(hypernode)
                user.save(user_info)
        watch_list = await self.hn_watch_list(user_info, for_print=True)
        msg += watch_list
        em = discord.Embed(description=msg, colour=discord.Colour.green())
        em.set_author(name="You're watching...")
        await self.bot.say(embed=em)

    @hypernode.command(name='unwatch', brief="WIP - Removes an HN from the watch list",
                       pass_context=True)
    async def watch(self, ctx, *, hypernode: str=''):
        """Adds a hn to watch, print the current list"""
        user = User(ctx.message.author.id)
        user_info = user.info()
        msg = ''
        if hypernode:
            # add the hhn to the list
            if hypernode in user_info.get('hn_watch', []):
                watch =  user_info.get('hn_watch', [])
                watch = [hn for hn in watch if hn != hypernode]
                # TODO: add to reverse index
                user_info['hn_watch'] = watch
                msg = "Removed {}\n".format(hypernode)
                user.save(user_info)
        watch_list = await self.hn_watch_list(user_info, for_print=True)
        msg += watch_list
        em = discord.Embed(description=msg, colour=discord.Colour.green())
        em.set_author(name="You're watching...")
        await self.bot.say(embed=em)
