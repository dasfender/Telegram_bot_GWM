import os
from aiogram import Router, F, types
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from utils import get_today_folder, load_dealer_codes, save_dealer_codes
from dotenv import load_dotenv

router = Router()
load_dotenv()
ADMIN_ID=os.getenv("ADMIN_ID")
dealer_codes = load_dealer_codes()

class Form(StatesGroup):
    waiting_for_code = State()
    waiting_for_text = State()
    waiting_for_photo = State()
    waiting_for_video = State()
    waiting_more_material = State()
    waiting_new_request = State()


def get_photo_video_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📷 Отправить фото")],
            [KeyboardButton(text="🎥 Отправить видео")],
            [KeyboardButton(text="🔄 Сменить Код Дилера")]
        ],
        resize_keyboard=True
    )

def get_yes_no_keyboard(yes_text="Да", no_text="Нет"):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=yes_text)],
            [KeyboardButton(text=no_text)]
        ],
        resize_keyboard=True
    )

def get_start_work_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Набрать текст")]
        ],
        resize_keyboard=True
    )


@router.message(F.text == "/start")
async def start_command(message: types.Message, state: FSMContext):
    if message.from_user.id in dealer_codes:
        await message.answer(
            f"👋 Привет, {dealer_codes[message.from_user.id]}!",
            reply_markup=get_start_work_keyboard()
        )
        await state.clear()
    else:
        await message.answer("👋 Привет! Пожалуйста, введите ваш Код Дилера:")
        await state.set_state(Form.waiting_for_code)


@router.message(F.text == "🔄 Сменить Код Дилера")
@router.message(F.text == "/change_code")
async def change_code(message: types.Message, state: FSMContext):
    await message.answer("✏️ Введите новый Код Дилера:")
    await state.set_state(Form.waiting_for_code)


@router.message(Form.waiting_for_code, F.content_type == "text")
async def set_dealer_code(message: types.Message, state: FSMContext):
    dealer_code = message.text.strip()
    dealer_codes[message.from_user.id] = dealer_code
    save_dealer_codes(dealer_codes)

    await message.answer(
        f"✅ Код Дилера установлен: {dealer_code}\nТеперь можете начать работу.",
        reply_markup=get_start_work_keyboard()
    )
    await state.clear()


@router.message(F.text == "Набрать текст")
async def start_typing_text(message: types.Message, state: FSMContext):
    await message.answer("✍️ Пришлите текстовую информацию.", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(Form.waiting_for_text)


@router.message(Form.waiting_for_text, F.content_type == "text")
async def handle_text(message: types.Message, state: FSMContext):
    dealer_code = dealer_codes.get(message.from_user.id, f"user_{message.from_user.id}")
    folder = get_today_folder(dealer_code)
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, f"text_{dealer_code}_{message.message_id}.txt")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(message.text)

    await message.bot.send_message(
        ADMIN_ID,
        f"📩 Новый текст от {dealer_code}:\n{message.text}"
    )

    await message.reply(
        "✅ Текст получен и сохранён.\nТеперь можете прикрепить фото или видео.",
        reply_markup=get_photo_video_keyboard()
    )
    await state.set_state(Form.waiting_more_material)


@router.message(Form.waiting_for_photo)
async def handle_photo(message: types.Message, state: FSMContext):
    if message.content_type != "photo":
        await message.reply("❗ Ожидается фото. Пожалуйста, пришлите фото.")
        return

    dealer_code = dealer_codes.get(message.from_user.id, f"user_{message.from_user.id}")
    folder = get_today_folder(dealer_code)
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, f"photo_{dealer_code}_{message.message_id}.jpg")

    photo = message.photo[-1]  # самый большой размер
    file = await message.bot.get_file(photo.file_id)
    await message.bot.download_file(file.file_path, destination=file_path)

    await message.bot.send_photo(
        ADMIN_ID,
        photo=photo.file_id,
        caption=f"📷 Фото от {dealer_code}"
    )

    await message.reply(
        "✅ Фото получено.\nХотите добавить ещё материал?",
        reply_markup=get_yes_no_keyboard("Добавить ещё", "Завершить отправку")
    )
    await state.set_state(Form.waiting_more_material)


@router.message(Form.waiting_for_video)
async def handle_video(message: types.Message, state: FSMContext):
    if message.content_type != "video":
        await message.reply("❗ Ожидается видео. Пожалуйста, пришлите видео.")
        return

    dealer_code = dealer_codes.get(message.from_user.id, f"user_{message.from_user.id}")
    folder = get_today_folder(dealer_code)
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, f"video_{dealer_code}_{message.message_id}.mp4")

    await message.video.download(destination_file=file_path)

    await message.bot.send_video(
        ADMIN_ID,
        video=message.video.file_id,
        caption=f"🎥 Видео от {dealer_code}"
    )

    await message.reply(
        "✅ Видео получено.\nХотите добавить ещё материал?",
        reply_markup=get_yes_no_keyboard("Добавить ещё", "Завершить отправку")
    )
    await state.set_state(Form.waiting_more_material)


@router.message(Form.waiting_more_material, F.text == "Добавить ещё")
async def more_material(message: types.Message, state: FSMContext):
    await message.answer(
        "Выберите, что хотите добавить:",
        reply_markup=get_photo_video_keyboard()
    )
    # состояние не меняем, остаёмся здесь


@router.message(Form.waiting_more_material, F.text == "Завершить отправку")
async def finish_material(message: types.Message, state: FSMContext):
    await message.answer(
        "📌 Хотите начать новый запрос?",
        reply_markup=get_yes_no_keyboard("Да", "Нет")
    )
    await state.set_state(Form.waiting_new_request)


@router.message(Form.waiting_new_request, F.text == "Да")
async def start_new_request(message: types.Message, state: FSMContext):
    await message.answer("✍️ Пришлите текстовую информацию.", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(Form.waiting_for_text)


@router.message(Form.waiting_new_request, F.text == "Нет")
async def exit_bot(message: types.Message, state: FSMContext):
    await message.answer("✅ Спасибо, данные сохранены. Чтобы начать заново, введите /start", reply_markup=types.ReplyKeyboardRemove())
    await state.clear()


@router.message(Form.waiting_more_material, F.text == "📷 Отправить фото")
async def ask_photo(message: types.Message, state: FSMContext):
    await message.answer("📷 Пришлите фото.", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(Form.waiting_for_photo)


@router.message(Form.waiting_more_material, F.text == "🎥 Отправить видео")
async def ask_video(message: types.Message, state: FSMContext):
    await message.answer("🎥 Пришлите видео.", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(Form.waiting_for_video)