from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime
from pathlib import Path
import json

router = Router()

BASE_DIR = Path(__file__).parent.parent
DEALER_FILES_DIR = BASE_DIR / "dealer_files"
DEALER_CODES_FILE = BASE_DIR / "dealer_codes.json"
DEALER_FILES_DIR.mkdir(parents=True, exist_ok=True)


def load_dealer_codes():
    if DEALER_CODES_FILE.exists():
        with open(DEALER_CODES_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_dealer_codes(codes):
    with open(DEALER_CODES_FILE, 'w') as f:
        json.dump(codes, f)


class RequestStates(StatesGroup):
    waiting_dealer_code = State()
    waiting_problem_description = State()
    choose_media = State()
    adding_photos = State()
    adding_videos = State()
    confirm_finish = State()


def create_dealer_folder(dealer_code: str) -> Path:
    """Создает папку для запроса с нумерацией от 1 до 99"""
    today = datetime.now().strftime("%Y-%m-%d")
    dealer_date_dir = DEALER_FILES_DIR / dealer_code / today

    request_num = 1
    while request_num <= 99:
        request_folder = dealer_date_dir / f"request_{request_num}"
        if not request_folder.exists():
            request_folder.mkdir(parents=True, exist_ok=True)
            return request_folder
        request_num += 1

    raise ValueError("❌ Достигнут лимит: 99 запросов в день от одного дилера")


def get_main_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Start", callback_data="start_request")
    builder.button(text="Help", callback_data="help")
    builder.adjust(1)
    return builder.as_markup()


@router.callback_query(F.data == "help")
async def show_help(callback: types.CallbackQuery):
    help_text = (
        "📌 <b>Инструкция по работе с ботом</b>\n\n"
        "1. Введите код дилера (формат: DLR123)\n"
        "2. Опишите проблему текстом\n"
        "3. Прикрепите фото/видео (макс. 20 файлов)\n"
        "4. Подтвердите отправку\n\n"
        "Каждый запрос сохраняется в отдельную папку."
    )
    await callback.message.answer(help_text, parse_mode="HTML")
    await callback.answer()


def get_media_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Фото", callback_data="photo")
    builder.button(text="Видео", callback_data="video")
    builder.adjust(1)
    return builder.as_markup()


def get_continue_media_kb(is_photo: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if is_photo:
        builder.button(text="Добавить еще фото", callback_data="continue_photo")
        builder.button(text="Добавить видео", callback_data="switch_to_video")
    else:
        builder.button(text="Добавить еще видео", callback_data="continue_video")
        builder.button(text="Добавить фото", callback_data="switch_to_photo")
    builder.button(text="Завершить добавление", callback_data="finish_media")
    builder.adjust(2, 1)
    return builder.as_markup()


def get_finish_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Подтвердить и отправить", callback_data="finish")
    builder.button(text="Начать заново", callback_data="restart")
    builder.adjust(1)
    return builder.as_markup()


def get_new_request_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Start", callback_data="start_request")
    builder.button(text="Help", callback_data="help")
    builder.adjust(1)
    return builder.as_markup()


@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    dealer_codes = load_dealer_codes()
    user_id = str(message.from_user.id)

    if user_id in dealer_codes:
        dealer_code = dealer_codes[user_id]
        await message.answer(
            f"Привет, {message.from_user.first_name}! Ваш код: {dealer_code}",
            reply_markup=get_main_kb()
        )
    else:
        await message.answer("Введите ваш дилерский код (формат: DLR123):")
        await state.set_state(RequestStates.waiting_dealer_code)


@router.message(RequestStates.waiting_dealer_code)
async def save_dealer_code(message: types.Message, state: FSMContext):
    dealer_code = message.text.strip().upper()
    if not (dealer_code.startswith('DLR') and dealer_code[3:].isdigit()):
        await message.answer("❌ Неверный формат! Используйте DLR123")
        return

    user_id = str(message.from_user.id)
    dealer_codes = load_dealer_codes()
    dealer_codes[user_id] = dealer_code
    save_dealer_codes(dealer_codes)

    # Сохраняем код дилера в state
    await state.update_data(dealer_code=dealer_code)

    await message.answer(
        f"✅ Код {dealer_code} сохранен!",
        reply_markup=get_main_kb()
    )
    await state.set_state(None)

@router.callback_query(F.data == "start_request")
async def start_request(callback: types.CallbackQuery, state: FSMContext):
    dealer_codes = load_dealer_codes()
    user_id = str(callback.from_user.id)

    if user_id not in dealer_codes:
        await callback.answer("❌ Сначала введите код дилера!", show_alert=True)
        return

    # Сохраняем код дилера в state
    await state.update_data(dealer_code=dealer_codes[user_id])

    await callback.message.answer("Опишите проблему:")
    await state.set_state(RequestStates.waiting_problem_description)
    await callback.answer()


@router.message(RequestStates.waiting_problem_description)
async def save_problem_description(message: types.Message, state: FSMContext):
    if not message.text:
        await message.answer("❌ Пожалуйста, введите текст!")
        return

    # Получаем данные пользователя
    user_data = await state.get_data()

    # Проверяем наличие кода дилера
    if "dealer_code" not in user_data:
        # Пытаемся получить код из сохраненных кодов
        dealer_codes = load_dealer_codes()
        user_id = str(message.from_user.id)

        if user_id in dealer_codes:
            dealer_code = dealer_codes[user_id]
            await state.update_data(dealer_code=dealer_code)
            user_data["dealer_code"] = dealer_code
        else:
            await message.answer("❌ Код дилера не найден. Начните заново /start")
            await state.clear()
            return

    try:
        # Создаем папку для запроса
        request_folder = create_dealer_folder(user_data["dealer_code"])
    except ValueError as e:
        await message.answer(str(e))
        return

    # Сохраняем описание проблемы
    with open(request_folder / "description.txt", "w", encoding="utf-8") as f:
        f.write(message.text)

    await state.update_data(
        problem_description=message.text,
        photos=[],
        videos=[],
        current_request_folder=str(request_folder)
    )

    await message.answer("✅ Описание сохранено!")
    await message.answer("Прикрепите материалы:", reply_markup=get_media_kb())
    await state.set_state(RequestStates.choose_media)


@router.callback_query(RequestStates.choose_media)
async def choose_media(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "photo":
        await callback.message.answer(
            "📷 Отправьте фото проблемы\n"
            "⚠️ Принимаются только изображения в формате JPG/PNG",
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.set_state(RequestStates.adding_photos)
    else:
        await callback.message.answer(
            "🎥 Отправьте видео проблемы\n"
            "⚠️ Принимаются только видео в формате MP4/MPEG",
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.set_state(RequestStates.adding_videos)
    await callback.answer()


@router.message(RequestStates.adding_photos)
async def handle_photo_input(message: Message, state: FSMContext):
    if not message.photo:
        await message.answer(
            "❌ Это не фото!\n"
            "Пожалуйста, отправьте изображение в формате JPG/PNG",
            reply_markup=get_continue_media_kb(is_photo=True)
        )
        return

    # Оригинальный код обработки фото
    user_data = await state.get_data()
    request_folder = Path(user_data["current_request_folder"])

    photo_num = len(list(request_folder.glob("photo_*.jpg"))) + 1
    if photo_num > 20:
        await message.answer("❌ Лимит: 20 фото на запрос")
        return

    try:
        photo = message.photo[-1]
        file = await message.bot.get_file(photo.file_id)
        await message.bot.download_file(
            file.file_path,
            destination=request_folder / f"photo_{photo_num}.jpg"
        )

        photos = user_data.get("photos", [])
        photos.append(f"photo_{photo_num}.jpg")
        await state.update_data(photos=photos)

        await message.answer(
            f"✅ Фото {photo_num} сохранено",
            reply_markup=get_continue_media_kb(is_photo=True)
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка сохранения: {str(e)}")


@router.message(RequestStates.adding_videos)
async def handle_video_input(message: Message, state: FSMContext):
    if not message.video:
        await message.answer(
            "❌ Это не видео!\n"
            "Пожалуйста, отправьте видео в формате MP4/MPEG",
            reply_markup=get_continue_media_kb(is_photo=False)
        )
        return

    # Оригинальный код обработки видео
    user_data = await state.get_data()
    request_folder = Path(user_data["current_request_folder"])

    video_num = len(list(request_folder.glob("video_*.mp4"))) + 1
    if video_num > 20:
        await message.answer("❌ Лимит: 20 видео на запрос")
        return

    try:
        video = message.video
        file = await message.bot.get_file(video.file_id)
        await message.bot.download_file(
            file.file_path,
            destination=request_folder / f"video_{video_num}.mp4"
        )

        videos = user_data.get("videos", [])
        videos.append(f"video_{video_num}.mp4")
        await state.update_data(videos=videos)

        await message.answer(
            f"✅ Видео {video_num} сохранено",
            reply_markup=get_continue_media_kb(is_photo=False)
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка сохранения: {str(e)}")


@router.message(RequestStates.adding_photos, F.photo)
async def add_photo(message: Message, state: FSMContext):
    user_data = await state.get_data()
    request_folder = Path(user_data["current_request_folder"])

    # Нумерация фото
    photo_num = len(list(request_folder.glob("photo_*.jpg"))) + 1
    if photo_num > 20:
        await message.answer("❌ Лимит: 20 фото на запрос")
        return

    try:
        photo = message.photo[-1]
        file = await message.bot.get_file(photo.file_id)
        await message.bot.download_file(
            file.file_path,
            destination=request_folder / f"photo_{photo_num}.jpg"
        )

        # Обновляем state
        photos = user_data.get("photos", [])
        photos.append(f"photo_{photo_num}.jpg")
        await state.update_data(photos=photos)

        await message.answer(
            f"✅ Фото {photo_num} сохранено",
            reply_markup=get_continue_media_kb(is_photo=True)
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")


@router.message(RequestStates.adding_videos, F.video)
async def add_video(message: Message, state: FSMContext):
    user_data = await state.get_data()
    request_folder = Path(user_data["current_request_folder"])

    # Нумерация видео
    video_num = len(list(request_folder.glob("video_*.mp4"))) + 1
    if video_num > 20:
        await message.answer("❌ Лимит: 20 видео на запрос")
        return

    try:
        video = message.video
        file = await message.bot.get_file(video.file_id)
        await message.bot.download_file(
            file.file_path,
            destination=request_folder / f"video_{video_num}.mp4"
        )

        videos = user_data.get("videos", [])
        videos.append(f"video_{video_num}.mp4")
        await state.update_data(videos=videos)

        await message.answer(
            f"✅ Видео {video_num} сохранено",
            reply_markup=get_continue_media_kb(is_photo=False)
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")


@router.callback_query(F.data.in_(["switch_to_photo", "switch_to_video"]))
async def switch_media_type(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "switch_to_photo":
        await callback.message.answer("Отправьте фото:")
        await state.set_state(RequestStates.adding_photos)
    else:
        await callback.message.answer("Отправьте видео:")
        await state.set_state(RequestStates.adding_videos)
    await callback.answer()


@router.callback_query(F.data.in_(["continue_photo", "continue_video"]))
async def continue_adding_media(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "continue_photo":
        await callback.message.answer("Отправьте следующее фото:")
        await state.set_state(RequestStates.adding_photos)
    else:
        await callback.message.answer("Отправьте следующее видео:")
        await state.set_state(RequestStates.adding_videos)
    await callback.answer()


@router.callback_query(F.data == "finish_media")
async def finish_adding_media(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Подтвердите отправку запроса:",
        reply_markup=get_finish_kb()
    )
    await state.set_state(RequestStates.confirm_finish)
    await callback.answer()


@router.callback_query(RequestStates.confirm_finish, F.data == "finish")
async def finish_request(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    request_folder = Path(user_data["current_request_folder"])

    if not request_folder.exists():
        await callback.answer("❌ Ошибка: папка запроса не найдена", show_alert=True)
        return

    # Создаем файл с информацией о запросе
    with open(request_folder / "request_info.txt", "w") as f:
        f.write(f"Дилер: {user_data['dealer_code']}\n")
        f.write(f"Дата: {datetime.now()}\n")
        f.write(f"Фото: {len(user_data.get('photos', []))}\n")
        f.write(f"Видео: {len(user_data.get('videos', []))}\n")

    await callback.message.answer(
        f"✅ Запрос #{request_folder.name} сохранен!\n"
        f"Папка: {request_folder}",
        reply_markup=get_new_request_kb()
    )
    await state.clear()
    await callback.answer()


@router.callback_query(RequestStates.confirm_finish, F.data == "restart")
async def restart_request(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Начинаем новый запрос. Опишите проблему:")
    await state.set_state(RequestStates.waiting_problem_description)
    await callback.answer()