"""
Common config instance
"""

import json


with open("config.json", "r") as f:
    CONFIG = json.load(f)
