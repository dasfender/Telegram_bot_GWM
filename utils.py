import os
import json
from datetime import datetime

DEALER_CODES_FILE = "dealer_codes.json"

def load_dealer_codes():
    if os.path.exists(DEALER_CODES_FILE):
        with open(DEALER_CODES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_dealer_codes(codes):
    with open(DEALER_CODES_FILE, "w", encoding="utf-8") as f:
        json.dump(codes, f, ensure_ascii=False, indent=2)

def get_today_folder(dealer_code):
    today = datetime.now().strftime("%Y-%m-%d")
    folder_path = os.path.join("data", dealer_code, today)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path