import os
from aiogram import types, F, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


class Form(StatesGroup):
    waiting_text = State()
    waiting_media_choice = State()
    waiting_photo = State()
    continue_photo = State()
    waiting_video = State()
    close_request = State()

DEALER_CODES = {}  # user_id: dealer_code

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

main_menu = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Start"), KeyboardButton(text="Help")]],
    resize_keyboard=True
)


def get_user_dir(user_id, dealer_code):
    user_folder = os.path.join(DATA_DIR, f"{user_id}_{dealer_code}")
    photos_folder = os.path.join(user_folder, "photos")
    videos_folder = os.path.join(user_folder, "videos")
    os.makedirs(photos_folder, exist_ok=True)
    os.makedirs(videos_folder, exist_ok=True)
    return user_folder, photos_folder, videos_folder


def register_handlers_user(dp: Dispatcher):

    # /start
    @dp.message(Command("start"))
    async def cmd_start(message: types.Message, state: FSMContext):
        user_id = message.from_user.id
        username = message.from_user.first_name
        dealer_code = DEALER_CODES.get(user_id, "не указан")
        await message.answer(f"Привет, {username}! Ваш дилерский код: {dealer_code}", reply_markup=main_menu)
        await state.clear()


    @dp.message(F.text == "Start")
    async def start_info(message: types.Message, state: FSMContext):
        await message.answer("Введите текст для информации:", reply_markup=ReplyKeyboardRemove())
        await state.set_state(Form.waiting_text)


    @dp.message(Form.waiting_text)
    async def process_text(message: types.Message, state: FSMContext):
        await state.update_data(info_text=message.text)

        user_id = message.from_user.id
        dealer_code = DEALER_CODES.get(user_id, "не указан")
        user_folder, _, _ = get_user_dir(user_id, dealer_code)
        with open(os.path.join(user_folder, "text.txt"), "w", encoding="utf-8") as f:
            f.write(message.text)

        media_menu = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Фото"), KeyboardButton(text="Видео")]],
            resize_keyboard=True
        )
        await message.answer("Хотите добавить фото или видео?", reply_markup=media_menu)
        await state.set_state(Form.waiting_media_choice)


    @dp.message(Form.waiting_media_choice)
    async def choose_media(message: types.Message, state: FSMContext):
        if message.text == "Фото":
            await message.answer("Добавьте фото:", reply_markup=ReplyKeyboardRemove())
            await state.set_state(Form.waiting_photo)
        elif message.text == "Видео":
            await message.answer("Добавьте видео:", reply_markup=ReplyKeyboardRemove())
            await state.set_state(Form.waiting_video)


    @dp.message(Form.waiting_photo, F.content_type == ["photo"])
    async def process_photo(message: types.Message, state: FSMContext):
        user_id = message.from_user.id
        dealer_code = DEALER_CODES.get(user_id, "не указан")
        _, photos_folder, _ = get_user_dir(user_id, dealer_code)

        file_id = message.photo[-1].file_id
        file_path = os.path.join(photos_folder, f"{file_id}.jpg")
        await message.photo[-1].download(destination_file=file_path)

        continue_menu = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Да"), KeyboardButton(text="Нет")]],
            resize_keyboard=True
        )
        await message.answer("Хотите продолжить добавлять фото?", reply_markup=continue_menu)
        await state.set_state(Form.continue_photo)


    @dp.message(Form.continue_photo)
    async def continue_photo(message: types.Message, state: FSMContext):
        if message.text == "Да":
            await message.answer("Добавьте ещё фото:", reply_markup=ReplyKeyboardRemove())
            await state.set_state(Form.waiting_photo)
        else:
            continue_video_menu = ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="Да"), KeyboardButton(text="Нет")]],
                resize_keyboard=True
            )
            await message.answer("Хотите добавить видео?", reply_markup=continue_video_menu)
            await state.set_state(Form.waiting_video)


    @dp.message(Form.waiting_video, F.content_type == ["video"])
    async def process_video(message: types.Message, state: FSMContext):
        user_id = message.from_user.id
        dealer_code = DEALER_CODES.get(user_id, "не указан")
        _, _, videos_folder = get_user_dir(user_id, dealer_code)

        file_id = message.video.file_id
        file_path = os.path.join(videos_folder, f"{file_id}.mp4")
        await message.video.download(destination_file=file_path)

        close_menu = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Да"), KeyboardButton(text="Нет")]],
            resize_keyboard=True
        )
        await message.answer("Хотите закрыть запрос?", reply_markup=close_menu)
        await state.set_state(Form.close_request)


    @dp.message(Form.close_request)
    async def close_request(message: types.Message, state: FSMContext):
        if message.text == "Да":
            await message.answer("Спасибо за ваш запрос, данные сохранены", reply_markup=main_menu)
            await state.clear()
        else:
            media_menu = ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="Фото"), KeyboardButton(text="Видео")]],
                resize_keyboard=True
            )
            await message.answer("Выберите фото или видео:", reply_markup=media_menu)
            await state.set_state(Form.waiting_media_choice)


    @dp.message(F.text == "Help")
    async def help_message(message: types.Message):
        await message.answer("Используйте кнопку Start для начала работы.")
