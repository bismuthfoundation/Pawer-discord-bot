"""
Pawer Discord Bot for Bismuth Cryptocurrency
"""

import asyncio

from discord.ext import commands
from discord.utils import get

from cogs.bismuth import Bismuth
from cogs.extra import Extra
from cogs.hypernodes import Hypernodes
from cogs.dragginator import Dragginator
from cogs.autogame import Autogame
from modules.config import CONFIG, EMOJIS

__version__ = '0.58'

# BOT_PREFIX = ('Pawer ', 'pawer ')  # Edit on_message before
BOT_PREFIX = 'Pawer '

client = commands.Bot(command_prefix=BOT_PREFIX)


@client.event
async def on_ready():
    """
    This function is not guaranteed to be the first event called.
    Likewise, this function is not guaranteed to only be called once.
    This library implements reconnection logic and thus will end up calling this event whenever a RESUME request fails.
    """
    global EMOJIS
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    EMOJIS['Bismuth'] = str(get(client.get_all_emojis(), name='Bismuth'))


@client.event
async def on_message(message):
    """Called when a message is created and sent to a server."""
    if message.content.startswith('pawer '):
        message.content = message.content.replace('pawer', 'Pawer')
    if message.content.startswith('!tip'):
        message.content = message.content.replace('!tip', 'Pawer tip')
    if message.content.startswith('!Tip'):
        message.content = message.content.replace('!Tip', 'Pawer tip')

    if not message.content.startswith(BOT_PREFIX):
        # Not for us
        return
    if client.user.id != message.author.id: # check not a bot message
        print("Got {} from {}".format(message.content, message.author.display_name))
    if message.content.startswith('Pawer tip'):
        # Exception
        await client.process_commands(message)
        return
    if message.server and message.channel.id not in CONFIG['bot_channel']:
        # TODO: blame if Pawer command in non private nor dedicated channel
        # Can PM and auto delete the message also?
        print('Unauth channel')
    else:
        await client.add_reaction(message, '⏳')  # Hourglass
        try:
            # only here, will process commands
            await client.process_commands(message)
        finally:
            await client.remove_reaction(message, '⏳', client.user)  # Hourglass


@client.command(name='about', brief="Pawer bot general info", pass_context=True)
async def about(ctx):
    # TODO: cache?
    # version
    # release logs?
    # number of wallets, of users, of messages?
    # other stats frm the bot (sqlite base?)
    await client.say("Pawer bot Version {}\nI'm your Bismuth butler. Type `Pawer help` for a full commands list.".format(__version__))


async def background_task(cog_list):
    await client.wait_until_ready()
    while not client.is_closed:
        for cog in cog_list:
            try:
                await cog.background_task()
            except:
                pass
        await asyncio.sleep(60)


if __name__ == '__main__':
    client.add_cog(Bismuth(client))
    client.add_cog(Hypernodes(client))
    client.add_cog(Extra(client))
    dragg = Dragginator(client)
    client.add_cog(dragg)
    client.add_cog(Autogame(client))

    client.loop.create_task(background_task([dragg]))

    client.run(CONFIG['token'])
