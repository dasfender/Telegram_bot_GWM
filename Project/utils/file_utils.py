import os
from datetime import date

DATA_FOLDER = os.path.join(os.path.dirname(__file__), "data")

def get_today_folder(dealer_code):
    today = date.today().isoformat()
    folder = os.path.join(DATA_FOLDER, dealer_code, today)
    os.makedirs(folder, exist_ok=True)
    return folder
