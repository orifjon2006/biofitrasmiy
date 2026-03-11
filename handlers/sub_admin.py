from aiogram import Router, F, Bot
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

# Loyihamiz ichki modullari
from states.admin_states import ClientAdd
from keyboards.admin_kb import course_duration_kb, sub_admin_main_kb, cancel_kb
from database import add_client, deactivate_client, get_all_clients
from config import generate_credentials

router = Router()

# ================= BEKOR QILISH TUGMASI =================
@router.message(F.text == "🚫 Bekor qilish")
async def cancel_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Amal bekor qilindi. Bosh menyudasiz.",
        reply_markup=sub_admin_main_kb()
    )
from database import async_session, Admin
from sqlalchemy.future import select

# Xabarni yuborgan odam bazada admin ekanligini tekshirish
async def is_sub_admin(message: Message):
    async with async_session() as session:
        result = await session.execute(
            select(Admin).where(Admin.telegram_id == message.from_user.id)
        )
        return result.scalars().first() is not None

# Barcha xabarlarga ushbu filtrni ulash
router.message.filter(is_sub_admin)
# ================= MIJOZ QO'SHISH JARAYONI (START) =================

@router.message(F.text == "👤 Mijoz qo'shish")
@router.message(F.text == "👤 Mijoz ro'yxatga olish") # Katta admin uchun ham
async def start_add_client(message: Message, state: FSMContext):
    await message.answer("Yangi mijozning <b>Ism va Familiyasini</b> kiriting:", reply_markup=cancel_kb())
    await state.set_state(ClientAdd.waiting_for_name)

@router.message(ClientAdd.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await message.answer(f"Rahmat, <b>{message.text}</b>. Endi mijozning <b>yashash manzilini</b> kiriting:")
    await state.set_state(ClientAdd.waiting_for_address)

@router.message(ClientAdd.waiting_for_address)
async def process_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    await message.answer("Mijozning <b>telefon raqamini</b> kiriting (masalan: +998901234567):")
    await state.set_state(ClientAdd.waiting_for_phone)

@router.message(ClientAdd.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer(
        "Mijoz necha oylik kurs xarid qildi? Quyidagilardan birini tanlang:",
        reply_markup=course_duration_kb()
    )
    await state.set_state(ClientAdd.waiting_for_duration)

@router.message(ClientAdd.waiting_for_duration)
async def process_duration(message: Message, state: FSMContext):
    if "oylik" not in message.text:
        await message.answer("Iltimos, pastdagi tugmalardan birini tanlang!")
        return

    duration_months = int(message.text.split()[0])
    user_data = await state.get_data()
    
    # --- Login va Parol generatsiyasi ---
    client_login = generate_credentials(6)
    client_password = generate_credentials(6)
    
    # --- Bazaga saqlash ---
    try:
        new_client = await add_client(
            full_name=user_data['full_name'],
            address=user_data['address'],
            phone=user_data['phone'],
            months=duration_months,
            login=client_login,
            password=client_password
        )
        
        # --- Adminga hisobot va mijoz uchun ma'lumotlar ---
        response_text = (
            f"✅ <b>Mijoz muvaffaqiyatli ro'yxatga olindi!</b>\n\n"
            f"👤 <b>Ism:</b> {user_data['full_name']}\n"
            f"📍 <b>Manzil:</b> {user_data['address']}\n"
            f"📞 <b>Tel:</b> {user_data['phone']}\n"
            f"📅 <b>Muddati:</b> {duration_months} oy\n"
            f"🏁 <b>Tugash sanasi:</b> {new_client.end_date.strftime('%d.%m.%Y')}\n\n"
            f"🔑 <b>LOGIN:</b> <code>{client_login}</code>\n"
            f"🔐 <b>PAROL:</b> <code>{client_password}</code>\n\n"
            f"<i>Ushbu login va parolni mijozga yuboring.</i>"
        )
        
        await message.answer(response_text, reply_markup=sub_admin_main_kb())
        await state.clear()
        
    except Exception as e:
        await message.answer(f"Xatolik yuz berdi: {e}", reply_markup=sub_admin_main_kb())
        await state.clear()

# ================= MIJOZNI CHETLATISH =================

@router.message(F.text.in_(["🚫 Mijoz chetlatish", "🚫 Mijozni chetlatish"]))
async def start_deactivate_client(message: Message):
    # Bu yerda oddiyroq bo'lishi uchun barcha mijozlarni ro'yxatini chiqaramiz
    clients = await get_all_clients()
    if not clients:
        await message.answer("Hozircha mijozlar yo'q.")
        return
    
    text = "Chetlatish uchun mijozning <b>ID raqamini</b> yozing yoki loginini yuboring:\n\n"
    for c in clients:
        status = "✅ Faol" if c.is_active else "❌ Chetlatilgan"
        text += f"ID: {c.id} | {c.full_name} | Login: {c.login} | {status}\n"
    
    await message.answer(text)

@router.message(F.text.regexp(r'^\d+$')) # Agar faqat raqam yuborsa ID deb qabul qilamiz
async def process_deactivation(message: Message):
    client_id = int(message.text)
    success = await deactivate_client(client_id)
    
    if success:
        await message.answer(f"Mijoz (ID: {client_id}) botdan muvaffaqiyatli chetlatildi.")
    else:

        await message.answer("Bunday ID dagi mijoz topilmadi.")
