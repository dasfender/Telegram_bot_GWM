from aiogram import Router, types
from aiogram.filters import Command
from project.utils.file_utils import get_today_folder
from project.utils.dealer_utils import load_dealer_codes

router = Router()


@router.message(Command("new_request"))
async def new_request(message: types.Message):
    codes = load_dealer_codes()
    user_id = str(message.from_user.id)
    if user_id not in codes:
        await message.answer("Сначала зарегистрируйтесь через /start и введите дилерский код.")
        return
    await message.answer("Отправьте файлы (фото или видео) по вашему запросу.")


@router.message(lambda message: message.photo or message.video)
async def handle_files(message: types.Message):
    codes = load_dealer_codes()
    user_id = str(message.from_user.id)
    if user_id not in codes:
        await message.answer("Сначала зарегистрируйтесь через /start и введите дилерский код.")
        return
    dealer_code = codes[user_id]
    folder = get_today_folder(dealer_code)

    if message.photo:
        file = message.photo[-1]
    elif message.video:
        file = message.video
    else:
        await message.answer("Не удалось обработать файл.")
        return

    file_path = f"{folder}/{file.file_id}.jpg" if message.photo else f"{folder}/{file.file_id}.mp4"
    await file.download(destination=file_path)
    await message.answer(f"Файл сохранён. Вы можете отправить ещё файлы или завершить запрос.")
