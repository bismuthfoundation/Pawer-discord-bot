"""
Bismuth related cog
"""

import json
import time

import discord
import requests
from discord.ext import commands

# from modules.config import CONFIG
from modules.helpers import User, ts_to_string

"""
Potential todo:
    play paper / rock / scissor
    play zircodice
    mining rentability calc
"""


class Bismuth:
    """Bismuth specific Cogs"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='bismuth', brief="Shows bismuth price", pass_context=True)
    async def bismuth(self, ctx):
        # TODO: cache
        url = 'https://bismuth.ciperyho.eu/api/markets'
        response = requests.get(url)
        cryptopia = response.json()['markets']['Cryptopia']
        qtrade = response.json()['markets']['QTrade']
        # await client.send_message(discord.Object(id='502494064420061184'), "Bitcoin price is: " + value)
        await self.bot.say(
            ":bis: price is {:0.8f} BTC or {:0.2f} USD on Cryptopia".format(cryptopia['BTC']['lastPrice'],
                                                                            cryptopia['USD']['lastPrice']))
        await self.bot.say(":bis: price is {:0.8f} BTC or {:0.2f} USD on QTrade".format(qtrade['BTC']['lastPrice'],
                                                                                        qtrade['USD']['lastPrice']))

    @commands.command(name='deposit', brief="Shows or creates a BIS deposit address", pass_context=True)
    async def deposit(self, ctx):
        user = User(ctx.message.author.id)
        user_info = user.info()
        print(ctx.message.author.id, user_info)
        if user_info:
            if user_info['accept']:
                msg = "{}, your :bis: address is `{}`".format(ctx.message.author.display_name, user_info['address'])
                em = discord.Embed(description=msg, colour=discord.Colour.green())
                await self.bot.say(embed=em)

                return
        disclaimer = """By creating a Bismuth address on this service, you acknowledge that:
        - This is meant to be used for tips, thanks you, quick experiments and other small amount usage.
        - The matching wallet private key is stored on a secret online server, team operated.
        - The team does not hold any responsability if your wallet or funds are lost.
        Basically, you're using this service at your own risks.

        Type `Pawer accept` to say you understand and proceed."""

        em = discord.Embed(description=disclaimer, colour=discord.Colour.dark_orange())
        em.set_author(name="Terms:")
        await self.bot.say(embed=em)

    @commands.command(name='accept', brief="Accept the Pawer terms", pass_context=True)
    async def accept(self, ctx):
        user = User(ctx.message.author.id)
        user_info = user.info()
        # if accepted, say when and gives address
        if user_info:
            if user_info['accept']:
                msg = "Your :bis: address is `{}`".format(user_info['address'])
                em = discord.Embed(description=msg, colour=discord.Colour.orange())
                em.set_author(name="{}, you already accepted the terms on {}".
                              format(ctx.message.author.display_name, ts_to_string(user_info['accept'])))
                await self.bot.say(embed=em)
                return
        # If not, creates wallet and stores accepted.
        address = user.create_wallet()
        info = {"accept": int(time.time()), "address": address}
        user.save(info)
        # TODO: safety, store an encrypted backup of the wallet elsewhere.
        msg = "Your :bis: address is `{}`".format(info['address'])
        em = discord.Embed(description=msg, colour=discord.Colour.green())
        em.set_author(name="{}: Terms accepted".format(ctx.message.author.display_name))
        await self.bot.say(embed=em)
