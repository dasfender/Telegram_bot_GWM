import os
from aiogram import Router, types
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

router = Router()

@router.message()
async def admin_notifications(message: types.Message):
    for admin_id in ADMIN_ID:
        await message.bot.send_message(admin_id, f"Новый запрос от {message.from_user.id}")

