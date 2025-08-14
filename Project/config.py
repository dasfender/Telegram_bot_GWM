import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

DATA_FOLDER = os.path.join(os.getcwd(), "requests")

os.makedirs(DATA_FOLDER, exist_ok=True)
