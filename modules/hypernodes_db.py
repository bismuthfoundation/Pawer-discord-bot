import sqlite3
import time
import os
from discord.utils import get


class HypernodesDb:
    async def safe_send_message(self, recipient, message, bot):
        try:
            await bot.send_message(recipient, message)
        except Exception as e:
            print(e)

    def __init__(self, db_path="data/hypernodes.db"):
        os.makedirs("data", exist_ok=True)
        
        self.db = sqlite3.connect(db_path)
        self.cursor = self.db.cursor()

        self.cursor.execute("CREATE TABLE IF NOT EXISTS users_info (user_id TEXT, ip TEXT)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS nodes_info (ip TEXT PRIMARY KEY, status INTEGER, "
                            "timestamp INTEGER)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS user_id on users_info(user_id);")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS ip on users_info(ip);")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS timestamp on nodes_info(timestamp);")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS nodes on nodes_info(ip, status);")
        self.db.commit()

    def stop(self):
        self.db.close()

    def watch(self, user_id, ip):
        self.cursor.execute("INSERT into users_info values(?,?)", (user_id, ip))
        self.db.commit()

    def unwatch(self, user_id, ip):
        self.cursor.execute("DELETE FROM users_info where user_id=? and ip=?", (user_id, ip))
        self.db.commit()

    async def update_nodes_status(self, hypernodes_data, bot):
        self.cursor.execute("select user_id, users_info.ip from users_info join nodes_info where"
                            " users_info.ip=nodes_info.ip and timestamp < ?", (int(time.time() - 4.1 * 60 * 5),))
        removed_nodes = self.cursor.fetchall()
        ip_list = "("
        for node in removed_nodes:
            member = get(bot.get_all_members(), id=node[0])
            await self.safe_send_message(member, "hypernode {} has been removed from the watch list because it don't "
                                                 "exists anymore.".format(node[1]), bot)
            ip_list += "'{}',".format(node[1])
        if removed_nodes:
            ip_list = ip_list[:-1]
        ip_list += ")"
        self.cursor.execute("DELETE FROM users_info WHERE ip in {}".format(ip_list))
        self.cursor.execute("DELETE FROM nodes_info WHERE timestamp < ?", (int(time.time() - 4.1 * 60 * 5),))
        self.db.commit()
        self.cursor.execute("SELECT distinct(ip) FROM users_info")
        ips = self.cursor.fetchall()
        hn_height = [[status[1], status[8]] for status in hypernodes_data.values() if (status[1],) in ips]
        current_time = int(time.time())
        for hn in hn_height:
            if hn[1] == "Inactive":
                hn[1] = 1
            else:
                hn[1] = 0

            self.cursor.execute("INSERT OR IGNORE into nodes_info values(?,?,?)", (hn[0], 0, current_time))
            self.cursor.execute("UPDATE nodes_info SET status=cast(status/10 as int)+?, timestamp=?"
                                " WHERE ip=?", (1000*hn[1], current_time, hn[0]))
        self.db.commit()

    async def get_nodes_status(self, bot):
        self.cursor.execute("select user_id, users_info.ip from users_info join nodes_info where"
                            " users_info.ip=nodes_info.ip and status=1110")
        stopped_nodes = self.cursor.fetchall()
        for node in stopped_nodes:
            member = get(bot.get_all_members(), id=node[0])
            await self.safe_send_message(member, "hypernode {} just stopped, you should check what append"
                                         .format(node[1]), bot)

    def get_list(self, user_id):
        self.cursor.execute("SELECT distinct(ip) FROM users_info WHERE user_id=?", (user_id,))
        return self.cursor.fetchall()
