from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from sqlalchemy.future import select

# Loyiha modullari
from states.admin_states import ClientAdd
from keyboards.admin_kb import course_duration_kb, sub_admin_main_kb, super_admin_main_kb, cancel_kb
from database import add_client, async_session, Admin, Client
from config import SUPER_ADMIN_ID
from utils.generator import generate_credentials # Agar bu funksiyani config.py da qoldirgan bo'lsangiz, shunday o'zgartiring: from config import generate_credentials

router = Router()

# ================= XAVFSIZLIK FILTRI =================
# Bu funksiya yozayotgan odam yo Katta Admin, yo ro'yxatdan o'tgan faol Kichik Admin ekanligini tekshiradi.
async def check_admin_access(message: Message) -> bool:
    if message.from_user.id == SUPER_ADMIN_ID:
        return True
        
    async with async_session() as session:
        # Kichik admin login qilib kirganida uning telegram_id si bazaga saqlangan bo'lishi kerak
        result = await session.execute(
            select(Admin).where(Admin.telegram_id == message.from_user.id, Admin.is_active == True)
        )
        return result.scalars().first() is not None

# Butun router uchun ushbu xavfsizlik filtrini o'rnatamiz
router.message.filter(check_admin_access)


# ================= BEKOR QILISH =================
@router.message(F.text == "🚫 Bekor qilish")
async def cancel_handler(message: Message, state: FSMContext):
    await state.clear()
    
    # Kim bekor qilayotganiga qarab to'g'ri menyuni ko'rsatamiz
    if message.from_user.id == SUPER_ADMIN_ID:
        kb = super_admin_main_kb()
    else:
        kb = sub_admin_main_kb()
        
    await message.answer("❌ Barcha amallar bekor qilindi. Bosh menyudasiz.", reply_markup=kb)


# ================= MIJOZ QO'SHISH JARAYONI (FSM) =================

@router.message(F.text.in_(["👤 Mijoz qo'shish", "👤 Mijoz ro'yxatga olish"]))
async def start_add_client(message: Message, state: FSMContext):
    await message.answer(
        "📝 <b>Yangi mijozni ro'yxatga olishni boshlaymiz.</b>\n\n"
        "Iltimos, mijozning <b>Ism va Familiyasini</b> to'liq kiriting:", 
        reply_markup=cancel_kb()
    )
    await state.set_state(ClientAdd.waiting_for_name)

@router.message(ClientAdd.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await message.answer(
        f"✅ Qabul qilindi: <b>{message.text}</b>\n\n"
        "Endi mijozning <b>yashash manzilini</b> kiriting (Shahar, tuman):"
    )
    await state.set_state(ClientAdd.waiting_for_address)

@router.message(ClientAdd.waiting_for_address)
async def process_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    await message.answer(
        "📱 Mijozning <b>telefon raqamini</b> kiriting:\n"
        "<i>(Masalan: +998901234567)</i>"
    )
    await state.set_state(ClientAdd.waiting_for_phone)

@router.message(ClientAdd.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer(
        "⏳ Mijoz necha oylik kurs xarid qildi?\n\n"
        "Quyidagi tugmalardan birini tanlang:",
        reply_markup=course_duration_kb()
    )
    await state.set_state(ClientAdd.waiting_for_duration)

@router.message(ClientAdd.waiting_for_duration)
async def process_duration(message: Message, state: FSMContext):
    # Tugma to'g'ri bosilganini tekshiramiz
    if "oylik" not in message.text.lower():
        await message.answer("⚠️ Iltimos, pastdagi klaviaturadagi tugmalardan birini tanlang!")
        return

    # "3 oylik" matnidan faqat raqamni (3 ni) ajratib olamiz
    try:
        duration_months = int(message.text.split()[0])
    except ValueError:
        await message.answer("⚠️ Oylikni aniqlashda xatolik. Qaytadan urinib ko'ring.")
        return

    user_data = await state.get_data()
    
    # 6 talik xavfsiz login va parol generatsiyasi
    client_login = generate_credentials(6)
    client_password = generate_credentials(6)
    
    try:
        # Ma'lumotlar bazasiga saqlash
        new_client = await add_client(
            full_name=user_data['full_name'],
            address=user_data['address'],
            phone=user_data['phone'],
            months=duration_months,
            login=client_login,
            password=client_password
        )
        
        # Muvaffaqiyatli saqlangach, to'g'ri menyuga qaytarish
        if message.from_user.id == SUPER_ADMIN_ID:
            kb = super_admin_main_kb()
        else:
            kb = sub_admin_main_kb()
            
        response_text = (
            f"🎉 <b>Mijoz muvaffaqiyatli ro'yxatga olindi!</b>\n\n"
            f"👤 <b>Ism:</b> {user_data['full_name']}\n"
            f"📍 <b>Manzil:</b> {user_data['address']}\n"
            f"📞 <b>Tel:</b> {user_data['phone']}\n"
            f"📅 <b>Muddati:</b> {duration_months} oy\n"
            f"🏁 <b>Tugash sanasi:</b> {new_client.end_date.strftime('%d.%m.%Y')}\n\n"
            f"🔑 <b>LOGIN:</b> <code>{client_login}</code>\n"
            f"🔐 <b>PAROL:</b> <code>{client_password}</code>\n\n"
            f"<i>Ushbu xabarni nusxalab mijozga yuboring. U botga kirishda aynan shu login va paroldan foydalanadi.</i>"
        )
        
        await message.answer(response_text, reply_markup=kb)
        await state.clear()
        
    except Exception as e:
        await message.answer(f"⚠️ Ma'lumotlar bazasiga saqlashda xatolik yuz berdi: {e}")
        await state.clear()


# ================= MIJOZNI CHETLATISH =================

@router.message(F.text.in_(["🚫 Mijoz chetlatish", "🚫 Mijozni chetlatish"]))
async def prompt_deactivate_client(message: Message):
    await message.answer(
        "🚫 <b>Mijozni tizimdan chetlatish</b>\n\n"
        "Chetlatmoqchi bo'lgan mijozingizning <b>6 xonali loginini</b> yuboring:",
        reply_markup=cancel_kb()
    )

# Agar admin roppa-rosa 6 ta belgi yuborsa, bu login deb faraz qilamiz
@router.message(F.text.len() == 6)
async def process_deactivation(message: Message):
    login_to_search = message.text
    
    async with async_session() as session:
        # Avval login bo'yicha mijozni topamiz
        result = await session.execute(select(Client).where(Client.login == login_to_search))
        client = result.scalars().first()
        
        if not client:
            await message.answer("⚠️ Bunday loginli mijoz topilmadi. Qaytadan tekshirib yozing:")
            return
            
        if not client.is_active:
            await message.answer(f"❕ <b>{client.full_name}</b> allaqachon botdan chetlatilgan.")
            return
            
        # Mijozni chetlatamiz (holatini o'zgartiramiz va telegram_id sini uzib qo'yamiz)
        client.is_active = False
        client.telegram_id = None
        await session.commit()
        
        # Adminni oldingi menyusiga qaytarish
        if message.from_user.id == SUPER_ADMIN_ID:
            kb = super_admin_main_kb()
        else:
            kb = sub_admin_main_kb()
            
        await message.answer(
            f"✅ <b>{client.full_name}</b> muvaffaqiyatli tizimdan chetlatildi.\n"
            f"Endi bu mijoz botga kira olmaydi, lekin uning ma'lumotlari arxivda saqlanadi.",
            reply_markup=kb
        )
