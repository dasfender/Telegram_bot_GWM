import json
import os

DEALER_CODES_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "dealer_codes.json")

def load_dealer_codes():
    if os.path.exists(DEALER_CODES_FILE):
        with open(DEALER_CODES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_dealer_codes(codes):
    with open(DEALER_CODES_FILE, "w", encoding="utf-8") as f:
        json.dump(codes, f, ensure_ascii=False, indent=2)