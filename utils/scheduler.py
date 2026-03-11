from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database import get_active_clients, deactivate_client, async_session, Client
from sqlalchemy.future import select
import datetime
from keyboards.client_kb import biofit_query_kb
import logging

logger = logging.getLogger(__name__)

async def check_course_expiration(bot: Bot):
    """Muddati tugagan mijozlarni tekshirish va o'chirish"""
    async with async_session() as session:
        now = datetime.datetime.utcnow()
        # Muddati o'tgan va hali faol bo'lgan mijozlarni topish
        result = await session.execute(
            select(Client).where(Client.end_date <= now, Client.is_active == True)
        )
        expired_clients = result.scalars().all()

        for client in expired_clients:
            await deactivate_client(client.id)
            if client.telegram_id:
                try:
                    await bot.send_message(
                        client.telegram_id, 
                        "⚠️ <b>Sizning kurs muddatingiz tugadi.</b>\nMa'lumotlaringiz saqlanib qoldi, davom etish uchun adminga murojaat qiling."
                    )
                except Exception as e:
                    logger.error(f"Xabar yuborib bo'lmadi {client.telegram_id}: {e}")

async def send_daily_8pm_question(bot: Bot):
    """Har kuni soat 20:00 da so'rovnoma yuborish"""
    active_clients = await get_active_clients()
    
    for client in active_clients:
        if client.telegram_id:
            try:
                await bot.send_message(
                    client.telegram_id,
                    "Bugun <b>Biofit</b> mahsulotini iste'mol qildingizmi? ✅❌",
                    reply_markup=biofit_query_kb()
                )
            except Exception as e:
                logger.error(f"So'rovnoma yuborilmadi {client.telegram_id}: {e}")

def schedule_daily_reports(scheduler: AsyncIOScheduler, bot: Bot):
    # Har kuni soat 20:00 da ishga tushadi
    scheduler.add_job(
        send_daily_8pm_question, 
        "cron", 
        hour=20, 
        minute=0, 
        args=[bot]
    )
    # Har soatda kurs muddatini tekshirib turadi
    scheduler.add_job(
        check_course_expiration, 
        "interval", 
        hours=1, 
        args=[bot]
    )