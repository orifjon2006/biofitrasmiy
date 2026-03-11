from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

# Loyiha ichki modullari
from states.client_states import AuthState
from database import authenticate_client, get_admin_by_login
from keyboards.client_kb import main_client_kb
from keyboards.admin_kb import super_admin_main_kb, sub_admin_main_kb
from config import SUPER_ADMIN_ID

router = Router()

# ================= START KOMANDASI =================
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    # Agar foydalanuvchi Super Admin bo'lsa, to'g'ridan-to'g'ri panelni ochish
    if message.from_user.id == SUPER_ADMIN_ID:
        await message.answer(
            f"Xush kelibsiz, Katta Admin! 🛡\nBoshqaruv panelingiz tayyor.",
            reply_markup=super_admin_main_kb()
        )
        return

    await message.answer(
        "Assalomu alaykum! 🌟\n\nBotdan foydalanish uchun sizga berilgan <b>6 xonali loginni</b> kiriting:"
    )
    await state.set_state(AuthState.waiting_for_login)

# ================= LOGINNI QABUL QILISH =================
@router.message(AuthState.waiting_for_login)
async def process_login(message: Message, state: FSMContext):
    if len(message.text) != 6:
        await message.answer("Xato! Login 6 ta belgidan iborat bo'lishi kerak. Qaytadan urinib ko'ring:")
        return
    
    await state.update_data(login=message.text)
    await message.answer("Endi <b>6 xonali parolni</b> kiriting:")
    await state.set_state(AuthState.waiting_for_password)

# ================= PAROLNI VA AVTORIZATSIYANI TEKSHIRISH =================
@router.message(AuthState.waiting_for_password)
async def process_password(message: Message, state: FSMContext):
    password = message.text
    user_data = await state.get_data()
    login = user_data['login']
    telegram_id = message.from_user.id

    # 1. Avval Adminlar bazasidan qidiramiz
    admin = await get_admin_by_login(login, password)
    if admin:
        await state.clear()
        # Adminni telegram_id sini bazada yangilab qo'yamiz (agar kerak bo'lsa)
        await message.answer(
            "Muvaffaqiyatli kirdingiz! Kichik admin paneli aktivlashtirildi. 👨‍💻",
            reply_markup=sub_admin_main_kb()
        )
        return

    # 2. Keyin Mijozlar bazasidan qidiramiz
    client = await authenticate_client(login, password, telegram_id)
    if client:
        await state.clear()
        if not client.is_active:
            await message.answer("⚠️ Uzr, sizning kurs muddatingiz tugagan va kirish cheklangan.")
            return

        await message.answer(
            f"Xush kelibsiz, <b>{client.full_name}</b>! ✨\n"
            "Siz muvaffaqiyatli tizimga kirdingiz. Quyidagi menyudan foydalanishingiz mumkin:",
            reply_markup=main_client_kb()
        )
    else:
        # Agar na admin, na mijoz topilmasa
        await message.answer(
            "❌ <b>Login yoki parol xato!</b>\n"
            "Iltimos, qaytadan tekshirib kiriting yoki adminga murojaat qiling.\n\n"
            "Loginni qaytadan kiriting:"
        )
        await state.set_state(AuthState.waiting_for_login)