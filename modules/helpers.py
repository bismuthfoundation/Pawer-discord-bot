"""
Helpers for the Pawer discord bot
"""

import json
import sys
from datetime import datetime
from os import path, makedirs

import aiohttp
from discord.ext import commands

from bismuthclient.bismuthwallet import BismuthWallet
from bismuthclient.bismuthclient import BismuthClient
from bismuthclient.bismuthutil import BismuthUtil


def ts_to_string(timestamp):
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')


HTTP_SESSION = None

BISMUTH_CLIENT = BismuthClient(verbose=True)


async def async_get(url, is_json=False):
    """Async gets an url content.

    If is_json, decodes the content
    """
    global HTTP_SESSION
    # TODO: retry on error?
    if not HTTP_SESSION:
        HTTP_SESSION = aiohttp.ClientSession()
    # async with aiohttp.ClientSession() as session:
    async with HTTP_SESSION.get(url) as resp:
        if is_json:
            return await resp.json()
        else:
            return await resp.text()
        # TODO: could use resp content-type to decide


def is_channel(channel_id):
    """No more used, kept for history"""
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

    def __init__(self, user_id: str):
        global BISMUTH_CLIENT
        user_id = str(user_id)
        self._user_id = user_id

        self._base_path = 'users/{}/{}/{}'.format(user_id[0], user_id[1], user_id)
        # print("self._base_path", self._base_path)
        base_dir = 'users/{}/{}'.format(user_id[0], user_id[1])
        if not path.isdir(base_dir):
            makedirs(base_dir, exist_ok=True)
        self._wallet = None
        self._info = None
        if not BISMUTH_CLIENT:
            # Here we can force to use a local, dedicated wallet server
            # See servers_list
            BISMUTH_CLIENT = BismuthClient(verbose=True)

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
        # We could simplify this since the BISMUTH_CLIENT has a wallet itself
        # if wallet exists, load
        if path.exists(self.wallet_file):
            self._wallet = BismuthWallet(wallet_file=self.wallet_file, verbose=True)
            return self._wallet.address
        # or create
        self._wallet = BismuthWallet(wallet_file=self.wallet_file, verbose=True)
        self._wallet.new(self.wallet_file)
        self._wallet.load(self.wallet_file)
        print("Created", self._wallet.address)
        # send address back
        return self._wallet.address

    def balance(self, token=''):
        """
        Returns balance of current wallet.
        If token is not empty, returns the balance for this specific token
        """
        # TODO: this is not async (but if async, should be serialized)
        BISMUTH_CLIENT.load_wallet(self.wallet_file)
        return BISMUTH_CLIENT.balance(for_display=True)

    @staticmethod
    def status():
        """Get Bismuth chain status from the server"""
        status = BISMUTH_CLIENT.status()
        try:
            status['server'] = BISMUTH_CLIENT.current_server
            status['supply'] = BismuthUtil.height_to_supply(status['blocks'])
            status['last_block'] = BISMUTH_CLIENT.command("blocklast")
        except:
            pass
        return status

    def send_bis_to(self, amount, recipient, data='', operation='', check_balance=False):
        """
        Sends BIS from current wallet to recipient, with optional data and operation

        If check_balance, checks the user balance is enough.

        Returns a dict with keys txid (txid if sudccess or None) and error ('', 'NO_WALLET','LOW_BALANCE','MP_INSERT')
        """
        error = ''
        txid = None
        if path.isfile(self.wallet_file):
            BISMUTH_CLIENT.load_wallet(self.wallet_file)
            if check_balance:
                balance = BISMUTH_CLIENT.balance(for_display=False)
                fees = BismuthUtil.fee_for_tx(data)
                if float(balance) < float(amount) + fees:
                    # TODO: better use an enum
                    error = 'LOW_BALANCE'
                    return {'txid': txid, 'error': error}
            txid = BISMUTH_CLIENT.send(recipient, amount, data=data, operation=operation)
            if not txid:
                error = 'MP_INSERT'
        else:
            error = 'NO_WALLET'
        return {'txid': txid, 'error': error}

    def sign_message(self, data):
        """
        Sign message with privkey, for off chain usage
        Returns a string with b64 encoded signature.
        """
        error = ''
        sign = None
        if path.isfile(self.wallet_file):
            BISMUTH_CLIENT.load_wallet(self.wallet_file)
            sign = BISMUTH_CLIENT.sign(data)
            if not sign:
                error = 'ERR_SIGN'
        else:
            error = 'NO_WALLET'
        return {'sign': sign, 'error': error}
