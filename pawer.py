"""
Pawer Discord Bot for Bismuth Cryptocurrency
"""

from discord.ext import commands

from cogs.bismuth import Bismuth
from cogs.extra import Extra
from cogs.hypernodes import Hypernodes
from modules.config import CONFIG

__version__ = '0.3'

BOT_PREFIX = "Pawer "

client = commands.Bot(command_prefix=BOT_PREFIX)


@client.event
async def on_ready():
    """
    This function is not guaranteed to be the first event called.
    Likewise, this function is not guaranteed to only be called once.
    This library implements reconnection logic and thus will end up calling this event whenever a RESUME request fails.
    """
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.event
async def on_message(message):
    """Called when a message is created and sent to a server."""
    if not message.content.startswith(BOT_PREFIX):
        # Not for us
        return
    if client.user.id != message.author.id: # check not a bot message
        print("Got {} from {}".format(message.content, message.author.display_name))
    if message.server and message.channel.id not in CONFIG['bot_channel']:
        # TODO: blame if Pawer command in non private nor dedicated channel
        # Can PM and auto delete the message also?
        print('Unauth channel')
    else:
        # only here, will process commands
        await client.process_commands(message)


# TODO: add generic "info" command
@client.command(name='info', brief="Pawer bot general info", pass_context=True)
async def info(ctx):
    # TODO: cache?
    await client.say("TODO - info")


if __name__ == '__main__':
    client.add_cog(Bismuth(client))
    client.add_cog(Hypernodes(client))
    client.add_cog(Extra(client))

    client.run(CONFIG['token'])
