"""
Common config instance
"""

import json

# For custom emojis
EMOJIS = {'Bismuth': ''}

with open("config.json", "r") as f:
    CONFIG = json.load(f)
