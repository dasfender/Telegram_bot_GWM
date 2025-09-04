from aiogram import Router, types, F
from aiogram.types import Message
from aiogram.filters import Command
from dotenv import load_dotenv
import os

load_dotenv()
ADMIN_ID= os.getenv('ADMIN_ID')

router = Router()


@router.message(Command("admin"))
async def admin_start(message: Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("Привет, админ! Ты будешь получать уведомления о новых заявках.")
    else:
        await message.answer("У вас нет прав для этой команды.")
