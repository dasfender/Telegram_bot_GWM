import os
from aiogram import Router, F, types
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from Project.utils import get_today_folder, load_dealer_codes, save_dealer_codes
from dotenv import load_dotenv


router = Router()
load_dotenv()
ADMIN_ID=os.getenv("ADMIN_ID")
dealer_codes = load_dealer_codes()

router = Router()
dealer_codes = load_dealer_codes()

class Registration(StatesGroup):
    waiting_for_code = State()

@router.message(F.text.startswith("/start"))
async def start_command(message: types.Message, state: FSMContext):
    args = message.text.split()
    user_id = message.from_user.id

    if user_id in dealer_codes:
        await message.answer(
            f"👋 Привет, {dealer_codes[user_id]}!\n"
            "Нажмите 'Новый запрос', чтобы начать.",
            reply_markup=types.ReplyKeyboardMarkup(
                keyboard=[[types.KeyboardButton(text="🆕 Новый запрос")]],
                resize_keyboard=True
            )
        )
    else:
        if len(args) == 2:
            dealer_code = args[1].strip()
            dealer_codes[user_id] = dealer_code
            save_dealer_codes(dealer_codes)
            await message.answer(
                f"✅ Код Дилера зарегистрирован: {dealer_code}\n"
                "Теперь вы можете начать работу, нажав 'Новый запрос'.",
                reply_markup=types.ReplyKeyboardMarkup(
                    keyboard=[[types.KeyboardButton(text="🆕 Новый запрос")]],
                    resize_keyboard=True
                )
            )
        else:
            await message.answer(
                "👋 Привет! Для регистрации введите команду:\n"
                "`/start ВАШ_КОД_ДИЛЕРА`",
                parse_mode="Markdown"
            )

@router.message(F.text == "/change_code")
async def change_code(message: types.Message, state: FSMContext):
    if message.from_user.id == ADMIN_ID:
        await message.answer("Введите ID пользователя и новый код через пробел:\n`123456789 NEWCODE`", parse_mode="Markdown")
    else:
        await message.answer("❌ У вас нет прав для изменения кода дилера.")

@router.message(F.text.regexp(r"^\d+\s+\S+$"))
async def admin_change_code(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        user_id_str, new_code = message.text.split(maxsplit=1)
        user_id = int(user_id_str)
        dealer_codes[user_id] = new_code.strip()
        save_dealer_codes(dealer_codes)
        await message.answer(f"✅ Код дилера для {user_id} изменён на {new_code}")
    except Exception as e:
        await message.answer(f"Ошибка: {e}")
