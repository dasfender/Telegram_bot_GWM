import os
from datetime import datetime
from Project.config import DATA_FOLDER

def get_request_folder(dealer_code: str) -> str:
    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    folder = os.path.join(DATA_FOLDER, dealer_code, date_str)
    os.makedirs(folder, exist_ok=True)
    return folder

def save_text_file(folder: str, text: str):
    file_path = os.path.join(folder, "text.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)


def dealer_utils():
    return None


def file_utils():
    return None


def file_utils():
    return None


def archive_utils():
    return None