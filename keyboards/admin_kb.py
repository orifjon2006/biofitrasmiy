from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def super_admin_main_kb():
    """Katta admin uchun asosiy menyu"""
    kb = [
        [
            KeyboardButton(text="➕ Admin qo'shish"),
            KeyboardButton(text="📋 Adminlar ro'yxati")
        ],
        [
            KeyboardButton(text="👤 Mijoz ro'yxatga olish"),
            KeyboardButton(text="🚫 Mijozni chetlatish")
        ],
        [
            KeyboardButton(text="📩 Xabar yuborish"),
            KeyboardButton(text="🔍 Mijoz haqida ma'lumot")
        ],
        [
            KeyboardButton(text="👥 Umumiy mijozlar ro'yxati")
        ]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=False)

def sub_admin_main_kb():
    """Kichik admin uchun asosiy menyu"""
    kb = [
        [
            KeyboardButton(text="👤 Mijoz qo'shish"),
            KeyboardButton(text="🚫 Mijoz chetlatish")
        ]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def broadcast_options_kb():
    """Xabar yuborish turlari (Inline)"""
    kb = [
        [InlineKeyboardButton(text="📢 Barchaga", callback_data="send_all")],
        [InlineKeyboardButton(text="✅ Kursni boshlaganlarga", callback_data="send_buyers")],
        [InlineKeyboardButton(text="⏳ Hali sotib olmaganlarga", callback_data="send_potentials")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_broadcast")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def course_duration_kb():
    """Mijoz uchun kurs muddati tanlash (Mijoz qo'shish jarayonida)"""
    kb = [
        [
            KeyboardButton(text="1 oylik"),
            KeyboardButton(text="3 oylik")
        ],
        [
            KeyboardButton(text="6 oylik"),
            KeyboardButton(text="12 oylik")
        ],
        [KeyboardButton(text="🚫 Bekor qilish")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def contact_request_kb():
    """Telefon raqamini yuborish tugmasi"""
    kb = [
        [KeyboardButton(text="📞 Telefon raqamini yuborish", request_contact=True)],
        [KeyboardButton(text="🚫 Bekor qilish")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def cancel_kb():
    """Har qanday jarayonni bekor qilish uchun umumiy tugma"""
    kb = [[KeyboardButton(text="🚫 Bekor qilish")]]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def admin_manage_inline(admin_id):
    """Adminlar ro'yxatida har bir admin ostida chiqadigan boshqaruv tugmasi"""
    kb = [
        [InlineKeyboardButton(text="❌ O'chirish", callback_data=f"del_admin_{admin_id}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)