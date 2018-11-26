"""
Helpers for the Pawer discord bot
"""

from discord.ext import commands
from datetime import datetime


def ts_to_string(timestamp):
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')


def is_channel(channel_id):
    def predicate(ctx):
        # print("server", ctx.message.server)
        if not ctx.message.server:
            # server = None means PM
            return True
        # print("Channel id {} private {}".format(ctx.message.channel.id, ctx.message.channel.is_private))
        return ctx.message.channel.id in channel_id
    return commands.check(predicate)
