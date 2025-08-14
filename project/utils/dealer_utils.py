import json
import os
from project.config import DATA_FOLDER

DEALER_CODES_FILE = os.path.join(DATA_FOLDER, "dealer_codes.json")

def load_dealer_codes():
    if not os.path.exists(DEALER_CODES_FILE):
        return {}
    with open(DEALER_CODES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_dealer_codes(codes: dict):
    os.makedirs(DATA_FOLDER, exist_ok=True)
    with open(DEALER_CODES_FILE, "w", encoding="utf-8") as f:
        json.dump(codes, f, ensure_ascii=False, indent=4)
