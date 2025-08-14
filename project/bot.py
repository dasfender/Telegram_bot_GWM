import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from project.handlers.request_handler import router
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")


async def main():
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode="HTML")
    )

    dp = Dispatcher()
    dp.include_router(router)  # Регистрируем роутер напрямую

    print("Бот запущен...")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())