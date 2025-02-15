import os
import json

def get_misp_config():
    if os.path.exists("misp_config.json"):
        with open("misp_config.json", "r") as f:
            return json.load(f)
    return None