import os
from ..utils.dealer_utils import load_dealer_codes
from aiogram import Router, F, types
from dotenv import load_dotenv


router = Router()
load_dotenv()
ADMIN_ID = os.getenv("ADMIN_ID")

@router.message(F.from_user.id == ADMIN_ID, F.text.startswith("/get_archive"))
async def get_archive(message: types.Message):
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("❌ Укажите код дилера: `/get_archive ABC123`", parse_mode="Markdown")
        return

    dealer_code = parts[1].strip()
    archive_path = create_request_archive(dealer_code)

    if not archive_path:
        await message.answer(f"❌ Нет запросов для дилера {dealer_code}")
        return

    await message.answer_document(types.FSInputFile(archive_path), caption=f"📦 Архив последнего запроса дилера {dealer_code}")
