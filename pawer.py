"""
Pawer Discord Bot for Bismuth Cryptocurrency
"""

import asyncio
import re
from time import time

from discord.ext import commands
from discord.utils import get
import discord
from cogs.bismuth import Bismuth
from cogs.token import Token
from cogs.extra import Extra
from cogs.hypernodes import Hypernodes
from cogs.dragginator import Dragginator
from cogs.autogame import Autogame
from cogs.autoHandlers import AutoCommands
from modules.config import CONFIG, EMOJIS, SHORTCUTS
from modules.helpers import User
from discord.ext.tasks import loop

__version__ = '0.65'

# BOT_PREFIX = ('Pawer ', 'pawer ')  # Edit on_message before
BOT_PREFIX = 'Pawer '

bot = commands.Bot(command_prefix=BOT_PREFIX)

CHECKING_BANS = False


@bot.event
async def on_ready():
    """
    This function is not guaranteed to be the first event called.
    Likewise, this function is not guaranteed to only be called once.
    This library implements reconnection logic and thus will end up calling this event whenever a RESUME request fails.
    """
    #  global EMOJIS
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    EMOJIS['Bismuth'] = str(get(bot.emojis, name='Bismuth'))
    if "broadcast_restart" in CONFIG and CONFIG["broadcast_restart"]:
        await bot.get_channel(CONFIG['bot_channel'][0]).send(
            "I just restarted, if one of your commands didn't get an answer, just resend it.")
    bot.loop.create_task(monitor_impersonators())


@bot.event
async def on_message(message):
    """Called when a message is created and sent to a server."""
    for search, replace in SHORTCUTS.items():
        if message.content.startswith(search):
            message.content = message.content.replace(search, replace)

    if not message.content.startswith(BOT_PREFIX):
        # Not for us
        return

    if bot.user.id != message.author.id:  # check not a bot message
        print("Got {} from {}".format(message.content, message.author.display_name))

    is_help_command = re.search(r'Pawer \w+ help', message.content)
    if is_help_command:
        # swap 'help' and 'command' accordingly
        message.content = re.sub(r'(%s)(.*)(%s)' % ('Pawer', ' help'), r'\1\3\2', message.content)

    if message.content.startswith('Pawer tip'):
        #  Exception
        await bot.process_commands(message)
        return

    if type(message.channel) == discord.TextChannel and message.channel.id not in CONFIG['bot_channel']:
        # TODO: blame if Pawer command in non private nor dedicated channel
        # Can PM and auto delete the message also?
        print('Unauth channel')
    else:
        if message.content.startswith('Pawer eligibility'):
            await eligibility(message)
            return
        if message.content.startswith('Pawer users'):
            await user_count(message)
            return
        await message.add_reaction('⏳')  # Hourglass
        try:
            # only here, will process commands
            await bot.process_commands(message)
        finally:
            await message.remove_reaction('⏳', bot.user)  # Hourglass


async def eligibility(message):
    try:
        registered_members = 0
        for member in bot.get_all_members():
            if str(member.status) != "offline" and not member.bot:
                current_user = User(member.id)
                user_info = current_user.info()
                if user_info and user_info["address"]:
                    registered_members += 1
        await message.channel.send("{} users are connected and have a pawer account".format(registered_members))
    except Exception as e:
        print(str(e))


async def user_count(message):
    try:
        registered_members = 0
        for member in bot.get_all_members():
            if not member.bot:
                current_user = User(member.id)
                user_info = current_user.info()
                if user_info and user_info["address"]:
                    registered_members += 1
                    # bot.tip_module.add_user(user_info["address"], member.id, member.display_name)
        await message.channel.send("{} users have a pawer account".format(registered_members))
    except Exception as e:
        print(str(e))


@bot.command()
async def about(ctx):
    """Pawer bot general info"""
    # TODO: cache?
    # version
    # release logs?
    # number of wallets, of users, of messages?
    # other stats frm the bot (sqlite base?)
    await ctx.send(
        "Pawer bot Version {}\nI'm your Bismuth butler. Type `Pawer help` for a full commands list.".format(
            __version__))


@loop(seconds=60)
async def background_task():
    for cog in background_cog_list:
        try:
            await cog.background_task(bot=bot)
        except Exception as e:
            print(e)

"""
async def background_task(cog_list):
    await bot.wait_until_ready()
    while not bot.is_closed:
        for cog in cog_list:
            try:
                await cog.background_task()
            except:
                pass
        await asyncio.sleep(60)
"""


async def monitor_impersonators():
    await bot.wait_until_ready()
    notified_impersonators = []
    # Make sure config is lowercase - this becomes a set, therefore unique names.
    CONFIG["foundation_members"] = { name.lower().strip() for name in CONFIG["foundation_members"] }
    print("Foundation list", CONFIG["foundation_members"])
    while not bot.is_closed:
        await ban_impersonators(notified_impersonators)  # that method can't raise an exception
        await ban_scammers()
        await asyncio.sleep(30)


async def ban_impersonators(notified_impersonators):
    global CHECKING_BANS
    imp_channel = bot.get_channel(id=int(CONFIG['impersonator_info_channel']))

    if CHECKING_BANS:
        # Avoid re-entrance.
        return
    try:
        CHECKING_BANS = True
        print("Checking bans...")
        start = time()
        members = list(bot.get_all_members())  # convert generator to list, we need all anyway.
        impersonators = [ member for member in members if member.name.lower().strip() in CONFIG["foundation_members"] and member.id not in CONFIG["admin_ids"] ]
        print("{} members, {} impersonators, {} sec". format(len(members), len(impersonators), time() - start))
        for impersonator in impersonators:
            if impersonator.name not in notified_impersonators:
                imp_channel = bot.get_channel(id=int(CONFIG['impersonator_info_channel']))
                await imp_channel(content="Impersonator - " + impersonator.mention + " found")
                print('Impersonator - {} found - Out of {} Total members'.format(impersonator.name, len(members)))
                notified_impersonators.append(impersonator.name)
            if CONFIG['ban_impersonator']:
                await impersonator.ban(reason="Impersonating")
                await imp_channel.send(content="Impersonator - " + impersonator.mention + " banned")
                print('Impersonator - {} banned'.format(impersonator.name))
    except Exception as e:
        print("Exception ban_impersonators", str(e))
    finally:
        CHECKING_BANS = False


def is_scammer(member):
    # print(member.display_name.lower(), member.name.lower())
    for badword in CONFIG["scammer_keywords"]:
        if badword in member.display_name.lower():
            return True
        if badword in member.name.lower():
            return True
    for badhash in CONFIG["scammer_avatars"]:
        if badhash == member.avatar:
            return True
    return False


async def ban_scammers():
    global CHECKING_BANS
    imp_channel = bot.get_channel(id=int(CONFIG['impersonator_info_channel']))
    if CHECKING_BANS:
        # Avoid re-entrance.
        return
    try:
        CHECKING_BANS = True
        print("Checking scammers...", CONFIG["scammer_keywords"])
        # start = time()
        members = list(bot.get_all_members())
        for member in members:
            if is_scammer(member):
                print(member.display_name, member.name)
        scammers = [member for member in members if is_scammer(member)]
        print("{} scammers". format(len(scammers)))
        for scammer in scammers:
            await imp_channel.send(content= "Scammer - " + scammer.mention + " banned")
            await scammer.ban(reason='Scammer banned')
            print('Scammer - {} banned'.format(scammer.name))

    except Exception as e:
        print("Exception ban_scammers", str(e))
    finally:
        CHECKING_BANS = False


if __name__ == '__main__':
    hypernodes = Hypernodes(bot)
    bot.add_cog(hypernodes)
    dragg = Dragginator(bot)

    bot.add_cog(dragg)

    bot.add_cog(Extra(bot))
    bot.add_cog(Bismuth(bot))
    bot.add_cog(Token())
    bot.add_cog(Autogame())
    bot.add_cog(AutoCommands(bot))


    background_cog_list = [hypernodes, dragg]
    background_task.start()
    bot.run(CONFIG['token'])
