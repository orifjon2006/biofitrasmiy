from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.future import select

# Loyiha modullari
from database import (
    add_admin, get_all_admins, get_all_clients, 
    get_active_clients, get_inactive_clients, async_session, Client, Admin
)
from states.admin_states import AdminAdd, BroadcastState
from keyboards.admin_kb import (
    super_admin_main_kb, broadcast_options_kb, admin_manage_inline
)
from config import generate_credentials, SUPER_ADMIN_ID
from utils.video_handler import send_user_video_archive

router = Router()

# ================= MUKAMMAL FILTR =================
# Bu routerga FAQAT Katta Admin (SUPER_ADMIN_ID) kira oladi.
# Boshqalar yozsa, xabar avtomatik keyingi routerlarga o'tib ketadi.
router.message.filter(F.from_user.id == SUPER_ADMIN_ID)
router.callback_query.filter(F.from_user.id == SUPER_ADMIN_ID)


# ================= ADMINLARNI BOSHQARISH =================

@router.message(F.text == "➕ Admin qo'shish")
async def start_add_admin(message: Message, state: FSMContext):
    await message.answer("Yangi admin uchun Telegram <b>username</b> yozing (masalan: @username):")
    await state.set_state(AdminAdd.waiting_for_username)

@router.message(AdminAdd.waiting_for_username)
async def process_admin_username(message: Message, state: FSMContext):
    username = message.text.replace("@", "")
    
    # 6 talik random login va parol yaratish
    login = generate_credentials(6)
    password = generate_credentials(6)
    
    # Bazaga qo'shish
    await add_admin(username=username, login=login, password=password)
    
    text = (
        f"✅ <b>Yangi admin qo'shildi!</b>\n\n"
        f"👤 Username: @{username}\n"
        f"🔑 Login: <code>{login}</code>\n"
        f"🔐 Parol: <code>{password}</code>\n\n"
        f"<i>Ushbu ma'lumotlarni adminga yetkazing.</i>"
    )
    await message.answer(text, reply_markup=super_admin_main_kb())
    await state.clear()

@router.message(F.text == "📋 Adminlar ro'yxati")
async def list_admins(message: Message):
    admins = await get_all_admins()
    if not admins:
        await message.answer("Hozircha kichik adminlar yo'q.")
        return
    
    for admin in admins:
        await message.answer(
            f"👤 Admin: @{admin.username}\n🔑 Login: <code>{admin.login}</code>",
            reply_markup=admin_manage_inline(admin.id)
        )

# Kichik adminni bazadan o'chirish (Inline tugma orqali)
@router.callback_query(F.data.startswith("del_admin_"))
async def delete_admin_handler(callback: CallbackQuery):
    admin_id = int(callback.data.split("_")[2])
    
    async with async_session() as session:
        result = await session.execute(select(Admin).where(Admin.id == admin_id))
        admin = result.scalars().first()
        
        if admin:
            await session.delete(admin)
            await session.commit()
            await callback.message.edit_text(f"❌ Admin @{admin.username} muvaffaqiyatli o'chirildi.")
        else:
            await callback.message.edit_text("⚠️ Ushbu admin allaqachon o'chirilgan yoki topilmadi.")
    
    await callback.answer()


# ================= MIJOZLAR HISOBOTI =================

@router.message(F.text == "👥 Umumiy mijozlar ro'yxati")
async def list_all_clients(message: Message):
    clients = await get_all_clients()
    if not clients:
        await message.answer("Mijozlar bazasi hozircha bo'sh.")
        return
    
    text = "👥 <b>Barcha mijozlar:</b>\n\n"
    for c in clients:
        status = "🟢" if c.is_active else "🔴"
        text += f"{status} {c.full_name} | Login: <code>{c.login}</code>\n"
    
    # Agar mijozlar juda ko'p bo'lsa, xabar uzunligi chegaradan oshib ketmasligini ta'minlash
    if len(text) > 4000:
        await message.answer(text[:4000] + "...\n<i>(Ro'yxat juda uzun)</i>")
    else:
        await message.answer(text)

@router.message(F.text == "🔍 Mijoz haqida ma'lumot")
async def search_client_prompt(message: Message):
    await message.answer("Ma'lumot olish uchun mijozning <b>6 xonali loginini</b> yuboring:")

@router.message(F.text.len() == 6) # Agar 6 ta belgi kiritilsa, login deb qabul qilamiz
async def get_client_info(message: Message):
    async with async_session() as session:
        result = await session.execute(select(Client).where(Client.login == message.text))
        client = result.scalars().first()
        
        if client:
            status = "✅ Faol" if client.is_active else "❌ Chetlatilgan"
            text = (
                f"👤 <b>Mijoz:</b> {client.full_name}\n"
                f"📍 <b>Manzil:</b> {client.address}\n"
                f"📞 <b>Tel:</b> {client.phone_number}\n"
                f"📅 <b>Muddat:</b> {client.course_months} oy\n"
                f"📊 <b>Holat:</b> {status}\n"
            )
            
            # Mijozning videolarini ko'rish uchun inline tugma ulaymiz
            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🎥 Videolarni ko'rish", callback_data=f"view_videos_{client.id}")]
            ])
            
            await message.answer(text, reply_markup=kb)
        else:
            await message.answer("⚠️ Bunday loginli mijoz topilmadi.")

# Mijoz videolarini ko'rsatish
@router.callback_query(F.data.startswith("view_videos_"))
async def show_client_videos(callback: CallbackQuery, bot: Bot):
    client_id = int(callback.data.split("_")[2])
    
    async with async_session() as session:
        result = await session.execute(select(Client).where(Client.id == client_id))
        client = result.scalars().first()
        
    if client:
        await send_user_video_archive(bot, callback.from_user.id, client_id, client.full_name)
    
    await callback.answer()


# ================= AQLLI XABAR YUBORISH (BROADCAST) =================

@router.message(F.text == "📩 Xabar yuborish")
async def broadcast_menu(message: Message):
    await message.answer(
        "Kimlarga xabar yubormoqchisiz?",
        reply_markup=broadcast_options_kb()
    )

@router.callback_query(F.data.startswith("send_"))
async def start_broadcast(callback: CallbackQuery, state: FSMContext):
    target = callback.data.split("_")[1]
    await state.update_data(target=target)
    
    await callback.message.edit_text(
        "📝 Xabar matnini kiriting.\n<i>(Rasm, video yoki oddiy matn yuborishingiz mumkin)</i>"
    )
    await state.set_state(BroadcastState.waiting_for_message)
    await callback.answer()

@router.callback_query(F.data == "cancel_broadcast")
async def cancel_broadcast_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Xabar yuborish bekor qilindi.")
    await callback.answer()

@router.message(BroadcastState.waiting_for_message)
async def perform_broadcast(message: Message, state: FSMContext):
    data = await state.get_data()
    target = data['target']
    
    # Kategoriya bo'yicha mijozlarni saralash
    if target == "all":
        users = await get_all_clients()
    elif target == "buyers":
        users = await get_active_clients()
    else: # potentials (sotib olmagan yoki muddati tugaganlar)
        users = await get_inactive_clients()

    count = 0
    # Xabarni barchaga nusxalab (copy_to) yuborish
    for user in users:
        if user.telegram_id: # Faqat botga start bosganlarga ketadi
            try:
                await message.copy_to(chat_id=user.telegram_id)
                count += 1
            except Exception:
                continue # Agar user botni bloklagan bo'lsa, xato bermaydi, keyingisiga o'tadi
    
    await message.answer(f"✅ Xabar muvaffaqiyatli {count} ta foydalanuvchiga yuborildi.", reply_markup=super_admin_main_kb())
    await state.clear()
