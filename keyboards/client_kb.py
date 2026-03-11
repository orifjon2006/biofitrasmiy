from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def main_client_kb():
    """Mijozning asosiy menyusi"""
    kb = [
        [KeyboardButton(text="🏋️ Mashqlar ro'yxati")],
        [KeyboardButton(text="🤖 Yordamchini aktivlashtirish")],
        [KeyboardButton(text="📈 Natijamni ko'rish")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def biofit_query_kb():
    """Ha/Yo'q savoli uchun inline tugmalar"""
    kb = [
        [
            InlineKeyboardButton(text="Ha ✅", callback_data="biofit_yes"),
            InlineKeyboardButton(text="Qabul qilmadim ❌", callback_data="biofit_no")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def skip_video_kb():
    """Video yuborishni o'tkazib yuborish tugmasi"""
    kb = [[InlineKeyboardButton(text="O'tkazib yuborish ⏭", callback_data="skip_video")]]
    return InlineKeyboardMarkup(inline_keyboard=kb)