import json
import os

DATA_FILE = os.path.join(os.path.dirname(__file__), "dealer_codes.json")

def load_dealer_codes():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_dealer_codes(codes):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(codes, f, ensure_ascii=False, indent=4)
