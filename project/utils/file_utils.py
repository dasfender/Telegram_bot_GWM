import os
from datetime import datetime
from project.config import DATA_FOLDER

def get_today_folder(dealer_code):
    today = datetime.now().strftime("%Y-%m-%d")
    folder = os.path.join(DATA_FOLDER, dealer_code, today)
    os.makedirs(folder, exist_ok=True)
    return folder
