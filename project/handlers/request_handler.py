from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime
from pathlib import Path
import os
import json

router = Router()

# Настройка папки для хранения файлов
BASE_DIR = Path(__file__).parent.parent
DEALER_FILES_DIR = BASE_DIR / "dealer_files"
DEALER_CODES_FILE = BASE_DIR / "dealer_codes.json"
DEALER_FILES_DIR.mkdir(parents=True, exist_ok=True)


# Загрузка и сохранение кодов дилеров
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


# Функции для создания клавиатур
def get_main_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Start", callback_data="start_request")
    builder.button(text="Help", callback_data="help")
    builder.adjust(1)
    return builder.as_markup()


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


def create_dealer_folder(dealer_code: str) -> Path:
    today = datetime.now().strftime("%Y-%m-%d")
    dealer_folder = DEALER_FILES_DIR / dealer_code / today
    dealer_folder.mkdir(parents=True, exist_ok=True)
    return dealer_folder


# Команда /start
@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    dealer_codes = load_dealer_codes()
    user_id = str(message.from_user.id)

    if user_id in dealer_codes:
        dealer_code = dealer_codes[user_id]
        await message.answer(
            f"Привет, {message.from_user.first_name}! Ваш дилерский код: {dealer_code}\n"
            "Выберите действие:",
            reply_markup=get_main_kb()
        )
    else:
        await message.answer(
            "Добро пожаловать! Пожалуйста, введите ваш дилерский код:"
        )
        await state.set_state(RequestStates.waiting_dealer_code)


# Сохранение дилерского кода
@router.message(RequestStates.waiting_dealer_code)
async def save_dealer_code(message: types.Message, state: FSMContext):
    dealer_code = message.text.strip()
    if len(dealer_code) < 3:
        await message.answer("Код дилера должен содержать минимум 3 символа. Попробуйте еще раз:")
        return

    user_id = str(message.from_user.id)
    dealer_codes = load_dealer_codes()
    dealer_codes[user_id] = dealer_code
    save_dealer_codes(dealer_codes)

    await state.update_data(dealer_code=dealer_code)
    await message.answer(
        f"Ваш дилерский код {dealer_code} успешно сохранен!\n"
        "Теперь вы можете начать новый запрос.",
        reply_markup=get_main_kb()
    )
    await state.set_state(None)


# Начало нового запроса
@router.callback_query(F.data == "start_request")
async def start_request(callback: types.CallbackQuery, state: FSMContext):
    dealer_codes = load_dealer_codes()
    user_id = str(callback.from_user.id)

    if user_id not in dealer_codes:
        await callback.answer("Сначала установите ваш дилерский код!", show_alert=True)
        return

    dealer_code = dealer_codes[user_id]
    await state.update_data(dealer_code=dealer_code)
    await callback.message.answer(
        "Опишите проблему или вопрос максимально подробно:",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(RequestStates.waiting_problem_description)
    await callback.answer()


# Сохранение описания проблемы
@router.message(RequestStates.waiting_problem_description)
async def save_problem_description(message: types.Message, state: FSMContext):
    if message.content_type != "text":
        await message.answer("Пожалуйста, введите текстовое описание!")
        return

    user_data = await state.get_data()
    dealer_code = user_data["dealer_code"]

    # Создаем папку для файлов
    dealer_folder = create_dealer_folder(dealer_code)

    # Сохраняем описание в файл
    description_file = dealer_folder / "description.txt"
    with open(description_file, "w", encoding="utf-8") as f:
        f.write(message.text)

    await state.update_data(
        problem_description=message.text,
        photos=[],
        videos=[]
    )

    await message.answer("Спасибо за обращение! Текст сохранен!")
    await message.answer(
        "Хотите прикрепить фото или видео материалы?",
        reply_markup=get_media_kb()
    )
    await state.set_state(RequestStates.choose_media)


# Выбор типа медиа
@router.callback_query(RequestStates.choose_media)
async def choose_media(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "photo":
        await callback.message.answer(
            "Пожалуйста, отправьте фото:",
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.set_state(RequestStates.adding_photos)
    elif callback.data == "video":
        await callback.message.answer(
            "Пожалуйста, отправьте видео:",
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.set_state(RequestStates.adding_videos)
    await callback.answer()


# Добавление фото
@router.message(RequestStates.adding_photos, F.photo)
async def add_photo(message: Message, state: FSMContext):
    user_data = await state.get_data()
    dealer_code = user_data["dealer_code"]
    dealer_folder = create_dealer_folder(dealer_code)

    photos = user_data.get("photos", [])
    if len(photos) >= 20:
        await message.answer("Максимальное количество фото - 20. Завершите добавление.")
        return

    photo = message.photo[-1]
    file_id = photo.file_id
    file_path = dealer_folder / f"photo_{len(photos) + 1}.jpg"

    file = await message.bot.get_file(file_id)
    await message.bot.download_file(file.file_path, destination=file_path)

    photos.append(str(file_path))
    await state.update_data(photos=photos)

    await message.answer(
        f"Фото {len(photos)} успешно добавлено!",
        reply_markup=get_continue_media_kb(is_photo=True)
    )


@router.message(RequestStates.adding_photos)
async def wrong_photo_input(message: Message):
    await message.answer("Пожалуйста, отправьте фото!")


# Добавление видео
@router.message(RequestStates.adding_videos, F.video)
async def add_video(message: Message, state: FSMContext):
    user_data = await state.get_data()
    dealer_code = user_data["dealer_code"]
    dealer_folder = create_dealer_folder(dealer_code)

    videos = user_data.get("videos", [])
    if len(videos) >= 20:
        await message.answer("Максимальное количество видео - 20. Завершите добавление.")
        return

    video = message.video
    file_id = video.file_id
    file_path = dealer_folder / f"video_{len(videos) + 1}.mp4"

    file = await message.bot.get_file(file_id)
    await message.bot.download_file(file.file_path, destination=file_path)

    videos.append(str(file_path))
    await state.update_data(videos=videos)

    await message.answer(
        f"Видео {len(videos)} успешно добавлено!",
        reply_markup=get_continue_media_kb(is_photo=False)
    )


@router.message(RequestStates.adding_videos)
async def wrong_video_input(message: Message):
    await message.answer("Пожалуйста, отправьте видео!")


# Переключение между фото и видео
@router.callback_query(F.data.in_(["switch_to_photo", "switch_to_video"]))
async def switch_media_type(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "switch_to_photo":
        await callback.message.answer("Отправьте фото:")
        await state.set_state(RequestStates.adding_photos)
    else:
        await callback.message.answer("Отправьте видео:")
        await state.set_state(RequestStates.adding_videos)
    await callback.answer()


# Продолжить/завершить добавление медиа
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
        "Хотите завершить запрос и отправить данные?",
        reply_markup=get_finish_kb()
    )
    await state.set_state(RequestStates.confirm_finish)
    await callback.answer()


# Завершение запроса
@router.callback_query(RequestStates.confirm_finish, F.data == "finish")
async def finish_request(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    dealer_code = user_data["dealer_code"]

    await callback.message.answer(
        f"Спасибо за ваш запрос, дилер {dealer_code}!\n"
        "Все данные сохранены.",
        reply_markup=get_new_request_kb()
    )
    await state.clear()
    await callback.answer()


@router.callback_query(RequestStates.confirm_finish, F.data == "restart")
async def restart_request(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Начинаем новый запрос. Опишите проблему:",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(RequestStates.waiting_problem_description)
    await callback.answer()