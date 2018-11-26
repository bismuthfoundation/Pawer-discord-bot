# import discord
# import asyncio
# import json
from discord.ext import commands
from cogs.extra import Extra
from modules.config import CONFIG

# client = discord.Client()
client = commands.Bot(command_prefix='Pawer ')

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



"""
@client.event
async def on_message(message):
    #Called when a message is created and sent to a server.
    if client.user.id != message.author.id: # check not a bot message
        print("Got", message.content)

    if message.content.startswith('Pawer test'):
        counter = 0
        tmp = await client.send_message(message.channel, 'Calculating messages...')
        async for log in client.logs_from(message.channel, limit=100):
            if log.author == message.author:
                counter += 1

        await client.edit_message(tmp, 'You have {} messages.'.format(counter))
    elif message.content.startswith('Pawer sleep'):
        await asyncio.sleep(5)
        await client.send_message(message.channel, 'Done sleeping')
"""

if __name__ == '__main__':

    client.add_cog(Extra(client))
    client.run(CONFIG['token'])
