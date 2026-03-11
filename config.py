import os
import random
import string
from dotenv import load_dotenv

# .env faylidagi o'zgaruvchilarni yuklash
load_dotenv()

# Bot sozlamalari
BOT_TOKEN = os.getenv("BOT_TOKEN")
SUPER_ADMIN_ID = int(os.getenv("SUPER_ADMIN_ID")) # Katta adminning telegram ID si

# Ma'lumotlar bazasi manzili
# Agar SQLite ishlatsangiz shunday qoladi, PostgreSQL bo'lsa o'zgartiriladi
DATABASE_URL = "sqlite+aiosqlite:///bot_database.db"

# Maxsus funksiya: 6 talik random login va parol yaratish
def generate_credentials(length=6):
    """
    6 talik tasodifiy harf va raqamlardan iborat login/parol yaratadi.
    Misol: 'A7B2X9'
    """
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

# Mashqlar ro'yxati (Buni keyinchalik bazaga ham o'tkazish mumkin)
EXERCISES = [
    {"id": 1, "name": "Ertalabki badantarbiya", "video": "VIDEO_ID_1"},
    {"id": 2, "name": "Qorin mushaklari uchun", "video": "VIDEO_ID_2"},
    {"id": 3, "name": "Oyoq mashqlari", "video": "VIDEO_ID_3"}
]

# Motivatsion gaplar (Biofit iste'mol qilinganda yuboriladi)
MOTIVATION_QUOTES = [
    "Barakalla! Sog'lom hayot sari yana bir qadam tashladingiz. 💪",
    "Ajoyib! Intizom — muvaffaqiyat kalitidir. ✨",
    "Siz o'z ustingizda ishlashdan to'xtamang, natija albatta bo'ladi! 🔥",
    "Biofit bilan siz yanada kuchlisiz! Davom eting. 🚀"
]