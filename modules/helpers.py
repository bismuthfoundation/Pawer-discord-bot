"""
Helpers for the Pawer discord bot
"""

import json
import sys
from os import path, makedirs
from bismuthclient.bismuthwallet import BismuthWallet
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









class User:

    __slots__ = ('_base_path', '_user_id', '_wallet', '_info')

    def __init__(self, user_id):
        self._user_id = user_id
        self._base_path = 'users/{}/{}/{}'.format(user_id[0], user_id[1], user_id)
        # print("self._base_path", self._base_path)
        base_dir = 'users/{}/{}'.format(user_id[0], user_id[1])
        if not path.isdir(base_dir):
            makedirs(base_dir, exist_ok=True)
        self._wallet = None
        self._info = None

    @property
    def json_file(self):
        return '{}.json'.format(self._base_path)

    @property
    def wallet_file(self):
        return '{}.der'.format(self._base_path)

    def info(self):
        if self._info:
            return self._info
        if path.exists(self.json_file):
            with open(self.json_file, 'r') as f:
                return json.load(f)
        else:
            return None



    def save(self, info):
        self._info = info
        with open(self.json_file, 'w') as f:
            json.dump(info, f)
        return True


    def create_wallet(self):
        # if wallet exists, load
        if path.exists(self.wallet_file):
            self._wallet = BismuthWallet(wallet_file=self.wallet_file, verbose=True)
            return self._wallet.address
        # or create
        self._wallet = BismuthWallet(wallet_file=self.wallet_file, verbose=True)
        self._wallet.new(self.wallet_file)
        try:
            self._wallet.load(self.wallet_file)
            print("Created", self._wallet.address)
        except Exception as e:
            print(str(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)

        return self._wallet.address
        # send back address
