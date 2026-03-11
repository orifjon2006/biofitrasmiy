from aiogram import Bot
from aiogram.types import InputMediaVideo
from database import get_client_reports
import logging

logger = logging.getLogger(__name__)

async def send_user_video_archive(bot: Bot, admin_id: int, client_id: int, client_name: str):
    """
    Foydalanuvchining barcha yuborgan videolarini bazadan olib, 
    adminga albom ko'rinishida yuboradi.
    """
    reports = await get_client_reports(client_id)
    
    # Faqat video mavjud bo'lgan hisobotlarni ajratib olamiz
    video_files = [r.video_file_id for r in reports if r.video_file_id]
    
    if not video_files:
        await bot.send_message(admin_id, f" Foydalanuvchi {client_name} hali video yubormagan.")
        return

    await bot.send_message(admin_id, f"🎥 {client_name} ning barcha videolari yuklanmoqda...")

    # Telegram bitta xabarda ko'pi bilan 10 ta video yuborishga ruxsat beradi
    # Shuning uchun videolarni 10 tadan bo'laklarga bo'lamiz
    for i in range(0, len(video_files), 10):
        chunk = video_files[i:i + 10]
        media_group = []
        
        for idx, file_id in enumerate(chunk):
            caption = f"{client_name} - Video {i + idx + 1}" if idx == 0 else ""
            media_group.append(InputMediaVideo(media=file_id, caption=caption))
        
        try:
            await bot.send_media_group(chat_id=admin_id, media=media_group)
        except Exception as e:
            logger.error(f"Videolarni yuborishda xatolik: {e}")
            await bot.send_message(admin_id, "⚠️ Ayrim videolarni yuklashda xatolik yuz berdi.")