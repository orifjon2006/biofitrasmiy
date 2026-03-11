from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, BigInteger, Date, Text
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
import datetime

# PostgreSQL uchun: "postgresql+asyncpg://user:password@localhost/dbname"
# Hozircha oson ishga tushirish uchun SQLite dan foydalanamiz, keyin Postgres'ga o'zgartirishingiz mumkin.
DATABASE_URL = "sqlite+aiosqlite:///bot_database.db"

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

# ================= MODELLAR (Jadvallar) =================

class Admin(Base):
    __tablename__ = 'admins'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, nullable=True) # Super admin uchun
    username = Column(String, nullable=True)
    login = Column(String(6), unique=True, nullable=False)
    password = Column(String(6), nullable=False)
    role = Column(String, default="sub_admin") # super_admin yoki sub_admin
    is_active = Column(Boolean, default=True)

class Client(Base):
    __tablename__ = 'clients'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, nullable=True) # User botga kirganda saqlanadi
    full_name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    course_months = Column(Integer, nullable=False) # Necha oylik kurs
    start_date = Column(DateTime, default=datetime.datetime.utcnow)
    end_date = Column(DateTime, nullable=False)
    login = Column(String(6), unique=True, nullable=False)
    password = Column(String(6), nullable=False)
    is_active = Column(Boolean, default=True) # Kurs muddati tugasa False bo'ladi
    
    reports = relationship("DailyReport", back_populates="client")

class DailyReport(Base):
    __tablename__ = 'daily_reports'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    date = Column(Date, default=datetime.date.today)
    consumed_product = Column(Boolean, nullable=False) # Biofit ichdimi yoki yo'q
    video_file_id = Column(String, nullable=True) # Video yuborsa saqlanadi
    skipped_video = Column(Boolean, default=False) # Videoni o'tkazib yubordimi
    
    client = relationship("Client", back_populates="reports")


# ================= BAZA BILAN ISHLOVCHI FUNKSIYALAR =================

async def init_models():
    """Jadvallarni yaratish (Loyiha ishga tushganda bir marta chaqiriladi)"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# --- Admin funksiyalari ---

async def add_admin(username: str, login: str, password: str, role: str = "sub_admin"):
    async with async_session() as session:
        new_admin = Admin(username=username, login=login, password=password, role=role)
        session.add(new_admin)
        await session.commit()
        return new_admin

async def get_admin_by_login(login: str, password: str):
    async with async_session() as session:
        result = await session.execute(select(Admin).where(Admin.login == login, Admin.password == password))
        return result.scalars().first()

async def get_all_admins():
    async with async_session() as session:
        result = await session.execute(select(Admin).where(Admin.role == "sub_admin"))
        return result.scalars().all()

# --- Mijoz funksiyalari ---

async def add_client(full_name: str, address: str, phone: str, months: int, login: str, password: str):
    async with async_session() as session:
        end_date = datetime.datetime.utcnow() + datetime.timedelta(days=30 * months)
        new_client = Client(
            full_name=full_name,
            address=address,
            phone_number=phone,
            course_months=months,
            end_date=end_date,
            login=login,
            password=password
        )
        session.add(new_client)
        await session.commit()
        return new_client

async def authenticate_client(login: str, password: str, telegram_id: int):
    """Mijoz login va parolni kiritganda tekshirish va telegram_id ni ulash"""
    async with async_session() as session:
        result = await session.execute(select(Client).where(Client.login == login, Client.password == password))
        client = result.scalars().first()
        
        if client:
            client.telegram_id = telegram_id
            await session.commit()
            return client
        return None

async def get_client_by_tg_id(telegram_id: int):
    async with async_session() as session:
        result = await session.execute(select(Client).where(Client.telegram_id == telegram_id))
        return result.scalars().first()

async def get_all_clients():
    async with async_session() as session:
        result = await session.execute(select(Client))
        return result.scalars().all()

async def get_active_clients():
    async with async_session() as session:
        result = await session.execute(select(Client).where(Client.is_active == True))
        return result.scalars().all()

async def get_inactive_clients():
    async with async_session() as session:
        result = await session.execute(select(Client).where(Client.is_active == False))
        return result.scalars().all()

async def deactivate_client(client_id: int):
    async with async_session() as session:
        result = await session.execute(select(Client).where(Client.id == client_id))
        client = result.scalars().first()
        if client:
            client.is_active = False
            client.telegram_id = None # Botdan chetlatiladi, lekin ma'lumoti saqlanadi
            await session.commit()
            return True
        return False

# --- Hisobot funksiyalari ---

async def add_daily_report(client_id: int, consumed: bool, video_id: str = None, skipped: bool = False):
    async with async_session() as session:
        report = DailyReport(
            client_id=client_id,
            consumed_product=consumed,
            video_file_id=video_id,
            skipped_video=skipped
        )
        session.add(report)
        await session.commit()
        return report

async def get_client_reports(client_id: int):
    async with async_session() as session:
        result = await session.execute(select(DailyReport).where(DailyReport.client_id == client_id))
        return result.scalars().all()