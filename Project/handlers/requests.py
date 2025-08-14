import os
from Project.utils.other_utils import get_today_folder
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Project.utils.dealer_utils import load_dealer_codes, save_dealer_codes
from dotenv import load_dotenv
from Project.config import ADMIN_ID

router = Router()
dealer_codes = load_dealer_codes()
load_dotenv()
ADMIN_ID=os.getenv("ADMIN_ID")


dealer_codes = load_dealer_codes()

class RequestForm(StatesGroup):
    waiting_for_text = State()
    waiting_for_photo = State()
    waiting_for_video = State()
    waiting_more_material = State()
    waiting_new_request = State()

def get_photo_video_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📷 Отправить фото")],
            [KeyboardButton(text="🎥 Отправить видео")]
        ],
        resize_keyboard=True
    )

def get_yes_no_keyboard(yes_text="Да", no_text="Нет"):
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=yes_text)], [KeyboardButton(text=no_text)]],
        resize_keyboard=True
    )

# Начало запроса
@router.message(F.text == "📝 Набрать текст")
async def start_request(message: types.Message, state: FSMContext):
    await message.answer("✍️ Пришлите текстовую информацию.", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(RequestForm.waiting_for_text)

# Обработка текста
@router.message(RequestForm.waiting_for_text, F.content_type == "text")
async def handle_text(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    dealer_code = dealer_codes.get(user_id, f"user_{user_id}")
    folder = get_today_folder(dealer_code)
    os.makedirs(folder, exist_ok=True)

    file_path = os.path.join(folder, f"text_{dealer_code}_{message.message_id}.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(message.text)

    await message.bot.send_message(
        ADMIN_ID,
        f"📩 Новый текст от {dealer_code}:\n{message.text}"
    )

    await message.answer(
        "✅ Текст получен.\nВыберите, что хотите добавить:",
        reply_markup=get_photo_video_keyboard()
    )
    await state.set_state(RequestForm.waiting_more_material)

# Обработка фото
@router.message(RequestForm.waiting_more_material, F.text == "📷 Отправить фото")
async def ask_photo(message: types.Message, state: FSMContext):
    await message.answer("📷 Пришлите фото.", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(RequestForm.waiting_for_photo)

@router.message(RequestForm.waiting_for_photo, F.content_type == "photo")
async def handle_photo(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    dealer_code = dealer_codes.get(user_id, f"user_{user_id}")
    folder = get_today_folder(dealer_code)
    os.makedirs(folder, exist_ok=True)

    file_path = os.path.join(folder, f"photo_{dealer_code}_{message.message_id}.jpg")
    await message.photo[-1].download(destination_file=file_path)

    await message.bot.send_photo(
        ADMIN_ID,
        photo=message.photo[-1].file_id,
        caption=f"📷 Фото от {dealer_code}"
    )

    await message.answer(
        "✅ Фото получено.\nХотите добавить ещё материал?",
        reply_markup=get_yes_no_keyboard("Добавить ещё", "Завершить отправку")
    )
    await state.set_state(RequestForm.waiting_more_material)

# Обработка видео
@router.message(RequestForm.waiting_more_material, F.text == "🎥 Отправить видео")
async def ask_video(message: types.Message, state: FSMContext):
    await message.answer("🎥 Пришлите видео.", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(RequestForm.waiting_for_video)

@router.message(RequestForm.waiting_for_video, F.content_type == "video")
async def handle_video(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    dealer_code = dealer_codes.get(user_id, f"user_{user_id}")
    folder = get_today_folder(dealer_code)
    os.makedirs(folder, exist_ok=True)

    file_path = os.path.join(folder, f"video_{dealer_code}_{message.message_id}.mp4")
    await message.video.download(destination_file=file_path)

    await message.bot.send_video(
        ADMIN_ID,
        video=message.video.file_id,
        caption=f"🎥 Видео от {dealer_code}"
    )

    await message.answer(
        "✅ Видео получено.\nХотите добавить ещё материал?",
        reply_markup=get_yes_no_keyboard("Добавить ещё", "Завершить отправку")
    )
    await state.set_state(RequestForm.waiting_more_material)

# Добавление/завершение
@router.message(RequestForm.waiting_more_material, F.text == "Добавить ещё")
async def more_material(message: types.Message, state: FSMContext):
    await message.answer("Выберите, что хотите добавить:", reply_markup=get_photo_video_keyboard())

@router.message(RequestForm.waiting_more_material, F.text == "Завершить отправку")
async def finish_material(message: types.Message, state: FSMContext):
    await message.answer("📌 Запрос завершён. Чтобы начать новый, нажмите 📝 Набрать текст.", reply_markup=get_text_keyboard())
    await state.clear()