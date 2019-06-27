import sqlite3
import time
import os


class Tips:
    def __init__(self, db_path="data/stats.db"):
        os.makedirs("data", exist_ok=True)
        
        self.db = sqlite3.connect(db_path)
        self.cursor = self.db.cursor()

        self.cursor.execute("CREATE TABLE IF NOT EXISTS users (address VARCHAR(56) PRIMARY KEY, id INTEGER, name TEXT)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS tips (from_address VARCHAR(56), to_address VARCHAR(56), "
                            "amount FLOAT, type VARCHAR(10), timestamp INTEGER)")
        self.db.commit()

    def stop(self):
        self.db.close()

    def add_user(self, address, user_id, user_name):
        try:
            self.cursor.execute("INSERT into users values(?,?,?)", (address, user_id, user_name))
            self.db.commit()
        except:
            print("error adding user {} to database".format(user_name))

    def tip(self, from_address, to_address, amount, tip_type="tip"):
        self.cursor.execute("INSERT into tips values(?,?,?,?,?)", (from_address, to_address, amount, tip_type,
                                                                   int(time.time())))
        self.db.commit()

    def start_rain(self, address, total_amount, user_count, rain_type="rain"):
        self.cursor.execute("INSERT into tips values(?,?,?,?,?)", (address, "{}:{}".format(total_amount, user_count), 0,
                                                                   rain_type, int(time.time())))
        self.db.commit()
