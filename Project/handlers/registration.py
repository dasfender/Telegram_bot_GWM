import os
from ..utils.dealer_utils import load_dealer_codes, save_dealer_codes
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv

router = Router()
dealer_codes = load_dealer_codes()
load_dotenv()
ADMIN_ID = int(os.getenv("ADMIN_ID"))

dealer_codes = load_dealer_codes()

class RegistrationForm(StatesGroup):
    waiting_for_code = State()

def get_text_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📝 Набрать текст")]],
        resize_keyboard=True
    )

@router.message(F.text == "/start")
async def start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id in dealer_codes:
        await message.answer(
            f"👋 Привет, {dealer_codes[user_id]}!\n"
            "Выберите действие:",
            reply_markup=get_text_keyboard()
        )
        await state.clear()
    else:
        await message.answer(
            "👋 Привет! Пожалуйста, введите ваш Код Дилера для регистрации:"
        )
        await state.set_state(RegistrationForm.waiting_for_code)

@router.message(RegistrationForm.waiting_for_code, F.content_type == "text")
async def set_dealer_code(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    dealer_code = message.text.strip()
    dealer_codes[user_id] = dealer_code
    save_dealer_codes(dealer_codes)

    await message.answer(
        f"✅ Ваш Код Дилера установлен: {dealer_code}\n"
        "Теперь выберите действие:",
        reply_markup=get_text_keyboard()
    )
    await state.clear()
