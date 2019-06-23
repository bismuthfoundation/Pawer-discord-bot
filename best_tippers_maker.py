import sqlite3
import json


db = sqlite3.connect("data/stats.db")
cursor = db.cursor()

data = {}

for tip_type in ["tip", "rain", "eggrain"]:
    for address in ["from", "to"]:
        cursor.execute("select sum(amount), count(amount),  id from tips join users where type='{}' and address={}_"
                       "address group by {}_address order by sum(amount) desc limit 5;".format(tip_type, address, address))
        tips = cursor.fetchall()
        data[tip_type] = {}
        data[tip_type][address] = tips

with open("data/tips.json", "w") as f:
    json.dump(data, f)
