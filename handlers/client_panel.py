import random
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InputMediaVideo
from aiogram.fsm.context import FSMContext

# Loyiha modullari
from database import get_client_by_tg_id, add_daily_report
from keyboards.client_kb import main_client_kb, biofit_query_kb, skip_video_kb
from states.client_states import DailyReportState
from config import EXERCISES, MOTIVATION_QUOTES, SUPER_ADMIN_ID

router = Router()

# ================= ASOSIY MENYU FUNKSIYALARI =================

@router.message(F.text == "🏋️ Mashqlar ro'yxati")
async def show_exercises(message: Message):
    text = "<b>Bugungi mashqlar to'plami:</b>\n\n"
    for ex in EXERCISES:
        text += f"🔹 {ex['name']}\n"
    
    text += "\n<i>Mashqlarni tartib bilan bajaring va natijaga erishing!</i>"
    await message.answer(text)

@router.message(F.text == "📈 Natijamni ko'rish")
async def show_results(message: Message):
    client = await get_client_by_tg_id(message.from_user.id)
    if client:
        # Muddatni hisoblash
        import datetime
        remaining = (client.end_date - datetime.datetime.utcnow()).days
        
        text = (
            f"👤 <b>Foydalanuvchi:</b> {client.full_name}\n"
            f"📅 <b>Kurs boshlangan:</b> {client.start_date.strftime('%d.%m.%Y')}\n"
            f"🏁 <b>Kurs tugaydi:</b> {client.end_date.strftime('%d.%m.%Y')}\n"
            f"⏳ <b>Qolgan vaqt:</b> {max(0, remaining)} kun\n\n"
            f"🚀 <i>Siz to'g'ri yo'ldasiz, to'xtab qolmang!</i>"
        )
        await message.answer(text)

@router.message(F.text == "🤖 Yordamchini aktivlashtirish")
async def activate_helper(message: Message):
    await message.answer(
        "🤖 <b>BIOFIT Yordamchisi aktiv!</b>\n\n"
        "Sizga har kuni mashqlarni bajarishda va mahsulotni o'z vaqtida iste'mol qilishda ko'maklashaman. "
        "Savollaringiz bo'lsa, adminga murojaat qilishingiz mumkin."
    )

# ================= BIOFIT SO'ROVNOMASI (CALLBACKS) =================

@router.callback_query(F.data == "biofit_yes")
async def process_biofit_yes(callback: CallbackQuery, state: FSMContext):
    # Tasodifiy motivatsion gap tanlash
    quote = random.choice(MOTIVATION_QUOTES)
    await callback.message.edit_text(f"✅ {quote}")
    
    # Keyingi bosqich: Video so'rash
    await callback.message.answer(
        "Endi bajargan mashqlaringiz haqida qisqacha video yuboring:",
        reply_markup=skip_video_kb()
    )
    await state.set_state(DailyReportState.waiting_for_video)
    await callback.answer()

@router.callback_query(F.data == "biofit_no")
async def process_biofit_no(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "❌ <b>Bu yaxshi emas!</b>\n\n"
        "Mahsulotni o'z vaqtida iste'mol qilish natija uchun juda muhim. "
        "Iltimos, sog'lig'ingizga mas'uliyat bilan yondashing."
    )
    
    # Shunda ham video so'raymiz (mashq qilgan bo'lishi mumkin)
    await callback.message.answer(
        "Mashqlar jarayoni haqida qisqacha video yuboring:",
        reply_markup=skip_video_kb()
    )
    await state.set_state(DailyReportState.waiting_for_video)
    await callback.answer()

# ================= VIDEO QABUL QILISH VA ADMINGA YUBORISH =================

@router.message(DailyReportState.waiting_for_video, F.video)
async def handle_video_report(message: Message, state: FSMContext, bot: Bot):
    client = await get_client_by_tg_id(message.from_user.id)
    
    # Bazaga saqlash
    await add_daily_report(
        client_id=client.id,
        consumed=True, # Bu yerda callback dan kelgan qiymatni saqlash ham mumkin
        video_id=message.video.file_id
    )
    
    # Adminga yuborish
    await bot.send_video(
        chat_id=SUPER_ADMIN_ID,
        video=message.video.file_id,
        caption=f"📹 <b>Yangi hisobot keldi!</b>\n\n👤 Mijoz: {client.full_name}\nID: {client.id}\nLogin: {client.login}"
    )
    
    await message.answer("Rahmat! Hisobotingiz qabul qilindi va adminga yuborildi. 💪")
    await state.clear()

@router.callback_query(F.data == "skip_video")
async def skip_video_handler(callback: CallbackQuery, state: FSMContext):
    client = await get_client_by_tg_id(callback.from_user.id)
    
    # Bazaga video yubormaganini belgilab qo'yamiz
    await add_daily_report(client_id=client.id, consumed=True, skipped=True)
    
    await callback.message.edit_text("Xo'p, mashqlar videosi yuborilmadi. Ertaga albatta kutiladi! 😉")
    await state.clear()
    await callback.answer()