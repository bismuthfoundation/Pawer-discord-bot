import sqlite3
import json


db = sqlite3.connect("../data/stats.db")
cursor = db.cursor()

data = {}

cursor.execute("select sum(amount), count(amount),  id from tips join users where type='tip' and address=from_address group by from"
               "_address order by sum(amount) desc limit 5;")
tips = cursor.fetchall()
data["tip"] = {}
data["tip"]["from"] = tips

cursor.execute("select sum(amount), count(amount),  id from tips join users where type='tip' and address=to_address group by to"
               "_address order by sum(amount) desc limit 5;")
tips = cursor.fetchall()
data["tip"]["to"] = tips



cursor.execute("select sum(amount), count(amount),  id from tips join users where type='rain' and address=from_address group by from"
               "_address order by sum(amount) desc limit 5;")
tips = cursor.fetchall()
data["rain"] = {}
data["rain"]["from"] = tips

cursor.execute("select sum(amount), count(amount),  id from tips join users where type='rain' and address=to_address group by to"
               "_address order by sum(amount) desc limit 5;")
tips = cursor.fetchall()
data["rain"]["to"] = tips





cursor.execute("select sum(amount), count(amount),  id from tips join users where type='eggrain' and address=from_address group by from"
               "_address order by sum(amount) desc limit 5;")
tips = cursor.fetchall()
data["eggrain"] = {}
data["eggrain"]["from"] = tips

cursor.execute("select sum(amount), count(amount),  id from tips join users where type='eggrain' and address=to_address group by to"
               "_address order by sum(amount) desc limit 5;")
tips = cursor.fetchall()
data["eggrain"]["to"] = tips

with open("../data/tips.json", "w") as f:
    json.dump(data, f)
