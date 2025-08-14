from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

# FSM состояния пользователя
class RequestStates(StatesGroup):
    waiting_text = State()
    choose_media = State()
    adding_photos = State()
    adding_videos = State()
    confirm_finish = State()

# Функции для создания клавиатур
def get_main_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Start", callback_data="start")
    builder.button(text="Help", callback_data="help")
    builder.adjust(1)
    return builder.as_markup()

def get_media_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Фото", callback_data="photo")
    builder.button(text="Видео", callback_data="video")
    builder.adjust(1)
    return builder.as_markup()

def get_continue_photo_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Да", callback_data="continue_photo")
    builder.button(text="Нет", callback_data="stop_photo")
    return builder.as_markup()

def get_video_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Да", callback_data="add_video")
    builder.button(text="Нет", callback_data="skip_video")
    return builder.as_markup()

def get_finish_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Да", callback_data="finish")
    builder.button(text="Нет", callback_data="restart")
    return builder.as_markup()

# Команда /start
@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    dealer_code = user_data.get("dealer_code", "не указан")
    await message.answer(
        f"Привет, {message.from_user.first_name}! Ваш дилерский код: {dealer_code}\nВыберите действие:",
        reply_markup=get_main_kb()
    )

# Обработка кнопки Start
@router.callback_query(F.data == "start")
async def start_request(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите текст для информации:")
    await state.set_state(RequestStates.waiting_text)
    await callback.answer()

# Сохранение текста
@router.message(RequestStates.waiting_text)
async def save_text(message: types.Message, state: FSMContext):
    await state.update_data(info_text=message.text)
    await message.answer("Хотите добавить фото или видео?", reply_markup=get_media_kb())
    await state.set_state(RequestStates.choose_media)

# Выбор медиа
@router.callback_query(RequestStates.choose_media)
async def choose_media(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "photo":
        await callback.message.answer("Добавьте фото:")
        await state.set_state(RequestStates.adding_photos)
    elif callback.data == "video":
        await callback.message.answer("Добавьте видео:")
        await state.set_state(RequestStates.adding_videos)
    await callback.answer()

# Добавление фото
@router.message(RequestStates.adding_photos, F.photo)
async def add_photos(message: types.Message, state: FSMContext):
    photos = (await state.get_data()).get("photos", [])
    photos.append(message.photo[-1].file_id)
    await state.update_data(photos=photos)
    await message.answer("Хотите продолжить добавлять фото?", reply_markup=get_continue_photo_kb())

# Продолжить фото
@router.callback_query(F.data == "continue_photo")
async def continue_photo(callback: types.CallbackQuery):
    await callback.message.answer("Добавьте еще фото:")
    await callback.answer()

# Прекратить добавление фото
@router.callback_query(F.data == "stop_photo")
async def stop_photo(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Хотите добавить видео?", reply_markup=get_video_kb())
    await state.set_state(RequestStates.adding_videos)
    await callback.answer()

# Добавление видео
@router.message(RequestStates.adding_videos, F.video)
async def add_video(message: types.Message, state: FSMContext):
    await state.update_data(video_id=message.video.file_id)
    await message.answer("Хотите закрыть запрос?", reply_markup=get_finish_kb())
    await state.set_state(RequestStates.confirm_finish)

# Обработка видео да/нет
@router.callback_query(RequestStates.adding_videos)
async def process_video_choice(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "add_video":
        await callback.message.answer("Добавьте видео:")
    elif callback.data == "skip_video":
        await callback.message.answer("Хотите закрыть запрос?", reply_markup=get_finish_kb())
        await state.set_state(RequestStates.confirm_finish)
    await callback.answer()

# Завершение запроса
@router.callback_query(RequestStates.confirm_finish)
async def finish_request(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "finish":
        await callback.message.answer("Спасибо за ваш запрос, данные сохранены!")
        await state.clear()
    elif callback.data == "restart":
        await callback.message.answer("Можете добавить фото или видео снова", reply_markup=get_media_kb())
        await state.set_state(RequestStates.choose_media)
    await callback.answer()