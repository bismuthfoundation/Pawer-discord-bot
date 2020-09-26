"""
Bismuth Hypernodes cogs
"""

import discord
import json
from discord.ext import commands
from distutils.version import LooseVersion
from modules.helpers import async_get
from modules.hypernodes_db import HypernodesDb
from os import path
import os, sys
import time

HN_STATUS_CACHE = 'users/status_ex.json'


class Hypernodes(commands.Cog):
    """Bismuth HN specific Cogs"""

    def __init__(self, bot):
        self.bot = bot
        self.bot.hypernodes_module = HypernodesDb()
        self.background_count = 0

    @staticmethod
    def fill(text, final_length, char=" "):
        return text + char * (final_length - len(text))

    @staticmethod
    async def _hn_status():
        """Returns cached (3 min) or live hn status"""
        if path.isfile(HN_STATUS_CACHE) and path.getmtime(HN_STATUS_CACHE) > time.time() - 3 * 60:
            with open(HN_STATUS_CACHE, 'r') as f:
                return json.load(f)
        url = 'https://hypernodes.bismuth.live/status_ex.json'
        response = await async_get(url, is_json=True)
        # converts list to dict, with ip as key for easier access
        response = {item[1]: item for item in response}
        with open(HN_STATUS_CACHE, 'w') as f:
            json.dump(response, f)
        return response

    async def hn_watch_list(self, user_info, for_print=False):
        hn_list = user_info.get('hn_watch', [])
        hn_status = await self._hn_status()
        hn_height = [(status[1], status[6]) for status in hn_status.values() if status[1] in hn_list]
        # Also add to global reverse index - lock?
        if for_print:
            return '\n'.join(["{} height {}".format(s[0], s[1]) for s in hn_height])
        return hn_height

    @commands.command()
    async def hypernodes(self, ctx):
        """Generic Hypernodes info"""
        
        response = await self._hn_status()
        status = {'active': 0, 'inactive': 0, 'active_collateral': 0,
                  'inactive_collateral': 0, 'total': 0, 'collateral': 0,
                  'latest_version': '0.0', 'latest_height': 0}
        for hn in response.values():
            # pos, ip, port, weight, registrar, reward, height, version, active
            #  0    1    2     3       4         5       6        7        8
            if hn[8] == 'Active':
                status['active'] += 1
                status['active_collateral'] += hn[3] * 10000
            else:
                status['inactive'] += 1
                status['inactive_collateral'] += hn[3] * 10000
            version = '0' if hn[7] == '?' else hn[7]
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
        await ctx.send(embed=em)

    @commands.group()
    async def hypernode(self, ctx):
        """Hypernode commands"""
        if ctx.invoked_subcommand is None:
            await ctx.send('hypernode needs a subcommand: watch, unwatch, list')

    @hypernode.command()
    async def label(self, ctx, hypernode, *description):
        """Add an description to the HN"""
        try:
            text = " ".join(description)

            self.bot.hypernodes_module.set_label(ctx.author.id, hypernode, text)

            await ctx.send("{} is now {}".format(hypernode, text))

        except Exception as e:
            print(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)

    @hypernode.command()
    async def watch(self, ctx, *hypernodes):
        """Add an HN to the watch list and warn via PM when down"""
        try:
            msg = ''
            for hypernode in hypernodes:
                if hypernode:
                    hn_status = await self._hn_status()
                    if hypernode not in hn_status:
                        # unknown ip
                        msg += "No known Hypernode with ip {}\n".format(hypernode)
                    else:
                        self.bot.hypernodes_module.watch(ctx.author.id, hypernode)
                        msg += "Added {}\n".format(hypernode)

            em = discord.Embed(description=msg, colour=discord.Colour.green())
            em.set_author(name="Hypernodes:")
            await ctx.send(embed=em)
        except Exception as e:
            print(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)

    @hypernode.command()
    async def unwatch(self, ctx, *hypernodes):
        """Removes an HN from the watch list"""
        msg = ''
        for hypernode in hypernodes:
            if hypernode:
                self.bot.hypernodes_module.unwatch(ctx.author.id, hypernode)
                msg += "Removed {}\n".format(hypernode)
        em = discord.Embed(description=msg, colour=discord.Colour.green())
        em.set_author(name="Hypernodes:")
        await ctx.send(embed=em)

    @hypernode.command()
    async def list(self, ctx):
        """shows your watch list"""
        hn_status = await self._hn_status()
        hn_list = {}
        for hn in self.bot.hypernodes_module.get_list(ctx.author.id):
            hn_list[hn[0]] = hn[1]
        hn_height = [(status[1], status[6]) for status in hn_status.values() if status[1] in hn_list]
        msg = "You are watching {} hypernode".format(len(hn_height))
        if len(hn_height) > 1:
            msg += "s"
        msg += "\n"

        for index, hn in enumerate(hn_height):
            char = "-"
            if hn[1] <= 0:
                char = "▸"
            text = "`{} {}   {} | {}`".format(char, self.fill(hn[0], 15), self.fill(str(hn[1]), 8), hn_list[hn[0]])
            if hn[1] <= 0:
                text = "**" + text + "**"
            msg += text+"\n"
            if not (index + 1) % 20:
                await ctx.send(msg)
                msg = ""

        await ctx.send(msg)

    @hypernode.command()
    async def recover(self, ctx, *hypernodes):
        """recovers your watch list"""

        hypernodes = " ".join(hypernodes)
        hypernodes = hypernodes.replace("▸", "-")
        hypernodes = hypernodes.split("-")
        ips = []
        labels = {}

        for hypernode in hypernodes:
            if "You are watching" in hypernode or not hypernode:
                continue
            ip, label = hypernode.split("|")
            ip = ip.split(" ")[1]
            label = label[1:]
            ips.append(ip)
            labels[ip] = label
        await self.watch.callback(self, ctx, *ips)

        for ip, label in labels.items():
            await self.label.callback(self, ctx, ip, label)

    async def background_task(self, bot=None):
        # Only run every 6 min
        self.background_count += 1

        if self.background_count < 6:
            return

        self.background_count = 0

        hn_status = await self._hn_status()
        await self.bot.hypernodes_module.update_nodes_status(hn_status, self.bot)
        await self.bot.hypernodes_module.get_nodes_status(self.bot)
