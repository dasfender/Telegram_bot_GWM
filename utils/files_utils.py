import os
from datetime import datetime

def get_request_folder(dealer_code: str):
    today = datetime.now().strftime("%Y-%m-%d")
    folder = os.path.join("requests", dealer_code, today)
    os.makedirs(folder, exist_ok=True)
    return folder

def save_text(folder: str, text: str, filename: str):
    with open(os.path.join(folder, filename), "w", encoding="utf-8") as f:
        f.write(text)