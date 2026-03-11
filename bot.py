import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Loyihadagi o'z modullarimizni chaqiramiz
from config import BOT_TOKEN
from database import init_models
# Handlerlar (papka ichidagi routerlar)
from handlers import super_admin, sub_admin, client_panel, auth, daily_report
# Taymer funksiyasi
from utils.scheduler import schedule_daily_reports

# Logging sozlamalari (Bot qanday ishlayotganini va xatolarni terminalda ko'rish uchun)
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def on_startup(bot: Bot):
    """Bot ishga tushayotganda bajariladigan amallar."""
    logger.info("Bot ishga tushmoqda...")
    
    # Ma'lumotlar bazasini ishga tushirish (jadvallarni yaratish)
    await init_models()
    logger.info("Ma'lumotlar bazasi muvaffaqiyatli ulandi va tayyor!")

async def on_shutdown(bot: Bot):
    """Bot to'xtatilayotganda bajariladigan amallar."""
    logger.info("Bot to'xtatilmoqda...")

async def main():
    # Bot va Dispatcher obyektlarini yaratamiz. HTML formatlashdan foydalanamiz.
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # Barcha routerlarni (handlerlarni) ro'yxatdan o'tkazamiz
    # Ketma-ketlik muhim emas, lekin tartibli bo'lgani yaxshi
    dp.include_router(auth.router)           # Login va parolni tekshiruvchi qism
    dp.include_router(super_admin.router)    # Katta admin paneli
    dp.include_router(sub_admin.router)      # Kichik admin paneli
    dp.include_router(client_panel.router)   # Mijozlar paneli
    dp.include_router(daily_report.router)   # Kechki so'rovnoma va videolarni qabul qilish

    # Bot ishga tushganda va to'xtaganda bajariladigan amallarni ro'yxatga olamiz
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # APScheduler - Har kuni kechki 8 dagi vazifani vaqt mintaqasi bo'yicha sozlash
    scheduler = AsyncIOScheduler(timezone="Asia/Tashkent")
    # Scheduler'ga bot obyekti bilan kerakli funksiyani ulaymiz
    schedule_daily_reports(scheduler, bot)
    scheduler.start()

    # Botni ishga tushirish (Drop pending updates - bot o'chiq paytida kelgan eski xabarlarni ignor qilish)
    await bot.delete_webhook(drop_pending_updates=True)
    try:
        logger.info("Polling boshlandi...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Kutilmagan xatolik yuz berdi: {e}")
    finally:
        # Bot to'xtaganda sessiyani yopish
        await bot.session.close()
        logger.info("Bot sessiyasi yopildi.")

if __name__ == '__main__':
    try:
        # Asinxron main funksiyasini ishga tushiramiz
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot dasturchi tomonidan to'xtatildi (Ctrl+C).")