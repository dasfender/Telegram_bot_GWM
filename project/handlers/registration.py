from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from project.utils.dealer_utils import load_dealer_codes, save_dealer_codes

router = Router()

class Registration(StatesGroup):
    waiting_for_dealer_code = State()

@router.message(Command("start"))
async def start_registration(message: types.Message, state: FSMContext):
    codes = load_dealer_codes()
    if str(message.from_user.id) in codes:
        await message.answer(f"Привет! Ваш дилерский код: {codes[str(message.from_user.id)]}\nВы можете начать работу.")
        return
    await message.answer("Введите ваш дилерский код:")
    await state.set_state(Registration.waiting_for_dealer_code)

@router.message(Registration.waiting_for_dealer_code)
async def save_dealer_code(message: types.Message, state: FSMContext):
    dealer_code = message.text.strip()
    codes = load_dealer_codes()
    codes[str(message.from_user.id)] = dealer_code
    save_dealer_codes(codes)
    await message.answer(f"Ваш дилерский код сохранён: {dealer_code}\nВы можете начинать работу.")
    await state.clear()
