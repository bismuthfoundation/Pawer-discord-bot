"""
Pawer Discord Bot for Bismuth Cryptocurrency
"""

from discord.ext import commands

from cogs.bismuth import Bismuth
from cogs.extra import Extra
from modules.config import CONFIG

__version__ = '0.2'

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

# TODO: add generic "info" command

if __name__ == '__main__':
    client.add_cog(Bismuth(client))
    client.add_cog(Extra(client))

    client.run(CONFIG['token'])
