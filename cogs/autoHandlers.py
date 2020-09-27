"""
COG: Dealing with automatic messages to Discord Community and single users.
"""

import os
import sys

from discord.ext import commands
from discord import Embed, Colour
from modules.config import CONFIG, EMOJIS, SHORTCUTS


class AutoCommands:
    def __init__(self, bot):
        self.bot = bot

    async def system_message(self, ctx, error, destination: int, handled: bool):
        """
        Send the error to selected destination
        """
        if destination == 1:  # To sys channel
            dest = await self.bot.get_channel(id=CONFIG['bot_channel'][0])
        elif destination == 2:  # To ctx channel
            dest = ctx.message.channel
        elif destination == 3:  # To author
            dest = ctx.message.author

        if handled:
            await dest.send(content=f"Command Executed: {ctx.message.content}\n"
                                    f"User: {ctx.message.author} ({ctx.message.author.id})\n"
                                    f"Error: {error}")
        else:
            await dest.send(
                content=f":warning: ***Unhandled Error***:warning: \nCommand Executed:{ctx.message.content}\n"
                        f"User: {ctx.message.author} ({ctx.message.author.id})\n"
                        f"Channel: {ctx.message.channel}"
                        f"Error: {error}")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await self.system_message(ctx=ctx, error=error, destination=3, handled=True)

        else:
            await self.system_message(ctx=ctx, error=error, destination=1, handled=True)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """
        When member joins a message will be sent to newly joined user
        :param member:
        :return:
        """
        if not member.bot:
            info_embed = Embed(title=f'__Welcome to {member.guild}__',
                               description=f'This is an automated system message from the f{self.bot.user}',
                               colour=Colour.magenta())
            info_embed.set_thumbnail(url=self.bot.user.avatar_url)
            info_embed.add_field(name='Bismuth Butler at your service!',
                                 value=f"I'm your Bismuth butler. Type `Pawer help` for a full commands list. Otherwise"
                                       f" ***__{member.guild}__*** has {len(member.guild.channels)} channels "
                                       f"available to {len(member.guild.members)}. Owner is {member.guild.owner} "
                                       f"(id:{member.guild.owner.id}) and system channel is "
                                       f"{member.guild.system_channel}. Enjoy your stay with us.")
            await member.send(embed=info_embed)


    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """
        Clean up process once member leaves the guild
        """

        if not member.bot:
            info_embed = Embed(title=f':warning: __Important Notice!__:warning: ',
                               description=f'This is an automated system message from the f{self.bot.user}',
                               colour=Colour.magenta())
            info_embed.set_thumbnail(url=self.bot.user.avatar_url)
            info_embed.add_field(name='Bismuth Butler message!',
                                 value=f"To bad you are leaving us. We would just like to remind you that, Prawer"
                                       f" allows to move Bismuth crypto currency in P2P transactions. Since you left us,"
                                       f" we would encourage you to check your personal wallet so Bismuth is not left "
                                       f"behind.")
            await member.send(embed=info_embed)

