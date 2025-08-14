import os
import asyncio
from Project.handlers import requests, registration, admin
from handlers import registration, requests, admin
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "Project"))
from Project.utils.dealer_utils import load_dealer_codes, save_dealer_codes




sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(registration.router)
    dp.include_router(requests.router)
    dp.include_router(admin.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
