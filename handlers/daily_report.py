import random
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

# Loyiha modullari
from database import get_client_by_tg_id, add_daily_report
from keyboards.client_kb import skip_video_kb
from states.client_states import DailyReportState
from config import MOTIVATION_QUOTES, SUPER_ADMIN_ID

router = Router()

# ================= 1-QADAM: BIOFIT ISTE'MOLI HAQIDA JAVOB =================

@router.callback_query(F.data == "biofit_yes")
async def process_biofit_yes(callback: CallbackQuery, state: FSMContext):
    """Mijoz 'Ha' tugmasini bosganida"""
    quote = random.choice(MOTIVATION_QUOTES)
    
    # Eskirgan tugmalarni o'chirib, motivatsiya yuboramiz
    await callback.message.edit_text(f"✅ <b>{quote}</b>")
    
    await callback.message.answer(
        "Endi bajargan mashqlaringiz haqida qisqacha <b>video</b> yuboring:",
        reply_markup=skip_video_kb()
    )
    # Video kutish holatiga o'tamiz
    await state.set_state(DailyReportState.waiting_for_video)
    await state.update_data(consumed=True) # Iste'mol qilganini eslab qolamiz
    await callback.answer()

@router.callback_query(F.data == "biofit_no")
async def process_biofit_no(callback: CallbackQuery, state: FSMContext):
    """Mijoz 'Qabul qilmadim' tugmasini bosganida"""
    await callback.message.edit_text(
        "⚠️ <b>Bu yaxshi emas!</b>\n\n"
        "Biofit mahsulotini o'z vaqtida iste'mol qilish natija uchun juda muhim. "
        "Ertaga albatta qabul qilishga harakat qiling!"
    )
    
    await callback.message.answer(
        "Mahsulot ichmagan bo'lsangiz ham, bajargan mashqlaringiz videosini yuboring:",
        reply_markup=skip_video_kb()
    )
    await state.set_state(DailyReportState.waiting_for_video)
    await state.update_data(consumed=False)
    await callback.answer()

# ================= 2-QADAM: VIDEO HISOBOTNI QABUL QILISH =================

@router.message(DailyReportState.waiting_for_video, F.video)
async def handle_video_report(message: Message, state: FSMContext, bot: Bot):
    """Mijoz video yuborganida"""
    data = await state.get_data()
    consumed_status = data.get("consumed", False)
    
    client = await get_client_by_tg_id(message.from_user.id)
    if not client:
        await message.answer("Xatolik: Mijoz ma'lumotlari topilmadi.")
        return

    # 1. Ma'lumotlar bazasiga saqlash
    await add_daily_report(
        client_id=client.id,
        consumed=consumed_status,
        video_id=message.video.file_id,
        skipped=False
    )
    
    # 2. Katta adminga (Super Admin) videoni yo'naltirish
    status_text = "✅ Ichgan" if consumed_status else "❌ Ichmagan"
    caption = (
        f"📹 <b>Yangi video hisobot!</b>\n\n"
        f"👤 <b>Mijoz:</b> {client.full_name}\n"
        f"🔑 <b>Login:</b> <code>{client.login}</code>\n"
        f"💊 <b>Biofit:</b> {status_text}\n"
        f"📅 <b>Sana:</b> {message.date.strftime('%d.%m.%Y %H:%M')}"
    )
    
    await bot.send_video(
        chat_id=SUPER_ADMIN_ID,
        video=message.video.file_id,
        caption=caption
    )
    
    await message.answer("Rahmat! Hisobotingiz qabul qilindi va adminga yuborildi. 💪")
    await state.clear()

# ================= 3-QADAM: VIDEONI O'TKAZIB YUBORISH =================

@router.callback_query(F.data == "skip_video")
async def skip_video_handler(callback: CallbackQuery, state: FSMContext):
    """Mijoz videoni yubormaslikni tanlaganida"""
    data = await state.get_data()
    consumed_status = data.get("consumed", False)
    
    client = await get_client_by_tg_id(callback.from_user.id)
    
    # Bazaga video yuborilmaganini belgilaymiz
    await add_daily_report(
        client_id=client.id,
        consumed=consumed_status,
        video_id=None,
        skipped=True
    )
    
    await callback.message.edit_text("Xo'p, mashqlar videosi yuborilmadi. Intizomni susaytirmang! 😉")
    await state.clear()
    await callback.answer()