import sqlite3
import time


class Tips:
    def __init__(self, db_path="data/stats.db"):
        self.db = sqlite3.connect(db_path)
        self.cursor = self.db.cursor()

        self.cursor.execute("CREATE TABLE IF NOT EXISTS tips (from_address VARCHAR(56), to_address VARCHAR(56), "
                            "amount FLOAT, type VARCHAR(10), timestamp INTEGER)")
        self.db.commit()

    def stop(self):
        self.db.close()

    def create_if_not_exists(self, address):
        for field in ["from", "to"]:
            if address not in self.data[field]:
                self.data[field][address] = {}

            for tip_type in self.tip_types:
                if tip_type not in self.data[field][address]:
                    self.data[field][address][tip_type] = 0

    def tip(self, from_address, to_address, amount, tip_type="tip"):
        self.cursor.execute("INSERT into tips values(?,?,?,?,?)", (from_address, to_address, amount, tip_type,
                                                                   int(time.time())))
        self.db.commit()


