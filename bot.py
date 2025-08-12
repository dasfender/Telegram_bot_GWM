import os
from dotenv import load_dotenv
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import handlers


load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(handlers.router)

    print("Бот запущен...")
    #await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
